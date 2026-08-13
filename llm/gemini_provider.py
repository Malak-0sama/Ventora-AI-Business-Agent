import logging
import time

from google import genai
from google.genai import errors as genai_errors

from config.llm_config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 5
_BASE_DELAY_SECONDS = 1.0
_MAX_DELAY_SECONDS = 60.0


def _is_retryable_error(exc: BaseException) -> bool:
    """Return True for rate-limit (429) and unavailable/server (5xx) errors."""
    if isinstance(exc, genai_errors.APIError):
        code = getattr(exc, "code", None)
        if code in _RETRYABLE_STATUS_CODES:
            return True
        status = (getattr(exc, "status", None) or "").upper()
        if status in {
            "RESOURCE_EXHAUSTED",
            "UNAVAILABLE",
            "INTERNAL",
            "DEADLINE_EXCEEDED",
            "ABORTED",
        }:
            return True

    message = str(exc).upper()
    markers = (
        "429",
        "503",
        "500",
        "502",
        "504",
        "RESOURCE_EXHAUSTED",
        "UNAVAILABLE",
        "RATE LIMIT",
        "TOO MANY REQUESTS",
        "OVERLOADED",
    )
    return any(marker in message for marker in markers)


def _extract_retry_delay_seconds(exc: BaseException) -> float | None:
    """Parse server-suggested retry delay from Gemini error details, if any."""
    details = getattr(exc, "details", None)
    if not isinstance(details, dict):
        return None

    candidates: list = []
    if isinstance(details.get("details"), list):
        candidates.extend(details["details"])
    error_obj = details.get("error")
    if isinstance(error_obj, dict) and isinstance(error_obj.get("details"), list):
        candidates.extend(error_obj["details"])

    for item in candidates:
        if not isinstance(item, dict):
            continue
        if item.get("@type", "").endswith("RetryInfo"):
            raw = item.get("retryDelay") or item.get("retry_delay")
            if isinstance(raw, str) and raw.endswith("s"):
                try:
                    return float(raw.rstrip("s"))
                except ValueError:
                    continue
            if isinstance(raw, (int, float)):
                return float(raw)
    return None


class GeminiProvider:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate(self, prompt: str) -> str:
        """
        Call Gemini with exponential backoff on 429 / 503 (and related
        transient) errors. Non-retryable errors are raised immediately.
        Honors server-provided RetryInfo delay when present.
        """
        last_error: BaseException | None = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                )
                text = getattr(response, "text", None)
                if text is None:
                    raise ValueError("Gemini returned an empty response.")
                return text

            except Exception as exc:  
                last_error = exc
                if not _is_retryable_error(exc) or attempt >= _MAX_ATTEMPTS:
                    raise

                suggested = _extract_retry_delay_seconds(exc)
                backoff = _BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                delay = min(max(suggested or backoff, backoff), _MAX_DELAY_SECONDS)

                logger.warning(
                    "Gemini API transient error (attempt %s/%s): %s. "
                    "Retrying in %.1fs...",
                    attempt,
                    _MAX_ATTEMPTS,
                    exc,
                    delay,
                )
                print(
                    f"[GeminiProvider] Transient error on attempt "
                    f"{attempt}/{_MAX_ATTEMPTS}: {exc}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

        raise RuntimeError(
            f"Gemini API failed after {_MAX_ATTEMPTS} attempts: {last_error}"
        )
