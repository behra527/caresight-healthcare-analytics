from __future__ import annotations

import pandas as pd

from src.schema import (
    NUMERIC_CANONICAL_FIELDS,
    REQUIRED_CANONICAL_COLUMNS,
)


# ============================================================
# Validation Configuration
# ============================================================

NUMERIC_COLUMNS = sorted(
    NUMERIC_CANONICAL_FIELDS
)


TEXT_COLUMNS = [
    "patient_id",
    "patient_name",
    "gender",
    "blood_group",
    "diabetes",
    "hypertension",
    "heart_disease",
    "asthma",
    "kidney_disease",
    "smoking_status",
    "visit_type",
    "department",
    "diagnosis",
    "risk_level",
    "medication",
    "allergies",
]


VALID_RISK_LEVELS = {
    "Low",
    "Medium",
    "High",
}


# ============================================================
# Column Validation
# ============================================================

def validate_columns(
    df: pd.DataFrame,
) -> tuple[bool, list[str]]:
    """
    Validate the required canonical healthcare fields.

    The dashboard is patient-centric, therefore patient_id
    is required.

    Optional healthcare fields are allowed to be missing.
    Unknown/additional columns are also allowed.
    """

    if df is None:
        return False, sorted(
            REQUIRED_CANONICAL_COLUMNS
        )

    if df.empty:
        return False, sorted(
            REQUIRED_CANONICAL_COLUMNS
        )

    present_columns = {
        str(column)
        for column in df.columns
    }

    missing_columns = sorted(
        REQUIRED_CANONICAL_COLUMNS
        - present_columns
    )

    if missing_columns:
        return False, missing_columns

    return True, []


# ============================================================
# Data Normalization
# ============================================================

def normalize_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize recognized healthcare fields that are present.

    Rules
    -----
    - Text values are stripped.
    - Risk levels are standardized.
    - Visit dates are converted to datetime.
    - Numeric healthcare fields are converted to numeric.
    - Missing optional fields are skipped.
    - Unknown columns are preserved.

    No values are fabricated.
    """

    if df is None:
        return pd.DataFrame()

    normalized_df = df.copy()

    # --------------------------------------------------------
    # Text fields
    # --------------------------------------------------------

    for column in TEXT_COLUMNS:

        if column not in normalized_df.columns:
            continue

        normalized_df[column] = (
            normalized_df[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if "risk_level" in normalized_df.columns:

        normalized_df["risk_level"] = (
            normalized_df["risk_level"]
            .astype("string")
            .str.strip()
            .str.title()
        )

    # --------------------------------------------------------
    # Visit date
    # --------------------------------------------------------

    if "visit_date" in normalized_df.columns:

        try:
            normalized_df["visit_date"] = (
                pd.to_datetime(
                    normalized_df["visit_date"],
                    errors="coerce",
                    format="mixed",
                )
            )

        except (TypeError, ValueError):

            normalized_df["visit_date"] = (
                pd.to_datetime(
                    normalized_df["visit_date"],
                    errors="coerce",
                )
            )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column not in normalized_df.columns:
            continue

        normalized_df[column] = pd.to_numeric(
            normalized_df[column],
            errors="coerce",
        )

    return normalized_df


# ============================================================
# Helper: Missing / Empty Values
# ============================================================

def _count_missing_or_empty(
    series: pd.Series,
) -> int:
    """
    Count null, blank, and whitespace-only values.
    """

    if series is None:
        return 0

    missing_values = int(
        series.isna().sum()
    )

    text_values = (
        series
        .astype("string")
        .str.strip()
    )

    empty_values = int(
        text_values
        .eq("")
        .fillna(False)
        .sum()
    )

    return missing_values + empty_values


# ============================================================
# Helper: Invalid Numeric Values
# ============================================================

def _count_invalid_numeric_values(
    series: pd.Series,
) -> int:
    """
    Count values that cannot be interpreted as numeric.

    Existing null/blank values are also counted because they
    cannot be used for numeric analytics.
    """

    if series is None:
        return 0

    numeric_values = pd.to_numeric(
        series,
        errors="coerce",
    )

    return int(
        numeric_values.isna().sum()
    )


# ============================================================
# Data Quality Validation
# ============================================================

def validate_data_quality(
    df: pd.DataFrame,
) -> dict:
    """
    Validate the uploaded healthcare dataset.

    Validation is adaptive:

    Required
    --------
    - patient_id

    Optional
    --------
    - patient_name
    - visit_date
    - risk_level
    - vital signs
    - laboratory fields
    - demographic fields
    - clinical information

    Missing optional fields generate no validation error.

    Returns
    -------
    dict
        {
            "is_valid": bool,
            "errors": list[str],
            "warnings": list[str]
        }
    """

    errors: list[str] = []
    warnings: list[str] = []

    # --------------------------------------------------------
    # Basic dataset check
    # --------------------------------------------------------

    if df is None:

        return {
            "is_valid": False,
            "errors": [
                "No dataset was provided."
            ],
            "warnings": [],
        }

    if not isinstance(df, pd.DataFrame):

        return {
            "is_valid": False,
            "errors": [
                "The provided dataset is not a pandas DataFrame."
            ],
            "warnings": [],
        }

    if df.empty:

        return {
            "is_valid": False,
            "errors": [
                "The dataset contains no records."
            ],
            "warnings": [],
        }

    if len(df.columns) == 0:

        return {
            "is_valid": False,
            "errors": [
                "The dataset does not contain any columns."
            ],
            "warnings": [],
        }

    # --------------------------------------------------------
    # Required column validation
    # --------------------------------------------------------

    columns_valid, missing_columns = (
        validate_columns(df)
    )

    if not columns_valid:

        errors.append(
            "Missing required column(s): "
            + ", ".join(
                missing_columns
            )
        )

    # --------------------------------------------------------
    # Patient ID validation
    # --------------------------------------------------------

    if "patient_id" in df.columns:

        missing_ids = _count_missing_or_empty(
            df["patient_id"]
        )

        if missing_ids > 0:

            warnings.append(
                f"{missing_ids:,} records have "
                "missing or empty patient IDs."
            )

        valid_ids = (
            df["patient_id"]
            .astype("string")
            .str.strip()
        )

        valid_ids = valid_ids[
            valid_ids.notna()
            & (valid_ids != "")
        ]

        if valid_ids.empty:

            errors.append(
                "The dataset does not contain any valid "
                "patient identifiers."
            )

    # --------------------------------------------------------
    # Patient name validation
    # --------------------------------------------------------

    if "patient_name" in df.columns:

        missing_names = _count_missing_or_empty(
            df["patient_name"]
        )

        if missing_names > 0:

            warnings.append(
                f"{missing_names:,} records have "
                "missing or empty patient names."
            )

    # --------------------------------------------------------
    # Visit date validation
    # --------------------------------------------------------

    if "visit_date" in df.columns:

        date_values = pd.to_datetime(
            df["visit_date"],
            errors="coerce",
        )

        invalid_dates = int(
            date_values.isna().sum()
        )

        if invalid_dates > 0:

            warnings.append(
                f"{invalid_dates:,} records have "
                "missing or invalid visit dates."
            )

    # --------------------------------------------------------
    # Risk level validation
    # --------------------------------------------------------

    if "risk_level" in df.columns:

        risk_values = (
            df["risk_level"]
            .astype("string")
            .str.strip()
            .str.title()
        )

        non_empty_risk_values = risk_values[
            risk_values.notna()
            & (risk_values != "")
        ]

        unexpected_risks = sorted(
            set(
                non_empty_risk_values
            )
            - VALID_RISK_LEVELS
        )

        if unexpected_risks:

            warnings.append(
                "Unexpected risk levels found: "
                + ", ".join(
                    str(value)
                    for value in unexpected_risks
                )
            )

        missing_risk = int(
            (
                risk_values.isna()
                | risk_values.eq("")
            ).sum()
        )

        if missing_risk > 0:

            warnings.append(
                f"{missing_risk:,} records have "
                "missing risk levels."
            )

    # --------------------------------------------------------
    # Numeric field quality
    #
    # Only fields actually present are checked.
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:
            continue

        invalid_values = (
            _count_invalid_numeric_values(
                df[column]
            )
        )

        if invalid_values > 0:

            warnings.append(
                f"{column}: "
                f"{invalid_values:,} missing or "
                "invalid numeric values."
            )

    # --------------------------------------------------------
    # Duplicate complete rows
    # --------------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:

        warnings.append(
            f"{duplicate_rows:,} duplicate rows detected."
        )

    # --------------------------------------------------------
    # Duplicate patient/date records
    #
    # Only meaningful when both fields are available.
    # --------------------------------------------------------

    if {
        "patient_id",
        "visit_date",
    }.issubset(df.columns):

        duplicate_visits = int(
            df.duplicated(
                subset=[
                    "patient_id",
                    "visit_date",
                ],
            ).sum()
        )

        if duplicate_visits > 0:

            warnings.append(
                f"{duplicate_visits:,} duplicate "
                "patient/date records detected."
            )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# Data Quality Report
# ============================================================

def get_data_quality_report(
    df: pd.DataFrame,
) -> dict:
    """
    Generate a dataset quality summary.

    The report works with any recognized combination of
    healthcare fields and preserves information about
    additional columns.

    Returns
    -------
    dict
        rows
        columns
        duplicate_rows
        missing_cells
        missing_by_column
    """

    if df is None:

        return {
            "rows": 0,
            "columns": 0,
            "duplicate_rows": 0,
            "missing_cells": 0,
            "missing_by_column": {},
        }

    if not isinstance(df, pd.DataFrame):

        return {
            "rows": 0,
            "columns": 0,
            "duplicate_rows": 0,
            "missing_cells": 0,
            "missing_by_column": {},
        }

    # --------------------------------------------------------
    # Missing values
    #
    # Include both null values and blank strings because
    # uploaded CSVs are initially read with
    # keep_default_na=False.
    # --------------------------------------------------------

    missing_by_column: dict[str, int] = {}

    for column in df.columns:

        missing_count = _count_missing_or_empty(
            df[column]
        )

        if missing_count > 0:

            missing_by_column[
                str(column)
            ] = missing_count

    missing_cells = int(
        sum(
            missing_by_column.values()
        )
    )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    return {
        "rows": int(
            len(df)
        ),

        "columns": int(
            len(df.columns)
        ),

        "duplicate_rows": duplicate_rows,

        "missing_cells": missing_cells,

        "missing_by_column": (
            missing_by_column
        ),
    }