import pandas as pd

from config.constants import (
    IDENTIFIER_KEYWORDS,
    IDENTIFIER_NAME_SCORE,
    IDENTIFIER_UNIQUE_SCORE,
    IDENTIFIER_STRING_SCORE,
    IDENTIFIER_SCORE_THRESHOLD,
)

# Fraction of non-null sample values that must parse as dates.
_DATETIME_PARSE_THRESHOLD = 0.85
_DATETIME_SAMPLE_SIZE = 100


def _looks_like_datetime(series: pd.Series) -> bool:
    """
    Detect datetime-like string/object columns without requiring a
    native datetime64 dtype (CSV loads usually keep dates as strings).
    Uses coerce + a success-rate threshold so mixed garbage does not
    raise, and random columns of IDs/names are not misclassified.
    """
    non_null = series.dropna()
    if len(non_null) == 0:
        return False

    sample = non_null
    if len(non_null) > _DATETIME_SAMPLE_SIZE:
        sample = non_null.sample(_DATETIME_SAMPLE_SIZE, random_state=42)

    try:
        converted = pd.to_datetime(
            sample.astype(str),
            errors="coerce",
            format="mixed",
        )
    except (TypeError, ValueError, OverflowError):
        try:
            converted = pd.to_datetime(sample.astype(str), errors="coerce")
        except Exception:
            return False

    success_ratio = float(converted.notna().mean())
    return success_ratio >= _DATETIME_PARSE_THRESHOLD


def detect_column_type(series: pd.Series):

    """
    Detect the semantic type of a column.
    """

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # String / object columns may hold parseable dates (e.g. Order Date).
    if (
        pd.api.types.is_string_dtype(series)
        or pd.api.types.is_object_dtype(series)
    ):
        if _looks_like_datetime(series):
            return "datetime"

        avg_length = (
            series
            .dropna()
            .astype(str)
            .str.len()
            .mean()
        )

        if avg_length > 50:
            return "text"

        return "categorical"

    return "unknown"

def missing_ratio(series):

    return series.isnull().mean()

def unique_ratio(series):

    return (
        series.nunique(dropna=True)
        /
        len(series)
    )

def has_outliers(series):

    if not pd.api.types.is_numeric_dtype(series):

        return False

    q1 = series.quantile(0.25)

    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    return bool(
    (
        (series < lower)
        |
        (series > upper)
    ).any()
)
def is_identifier(
    column_name,
    series
):

    score = 0

    normalized = (
        column_name
        .lower()
        .replace("_", "")
        .replace(" ", "")
    )

    for keyword in IDENTIFIER_KEYWORDS:

        if keyword in normalized:

            score += IDENTIFIER_NAME_SCORE

            break

    
    ratio = unique_ratio(series)

    if ratio >= 0.95:

        score += IDENTIFIER_UNIQUE_SCORE

   
    if (
        detect_column_type(series)
        == "categorical"
        and ratio >= 0.90
    ):

        score += IDENTIFIER_STRING_SCORE

    return score >= IDENTIFIER_SCORE_THRESHOLD


def is_constant(series):

    return series.nunique(dropna=True) <= 1

def column_memory(series):

    return int(
        series.memory_usage(deep=True)
    )

