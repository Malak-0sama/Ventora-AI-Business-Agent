"""
storage/base_store.py
======================

Defines the abstract contract for the Artifact Store persistence layer
used across the AI Business Intelligence Platform pipeline.

Design Rationale
-----------------
Every stage of the pipeline (Schema Agent, Planner Agent, LLM Planner
Reviewer, Preprocessing Agent, Model Agent, Report Agent, ...) produces
artifacts that must outlive the Python process that created them:
schemas, execution plans, processed datasets, trained models,
evaluation metrics, and LLM-generated text (summaries, explanations,
recommendations, prompts).

Rather than letting each agent read/write files directly (which would
scatter storage concerns across the codebase and make swapping storage
backends - local disk, S3, Azure Blob, GCS, PostgreSQL - a large,
error-prone refactor), all persistence is funneled through a single
abstraction: ``ArtifactStore``.

This follows the Strategy Pattern (mirroring ``llm/provider.py`` in
this codebase): callers depend only on the abstract contract defined
here, never on a concrete backend. Concrete backends (see
``storage/local_store.py`` and future ``storage/s3_store.py``, etc.)
implement this contract without requiring any change to calling code.

Every persisted artifact is automatically wrapped with an
``ArtifactMetadata`` record, giving the platform first-class support
for auditing, versioning, and integrity verification -- all of which
are prerequisites for an enterprise-grade, multi-tenant SaaS product.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import pandas as pd


__all__ = [
    "ArtifactType",
    "ArtifactMetadata",
    "ArtifactStore",
    "ArtifactStoreError",
    "ArtifactNotFoundError",
    "ArtifactIntegrityError",
    "ArtifactWriteError",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ArtifactStoreError(Exception):
    """
    Base exception for all Artifact Store failures.

    Every exception raised by any ``ArtifactStore`` implementation
    (local filesystem, S3, Azure Blob, GCS, PostgreSQL, ...) MUST
    inherit from this class. This allows calling code to catch a
    single exception type when it does not need to distinguish
    between failure modes, e.g.:

        try:
            store.save_json(...)
        except ArtifactStoreError:
            logger.exception("Failed to persist artifact")
    """


class ArtifactNotFoundError(ArtifactStoreError):
    """
    Raised when an operation references an artifact that does not
    exist in the store.

    Raised by: ``load_json``, ``load_dataframe``, ``load_model``,
    ``load_metrics``, ``get_metadata``, and ``delete`` (when the
    target artifact is missing).
    """

    def __init__(self, run_id: str, artifact_name: str) -> None:
        self.run_id = run_id
        self.artifact_name = artifact_name
        super().__init__(
            f"Artifact '{artifact_name}' not found for run_id="
            f"'{run_id}'."
        )


class ArtifactIntegrityError(ArtifactStoreError):
    """
    Raised when the checksum recorded in an artifact's metadata does
    not match the checksum computed from the artifact's content at
    read time.

    This indicates the underlying storage was modified outside of the
    ``ArtifactStore`` API (manual edit, disk corruption, partial
    write, tampering) and the artifact can no longer be trusted.

    Raised by: ``load_json``, ``load_dataframe``, ``load_model``,
    ``load_metrics``.
    """

    def __init__(
        self,
        run_id: str,
        artifact_name: str,
        expected_checksum: str,
        actual_checksum: str,
    ) -> None:
        self.run_id = run_id
        self.artifact_name = artifact_name
        self.expected_checksum = expected_checksum
        self.actual_checksum = actual_checksum
        super().__init__(
            f"Checksum mismatch for artifact '{artifact_name}' "
            f"(run_id='{run_id}'). Expected "
            f"'{expected_checksum}', got '{actual_checksum}'. "
            "The artifact may be corrupted or was modified outside "
            "of the ArtifactStore API."
        )


class ArtifactWriteError(ArtifactStoreError):
    """
    Raised when an artifact cannot be persisted to the backing store.

    Wraps lower-level failures such as disk-full conditions,
    permission errors, network failures against a cloud backend, or
    serialization failures, so that callers only need to handle a
    single, stable exception type regardless of the active backend.

    Raised by: ``save_json``, ``save_dataframe``, ``save_model``,
    ``save_metrics``.
    """

    def __init__(self, run_id: str, artifact_name: str, reason: str) -> None:
        self.run_id = run_id
        self.artifact_name = artifact_name
        self.reason = reason
        super().__init__(
            f"Failed to write artifact '{artifact_name}' for "
            f"run_id='{run_id}': {reason}"
        )


# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------


class ArtifactType(str, Enum):
    """
    Enumerates the categories of artifacts the platform persists.

    Kept as a ``str`` subclass so values serialize cleanly to JSON
    (``json.dumps`` will emit the plain string value) and can be
    compared directly against string literals in tests and queries.
    """

    JSON = "json"
    DATAFRAME = "dataframe"
    MODEL = "model"
    METRICS = "metrics"
    TEXT = "text"


@dataclass(frozen=True)
class ArtifactMetadata:
    """
    Immutable metadata record automatically generated and stored
    alongside every artifact persisted through an ``ArtifactStore``.

    This record is the foundation for auditing (who produced what,
    when), versioning (how many times has this artifact been
    overwritten), and integrity verification (has the content changed
    since it was written).

    Attributes:
        artifact_name: Logical, run-scoped unique name for the
            artifact (e.g. ``"schema"``, ``"plan"``,
            ``"processed_dataset"``, ``"model_LightGBM"``).
        artifact_type: The category of the artifact. See
            ``ArtifactType``.
        run_id: Identifier of the pipeline run that owns this
            artifact. All artifacts for a single dataset run share
            the same ``run_id``.
        stage: The pipeline stage that produced the artifact (e.g.
            ``"schema_agent"``, ``"llm_planner_agent"``,
            ``"model_agent"``). Distinct from ``producer_agent`` to
            allow a single agent to tag artifacts under different
            logical stages if needed; in practice these are often
            equal.
        created_at: UTC timestamp of when this artifact version was
            written.
        version: 1-based version number. Incremented automatically
            each time an artifact with the same ``artifact_name`` is
            saved again under the same ``run_id``, enabling full
            history retention rather than silent overwrites.
        checksum: SHA-256 hex digest computed over the serialized
            artifact content, used to detect corruption or tampering
            on read.
        file_size_bytes: Size, in bytes, of the serialized artifact
            content.
        producer_agent: Name of the agent/class that produced the
            artifact (e.g. ``"SchemaAgent"``, ``"ModelTrainer"``).
            Used for auditing and for tracing an artifact back to the
            code that generated it.
        content_type: MIME-like descriptor of the serialization
            format (e.g. ``"application/json"``,
            ``"application/vnd.apache.parquet"``,
            ``"application/octet-stream"``). Useful for future HTTP-
            based backends (e.g. serving artifacts via a REST API).
        artifact_id: Globally unique identifier (UUID4) minted for
            this specific artifact *version*. Unlike
            ``artifact_name`` (a stable, human-readable, run-scoped
            key that stays the same across versions), ``artifact_id``
            uniquely identifies this exact version across the entire
            platform -- including across different runs and
            different artifact names. This is what a future REST API
            would expose as the addressable resource id (e.g.
            ``GET /artifacts/{artifact_id}``), and what an experiment
            tracker would use as a foreign key when comparing model
            versions across runs.
        tags: Optional free-form key/value labels attached at save
            time (e.g. ``{"experiment": "q3-pricing-model",
            "environment": "staging"}``). Enables filtering and
            grouping artifacts across runs without changing the
            storage schema -- the foundation for future experiment
            tracking. Defaults to an empty dict.
        extra_metadata: Optional free-form dictionary reserved for
            forward compatibility. New metadata needs discovered
            later (e.g. data-lineage hashes, compute environment
            fingerprints, cost tracking) can be attached here without
            requiring an interface change or a migration of every
            existing ``ArtifactStore`` implementation. Defaults to an
            empty dict. Treat this as an escape hatch, not a
            replacement for promoting a field to first-class status
            once it proves broadly useful.
    """

    artifact_name: str
    artifact_type: ArtifactType
    run_id: str
    stage: str
    created_at: datetime
    version: int
    checksum: str
    file_size_bytes: int
    producer_agent: str
    content_type: str = field(default="application/octet-stream")
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: dict[str, Any] = field(default_factory=dict)
    extra_metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract contract
# ---------------------------------------------------------------------------


class ArtifactStore(ABC):
    """
    Abstract contract for persisting and retrieving pipeline
    artifacts.

    Every method is scoped by ``run_id`` (which pipeline execution
    the artifact belongs to) and ``artifact_name`` (a logical, unique
    name within that run, e.g. ``"schema"``, ``"plan"``,
    ``"processed_dataset"``, ``"model_LightGBM"``,
    ``"evaluation_results"``). Implementations translate this
    ``(run_id, artifact_name)`` pair into whatever addressing scheme
    their backend uses (a file path, an S3 object key, a blob name,
    a database row) -- callers never need to know or care.

    Concrete implementations MUST:

    1. Compute a SHA-256 ``checksum`` over the serialized artifact
       content on every ``save_*`` call.
    2. Auto-increment ``version`` when an artifact with the same
       ``artifact_name`` is saved again under the same ``run_id``.
    3. Verify the stored ``checksum`` against freshly computed
       content on every ``load_*`` call and raise
       ``ArtifactIntegrityError`` on mismatch.
    4. Raise ``ArtifactNotFoundError`` (never return ``None`` or raise
       a generic/backend-specific exception) when a requested
       artifact does not exist.
    5. Raise ``ArtifactWriteError`` (never let backend-specific
       exceptions propagate) when a write fails.

    This uniform error contract is what allows calling code -- and
    unit tests -- to depend only on this module's exception types,
    regardless of which concrete backend is configured.
    """

    # ------------------------------------------------------------------
    # JSON artifacts (schema, plan, evaluation summaries, insights, ...)
    # ------------------------------------------------------------------

    @abstractmethod
    def save_json(
        self,
        run_id: str,
        stage: str,
        artifact_name: str,
        data: dict[str, Any],
        producer_agent: str,
        tags: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ArtifactMetadata:
        """
        Persist a JSON-serializable dictionary as an artifact.

        Args:
            run_id: Identifier of the pipeline run.
            stage: Pipeline stage producing this artifact (e.g.
                ``"schema_agent"``).
            artifact_name: Logical, run-scoped unique artifact name
                (e.g. ``"schema"``, ``"plan"``).
            data: JSON-serializable dictionary to persist.
            producer_agent: Name of the agent/class producing the
                artifact.
            tags: Optional free-form labels to attach to this
                artifact version (see ``ArtifactMetadata.tags``).
            extra_metadata: Optional forward-compatible metadata to
                attach to this artifact version (see
                ``ArtifactMetadata.extra_metadata``).

        Returns:
            Metadata describing the newly written artifact version.

        Raises:
            ArtifactWriteError: If serialization or the underlying
                write operation fails.
        """
        raise NotImplementedError

    @abstractmethod
    def load_json(self, run_id: str, artifact_name: str) -> dict[str, Any]:
        """
        Load the latest version of a JSON artifact.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to load.

        Returns:
            The deserialized dictionary.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
            ArtifactIntegrityError: If the stored checksum does not
                match the content read from the backend.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Tabular data artifacts (processed datasets, feature matrices, ...)
    # ------------------------------------------------------------------

    @abstractmethod
    def save_dataframe(
        self,
        run_id: str,
        stage: str,
        artifact_name: str,
        df: pd.DataFrame,
        producer_agent: str,
        tags: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ArtifactMetadata:
        """
        Persist a pandas DataFrame as an artifact.

        Implementations should use a columnar, type-preserving format
        (e.g. Parquet) rather than CSV, so that dtypes (datetimes,
        numeric precision, categoricals) survive the round trip.

        Args:
            run_id: Identifier of the pipeline run.
            stage: Pipeline stage producing this artifact.
            artifact_name: Logical, run-scoped unique artifact name
                (e.g. ``"processed_dataset"``).
            df: The DataFrame to persist.
            producer_agent: Name of the agent/class producing the
                artifact.
            tags: Optional free-form labels to attach to this
                artifact version (see ``ArtifactMetadata.tags``).
            extra_metadata: Optional forward-compatible metadata to
                attach to this artifact version (see
                ``ArtifactMetadata.extra_metadata``).

        Returns:
            Metadata describing the newly written artifact version.

        Raises:
            ArtifactWriteError: If serialization or the underlying
                write operation fails.
        """
        raise NotImplementedError

    @abstractmethod
    def load_dataframe(self, run_id: str, artifact_name: str) -> pd.DataFrame:
        """
        Load the latest version of a DataFrame artifact.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to load.

        Returns:
            The deserialized DataFrame.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
            ArtifactIntegrityError: If the stored checksum does not
                match the content read from the backend.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Trained model artifacts
    # ------------------------------------------------------------------

    @abstractmethod
    def save_model(
        self,
        run_id: str,
        stage: str,
        artifact_name: str,
        model: Any,
        producer_agent: str,
        tags: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ArtifactMetadata:
        """
        Persist a trained model object as an artifact.

        Implementations should use a serialization format suited to
        the numeric arrays typically embedded in fitted scikit-learn-
        compatible estimators (e.g. ``joblib``), rather than the
        stdlib ``pickle`` module directly.

        Args:
            run_id: Identifier of the pipeline run.
            stage: Pipeline stage producing this artifact (e.g.
                ``"model_agent"``).
            artifact_name: Logical, run-scoped unique artifact name
                (e.g. ``"model_LightGBM"``).
            model: The fitted model/estimator object to persist.
            producer_agent: Name of the agent/class producing the
                artifact.
            tags: Optional free-form labels to attach to this
                artifact version (see ``ArtifactMetadata.tags``).
                For models, commonly used for hyperparameter
                summaries or experiment names.
            extra_metadata: Optional forward-compatible metadata to
                attach to this artifact version (see
                ``ArtifactMetadata.extra_metadata``).

        Returns:
            Metadata describing the newly written artifact version.

        Raises:
            ArtifactWriteError: If serialization or the underlying
                write operation fails.
        """
        raise NotImplementedError

    @abstractmethod
    def load_model(self, run_id: str, artifact_name: str) -> Any:
        """
        Load the latest version of a model artifact.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to load.

        Returns:
            The deserialized model/estimator object.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
            ArtifactIntegrityError: If the stored checksum does not
                match the content read from the backend.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Metrics artifacts (first-class: consumed by Report Agent/Dashboard)
    # ------------------------------------------------------------------

    @abstractmethod
    def save_metrics(
        self,
        run_id: str,
        stage: str,
        artifact_name: str,
        metrics: dict[str, Any],
        producer_agent: str,
        tags: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ArtifactMetadata:
        """
        Persist a metrics dictionary as a first-class artifact.

        Kept distinct from ``save_json`` (even though the underlying
        serialization is JSON) so that metrics can be queried,
        versioned, and typed independently of generic JSON blobs --
        e.g. ``list_artifacts(run_id, artifact_type=ArtifactType.METRICS)``
        lets the Report Agent and Dashboard retrieve exactly the
        evaluation results they need without scanning unrelated JSON
        artifacts such as the schema or plan.

        Args:
            run_id: Identifier of the pipeline run.
            stage: Pipeline stage producing this artifact (e.g.
                ``"model_agent"``).
            artifact_name: Logical, run-scoped unique artifact name
                (e.g. ``"evaluation_results"``).
            metrics: Dictionary of metric names to values (numeric,
                nested dicts/lists such as confusion matrices, etc.).
            producer_agent: Name of the agent/class producing the
                artifact.
            tags: Optional free-form labels to attach to this
                artifact version (see ``ArtifactMetadata.tags``).
            extra_metadata: Optional forward-compatible metadata to
                attach to this artifact version (see
                ``ArtifactMetadata.extra_metadata``).

        Returns:
            Metadata describing the newly written artifact version.

        Raises:
            ArtifactWriteError: If serialization or the underlying
                write operation fails.
        """
        raise NotImplementedError

    @abstractmethod
    def load_metrics(self, run_id: str, artifact_name: str) -> dict[str, Any]:
        """
        Load the latest version of a metrics artifact.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to load.

        Returns:
            The deserialized metrics dictionary.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
            ArtifactIntegrityError: If the stored checksum does not
                match the content read from the backend.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Text artifacts (LLM-generated summaries, explanations, prompts,
    # narrative recommendations, ...)
    # ------------------------------------------------------------------

    @abstractmethod
    def save_text(
        self,
        run_id: str,
        stage: str,
        artifact_name: str,
        text: str,
        producer_agent: str,
        tags: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> ArtifactMetadata:
        """
        Persist a plain-text artifact.

        Kept distinct from ``save_json`` because free-form text --
        LLM-generated narrative summaries, natural-language
        explanations of model behavior, the exact prompt sent to an
        LLM provider, or business recommendations produced by the
        Report Agent -- is not structured data and should not be
        forced into a JSON envelope just to be persisted. Storing it
        as first-class text also keeps it human-readable directly
        from the backing store (e.g. opening the file in a text
        editor, or rendering it verbatim in a dashboard) without a
        JSON-parsing step.

        Args:
            run_id: Identifier of the pipeline run.
            stage: Pipeline stage producing this artifact (e.g.
                ``"report_agent"``).
            artifact_name: Logical, run-scoped unique artifact name
                (e.g. ``"executive_summary"``,
                ``"planner_prompt"``).
            text: The raw text content to persist.
            producer_agent: Name of the agent/class producing the
                artifact.
            tags: Optional free-form labels to attach to this
                artifact version (see ``ArtifactMetadata.tags``).
            extra_metadata: Optional forward-compatible metadata to
                attach to this artifact version (see
                ``ArtifactMetadata.extra_metadata``). Commonly used
                here to record the generating LLM's model name and
                token usage.

        Returns:
            Metadata describing the newly written artifact version.

        Raises:
            ArtifactWriteError: If the underlying write operation
                fails.
        """
        raise NotImplementedError

    @abstractmethod
    def load_text(self, run_id: str, artifact_name: str) -> str:
        """
        Load the latest version of a text artifact.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to load.

        Returns:
            The raw text content.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
            ArtifactIntegrityError: If the stored checksum does not
                match the content read from the backend.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Generic management operations
    # ------------------------------------------------------------------

    @abstractmethod
    def exists(self, run_id: str, artifact_name: str) -> bool:
        """
        Check whether an artifact exists for the given run.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to check.

        Returns:
            ``True`` if at least one version of the artifact exists,
            ``False`` otherwise. This method never raises
            ``ArtifactNotFoundError``.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, run_id: str, artifact_name: str) -> bool:
        """
        Delete an artifact (all versions) for the given run.

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to delete.

        Returns:
            ``True`` if the artifact existed and was deleted.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
        """
        raise NotImplementedError

    @abstractmethod
    def list_artifacts(
        self,
        run_id: str,
        stage: Optional[str] = None,
        artifact_type: Optional[ArtifactType] = None,
    ) -> list[ArtifactMetadata]:
        """
        List metadata for all artifacts belonging to a run, optionally
        filtered by stage and/or artifact type.

        Args:
            run_id: Identifier of the pipeline run.
            stage: If provided, only return artifacts produced at
                this pipeline stage.
            artifact_type: If provided, only return artifacts of this
                type (e.g. only ``ArtifactType.METRICS`` for a
                dashboard summary view).

        Returns:
            A list of ``ArtifactMetadata`` for the latest version of
            each matching artifact, ordered by ``created_at``
            ascending. Returns an empty list if the run has no
            matching artifacts (this is not an error condition).
        """
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self, run_id: str, artifact_name: str) -> ArtifactMetadata:
        """
        Retrieve metadata for the latest version of an artifact
        without loading its content.

        Useful for audit trails, integrity checks, and dashboard
        views that need to display artifact provenance (who produced
        it, when, which version) without paying the cost of
        deserializing potentially large content (e.g. a full
        DataFrame or model).

        Args:
            run_id: Identifier of the pipeline run.
            artifact_name: Logical artifact name to inspect.

        Returns:
            The metadata record for the latest version.

        Raises:
            ArtifactNotFoundError: If no artifact with this name
                exists for the given run.
        """
        raise NotImplementedError