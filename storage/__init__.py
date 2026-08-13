"""
storage
=======

Persistence layer for the AI Business Intelligence Platform.

Exposes the ``ArtifactStore`` abstract contract, its supporting types
(``ArtifactType``, ``ArtifactMetadata``), and the exception hierarchy
used across all concrete storage backends (local filesystem, and,
eventually, S3 / Azure Blob / GCS / PostgreSQL).

Concrete backends are intentionally NOT imported here to avoid forcing
optional dependencies (e.g. ``boto3`` for S3) onto every consumer of
this package. Import concrete implementations directly, e.g.:

    from storage.local_store import LocalFileArtifactStore
"""

from storage.base_store import (
    ArtifactIntegrityError,
    ArtifactMetadata,
    ArtifactNotFoundError,
    ArtifactStore,
    ArtifactStoreError,
    ArtifactType,
    ArtifactWriteError,
)

__all__ = [
    "ArtifactStore",
    "ArtifactType",
    "ArtifactMetadata",
    "ArtifactStoreError",
    "ArtifactNotFoundError",
    "ArtifactIntegrityError",
    "ArtifactWriteError",
]