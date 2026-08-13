"""
Project Constants
-----------------
All project-wide constants are stored here.
"""

IDENTIFIER_KEYWORDS = {
    "id",
    "identifier",
    "uuid",
    "guid",
    "key",
    "code",
    "serial",
    "number"
}

IDENTIFIER_SCORE_THRESHOLD = 8

IDENTIFIER_NAME_SCORE = 5
IDENTIFIER_UNIQUE_SCORE = 5
IDENTIFIER_STRING_SCORE = 3



LOW_MISSING_THRESHOLD = 0.05

MEDIUM_MISSING_THRESHOLD = 0.30

HIGH_MISSING_THRESHOLD = 0.60



NORMAL_DISTRIBUTION_THRESHOLD = 0.5


SMALL_DATASET_ROWS = 1000

MEDIUM_DATASET_ROWS = 10000

LARGE_DATASET_ROWS = 100000