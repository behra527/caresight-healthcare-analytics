from __future__ import annotations

from io import BytesIO

import pandas as pd

from src.schema import (
    apply_column_mapping,
    detect_columns,
    get_available_canonical_columns,
    get_available_trend_fields,
    get_missing_optional_columns,
    get_missing_required_columns,
    get_unmapped_columns,
)


# ============================================================
# Internal CSV Reader
# ============================================================

def _read_uploaded_csv(
    uploaded_file,
) -> pd.DataFrame:
    """
    Read a Streamlit UploadedFile into a pandas DataFrame.

    Responsibilities
    ----------------
    - Verify that a file was uploaded.
    - Read CSV content safely.
    - Preserve values such as "None" and "N/A" as text
      during the initial loading stage.
    - Reject empty files.
    - Reject CSV files without columns.

    Schema detection and data validation are handled
    separately.
    """

    if uploaded_file is None:
        raise ValueError(
            "No CSV file was uploaded."
        )

    try:
        file_bytes = uploaded_file.getvalue()

        if not file_bytes:
            raise ValueError(
                "The uploaded CSV file is empty."
            )

        df = pd.read_csv(
            BytesIO(file_bytes),
            keep_default_na=False,
        )

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            f"Unable to read the CSV file: {exc}"
        ) from exc

    if len(df.columns) == 0:
        raise ValueError(
            "The uploaded CSV file does not contain "
            "any columns."
        )

    if df.empty:
        raise ValueError(
            "The uploaded CSV file contains no records."
        )

    return df


# ============================================================
# Load Healthcare CSV
# ============================================================

def load_csv(
    uploaded_file,
) -> pd.DataFrame:
    """
    Load and prepare an uploaded healthcare CSV.

    Processing
    ----------
    1. Read the uploaded CSV.
    2. Detect patient/healthcare columns.
    3. Verify required patient_id field.
    4. Apply canonical column mapping.
    5. Verify patient_id after mapping.
    6. Return the prepared DataFrame.

    Example mapping
    ---------------
    Patient_ID       -> patient_id
    Name             -> patient_name
    Age              -> age
    Gender           -> gender
    Timestamp        -> visit_date
    Heart_Rate       -> heart_rate
    Systolic_BP      -> systolic_bp
    Diastolic_BP     -> diastolic_bp
    SpO2             -> spo2

    Unknown columns are preserved.
    No values are fabricated.
    """

    # --------------------------------------------------------
    # Step 1: Read raw CSV
    # --------------------------------------------------------

    df = _read_uploaded_csv(
        uploaded_file
    )

    # --------------------------------------------------------
    # Step 2: Detect healthcare fields
    # --------------------------------------------------------

    detected_columns = detect_columns(
        df
    )

    # --------------------------------------------------------
    # Step 3: Required patient field check
    #
    # Patient ID is required because the dashboard is
    # patient-centric.
    # --------------------------------------------------------

    missing_columns = (
        get_missing_required_columns(
            df
        )
    )

    if missing_columns:
        raise ValueError(
            "The uploaded CSV could not be used as a "
            "patient dataset because the following required "
            "field(s) were not detected: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # Step 4: Apply canonical mapping
    # --------------------------------------------------------

    mapped_df = apply_column_mapping(
        df
    )

    # --------------------------------------------------------
    # Step 5: Final required-field check
    # --------------------------------------------------------

    final_missing_columns = (
        get_missing_required_columns(
            mapped_df
        )
    )

    if final_missing_columns:
        raise ValueError(
            "Healthcare column mapping failed. "
            "Missing required field(s): "
            + ", ".join(
                final_missing_columns
            )
        )

    # --------------------------------------------------------
    # Step 6: Basic patient ID sanity check
    # --------------------------------------------------------

    if "patient_id" in mapped_df.columns:

        patient_ids = (
            mapped_df["patient_id"]
            .astype("string")
            .str.strip()
        )

        valid_patient_ids = patient_ids[
            patient_ids.notna()
            & (patient_ids != "")
        ]

        if valid_patient_ids.empty:
            raise ValueError(
                "The uploaded CSV contains a patient_id "
                "column, but it does not contain any valid "
                "patient identifiers."
            )

        # Store cleaned patient IDs.
        mapped_df["patient_id"] = patient_ids

    return mapped_df


# ============================================================
# CSV Column Mapping
# ============================================================

def get_csv_column_mapping(
    uploaded_file,
) -> dict[str, str]:
    """
    Return raw CSV column -> canonical field mappings.

    Example
    -------
    {
        "Patient_ID": "patient_id",
        "Name": "patient_name",
        "Age": "age",
        "Timestamp": "visit_date",
        "Heart_Rate": "heart_rate",
        "Systolic_BP": "systolic_bp",
        "Diastolic_BP": "diastolic_bp",
        "SpO2": "spo2"
    }

    Unknown columns are not included.
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    return detect_columns(
        df
    )


# ============================================================
# Available Healthcare Fields
# ============================================================

def get_csv_available_fields(
    uploaded_file,
) -> list[str]:
    """
    Return recognized canonical healthcare fields
    available in the uploaded CSV.

    Example
    -------
    [
        "age",
        "gender",
        "heart_rate",
        "patient_id",
        "spo2",
        "visit_date"
    ]
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    return get_available_canonical_columns(
        df
    )


# ============================================================
# Available Trend Fields
# ============================================================

def get_csv_available_trend_fields(
    uploaded_file,
) -> list[str]:
    """
    Return vital/measurement fields that can be used
    for patient trend charts.
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    return get_available_trend_fields(
        df
    )


# ============================================================
# Missing Optional Healthcare Fields
# ============================================================

def get_csv_missing_optional_fields(
    uploaded_file,
) -> list[str]:
    """
    Return known optional healthcare fields that are not
    available in the uploaded CSV.

    This is informational only.
    Missing optional fields do not prevent the dashboard
    from loading the patient data.
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    return get_missing_optional_columns(
        df
    )


# ============================================================
# Unmapped / Additional CSV Columns
# ============================================================

def get_csv_unmapped_columns(
    uploaded_file,
) -> list[str]:
    """
    Return raw CSV columns that are not recognized by
    the healthcare schema.

    Unknown columns remain in the DataFrame and are not
    treated as an upload error.
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    return get_unmapped_columns(
        df
    )


# ============================================================
# CSV Information
# ============================================================

def get_csv_information(
    uploaded_file,
) -> dict:
    """
    Return structured information about the uploaded CSV.

    Intended for:
    - dashboard upload status
    - schema information
    - debugging
    - logging
    - data-quality UI

    Returns
    -------
    dict
        filename
        rows
        columns
        original_columns
        detected_columns
        detected_count
        available_fields
        available_field_count
        available_trend_fields
        missing_optional_fields
        unmapped_columns
        unmapped_count
    """

    df = _read_uploaded_csv(
        uploaded_file
    )

    detected_columns = detect_columns(
        df
    )

    available_fields = (
        get_available_canonical_columns(
            df
        )
    )

    available_trend_fields = (
        get_available_trend_fields(
            df
        )
    )

    missing_optional_fields = (
        get_missing_optional_columns(
            df
        )
    )

    unmapped_columns = (
        get_unmapped_columns(
            df
        )
    )

    return {
        "filename": getattr(
            uploaded_file,
            "name",
            "uploaded.csv",
        ),

        "rows": int(
            len(df)
        ),

        "columns": int(
            len(df.columns)
        ),

        "original_columns": [
            str(column)
            for column in df.columns
        ],

        "detected_columns": detected_columns,

        "detected_count": int(
            len(detected_columns)
        ),

        "available_fields": available_fields,

        "available_field_count": int(
            len(available_fields)
        ),

        "available_trend_fields": (
            available_trend_fields
        ),

        "missing_optional_fields": (
            missing_optional_fields
        ),

        "unmapped_columns": (
            unmapped_columns
        ),

        "unmapped_count": int(
            len(unmapped_columns)
        ),
    }