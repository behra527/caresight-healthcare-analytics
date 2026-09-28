from __future__ import annotations

import pandas as pd


# ============================================================
# Configuration
# ============================================================

DEMOGRAPHIC_FIELDS = [
    "patient_name",
    "age",
    "gender",
    "blood_group",
]


VITAL_FIELDS = [
    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "temperature",
    "glucose",
    "hba1c",
    "cholesterol",
    "wbc",
    "bmi",
    "weight_kg",
]


CLINICAL_FIELDS = [
    "diabetes",
    "hypertension",
    "heart_disease",
    "asthma",
    "kidney_disease",
    "smoking_status",
    "diagnosis",
    "medication",
    "allergies",
]


RISK_FIELDS = [
    "risk_level",
]


# ============================================================
# Internal Helpers
# ============================================================

def _empty_dataframe() -> pd.DataFrame:
    """Return an empty DataFrame."""
    return pd.DataFrame()


def _clean_patient_id(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize patient identifiers for reliable comparison.
    """

    return (
        series
        .astype("string")
        .str.strip()
    )


def _clean_text(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize text values.
    """

    return (
        series
        .astype("string")
        .str.strip()
    )


def _valid_patient_ids(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Return valid non-empty patient identifiers.
    """

    if (
        df is None
        or df.empty
        or "patient_id" not in df.columns
    ):
        return pd.Series(
            dtype="string"
        )

    patient_ids = _clean_patient_id(
        df["patient_id"]
    )

    return patient_ids[
        patient_ids.notna()
        & patient_ids.ne("")
    ]


def _sort_patient_records(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Sort records chronologically when visit_date exists.

    Patient ID is used as the secondary sorting field when
    available.
    """

    if df is None or df.empty:
        return (
            df.copy()
            if df is not None
            else pd.DataFrame()
        )

    working_df = df.copy()

    if "visit_date" in working_df.columns:

        working_df["visit_date"] = pd.to_datetime(
            working_df["visit_date"],
            errors="coerce",
        )

        if "patient_id" in working_df.columns:

            working_df = working_df.sort_values(
                [
                    "patient_id",
                    "visit_date",
                ],
                kind="stable",
            )

        else:

            working_df = working_df.sort_values(
                "visit_date",
                kind="stable",
            )

    elif "patient_id" in working_df.columns:

        working_df = working_df.sort_values(
            "patient_id",
            kind="stable",
        )

    return working_df


def _get_latest_row(
    df: pd.DataFrame,
) -> pd.Series | None:
    """
    Return the latest row from a patient's records.

    visit_date is preferred when available.
    Otherwise the last available record is used.
    """

    if df is None or df.empty:
        return None

    working_df = df.copy()

    if "visit_date" in working_df.columns:

        working_df["visit_date"] = pd.to_datetime(
            working_df["visit_date"],
            errors="coerce",
        )

        valid_dates = working_df[
            working_df["visit_date"].notna()
        ]

        if not valid_dates.empty:

            return valid_dates.loc[
                valid_dates["visit_date"].idxmax()
            ]

    return working_df.iloc[-1]


# ============================================================
# Dataset Metrics
# ============================================================

def get_dataset_metrics(
    df: pd.DataFrame,
) -> dict:
    """
    Generate patient-focused dashboard metrics.

    Returns
    -------
    dict
        total_patients
        total_visits
        total_records
        high_risk_patients
        medium_risk_patients
        low_risk_patients
        risk_available
        date_available
    """

    metrics = {
        "total_patients": 0,
        "total_visits": 0,
        "total_records": 0,
        "high_risk_patients": None,
        "medium_risk_patients": None,
        "low_risk_patients": None,
        "risk_available": False,
        "date_available": False,
    }

    if df is None or df.empty:
        return metrics

    metrics["total_records"] = int(
        len(df)
    )

    metrics["total_visits"] = int(
        len(df)
    )

    # --------------------------------------------------------
    # Patient count
    # --------------------------------------------------------

    if "patient_id" in df.columns:

        patient_ids = _valid_patient_ids(
            df
        )

        metrics["total_patients"] = int(
            patient_ids.nunique()
        )

    # --------------------------------------------------------
    # Date availability
    # --------------------------------------------------------

    if "visit_date" in df.columns:

        dates = pd.to_datetime(
            df["visit_date"],
            errors="coerce",
        )

        metrics["date_available"] = bool(
            dates.notna().any()
        )

    # --------------------------------------------------------
    # Risk distribution
    #
    # Counts are patient-level when patient_id exists.
    # --------------------------------------------------------

    if "risk_level" in df.columns:

        metrics["risk_available"] = True

        if "patient_id" in df.columns:

            patient_summary = get_patient_summary(
                df
            )

            if (
                not patient_summary.empty
                and "risk_level"
                in patient_summary.columns
            ):

                risk_values = (
                    patient_summary["risk_level"]
                    .astype("string")
                    .str.strip()
                    .str.casefold()
                )

                metrics["high_risk_patients"] = int(
                    risk_values.eq("high").sum()
                )

                metrics["medium_risk_patients"] = int(
                    risk_values.eq("medium").sum()
                )

                metrics["low_risk_patients"] = int(
                    risk_values.eq("low").sum()
                )

        else:

            risk_values = (
                df["risk_level"]
                .astype("string")
                .str.strip()
                .str.casefold()
            )

            metrics["high_risk_patients"] = int(
                risk_values.eq("high").sum()
            )

            metrics["medium_risk_patients"] = int(
                risk_values.eq("medium").sum()
            )

            metrics["low_risk_patients"] = int(
                risk_values.eq("low").sum()
            )

    return metrics


# ============================================================
# Dashboard Metrics
# ============================================================

def get_dashboard_metrics(
    df: pd.DataFrame,
) -> dict:
    """
    Return KPI metrics used directly by the dashboard.

    This function is kept as a compatibility wrapper around
    get_dataset_metrics().
    """

    metrics = get_dataset_metrics(
        df
    )

    return {
        "total_patients": metrics[
            "total_patients"
        ],

        "total_visits": metrics[
            "total_visits"
        ],

        "high_risk_patients": metrics[
            "high_risk_patients"
        ],

        "medium_risk_patients": metrics[
            "medium_risk_patients"
        ],

        "low_risk_patients": metrics[
            "low_risk_patients"
        ],
    }


# ============================================================
# Patient Summary
# ============================================================

def get_patient_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create one summary row per patient.

    The summary contains only fields that are actually
    available in the uploaded dataset.

    Includes:
    - patient identity
    - demographics
    - latest risk level
    - visit count
    - last visit
    - latest available vital measurements
    """

    if (
        df is None
        or df.empty
        or "patient_id" not in df.columns
    ):
        return _empty_dataframe()

    working_df = df.copy()

    working_df["patient_id"] = _clean_patient_id(
        working_df["patient_id"]
    )

    working_df = working_df[
        working_df["patient_id"].notna()
        & working_df["patient_id"].ne("")
    ].copy()

    if working_df.empty:
        return _empty_dataframe()

    # --------------------------------------------------------
    # Normalize date if available
    # --------------------------------------------------------

    if "visit_date" in working_df.columns:

        working_df["visit_date"] = pd.to_datetime(
            working_df["visit_date"],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Sort so "last" means latest available record
    # --------------------------------------------------------

    working_df = _sort_patient_records(
        working_df
    )

    aggregation = {}

    # --------------------------------------------------------
    # Demographics
    # --------------------------------------------------------

    for field in DEMOGRAPHIC_FIELDS:

        if field in working_df.columns:

            aggregation[field] = (
                field,
                "first",
            )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    if "risk_level" in working_df.columns:

        aggregation["risk_level"] = (
            "risk_level",
            "last",
        )

    # --------------------------------------------------------
    # Visit information
    # --------------------------------------------------------

    if "visit_date" in working_df.columns:

        aggregation["visits"] = (
            "visit_date",
            "count",
        )

        aggregation["last_visit"] = (
            "visit_date",
            "max",
        )

    else:

        aggregation["visits"] = (
            "patient_id",
            "size",
        )

    # --------------------------------------------------------
    # Latest available vitals
    # --------------------------------------------------------

    for field in VITAL_FIELDS:

        if field in working_df.columns:

            aggregation[
                f"latest_{field}"
            ] = (
                field,
                "last",
            )

    # --------------------------------------------------------
    # Group by patient
    # --------------------------------------------------------

    summary = (
        working_df
        .groupby(
            "patient_id",
            as_index=False,
            sort=False,
        )
        .agg(**aggregation)
    )

    # --------------------------------------------------------
    # Stable patient ordering
    # --------------------------------------------------------

    if "patient_name" in summary.columns:

        summary = summary.sort_values(
            [
                "patient_name",
                "patient_id",
            ],
            kind="stable",
        )

    else:

        summary = summary.sort_values(
            "patient_id",
            kind="stable",
        )

    return summary.reset_index(
        drop=True
    )


# ============================================================
# Risk Filter
# ============================================================

def filter_by_risk(
    df: pd.DataFrame,
    risk_level: str | None,
) -> pd.DataFrame:
    """
    Filter patient records by risk level.

    Parameters
    ----------
    df:
        Healthcare records.

    risk_level:
        "All", "Low", "Medium", or "High".

    Behavior
    --------
    - "All" returns all records.
    - Missing risk_level column returns all records.
    - Matching is case-insensitive.
    """

    if df is None or df.empty:
        return (
            df.copy()
            if df is not None
            else pd.DataFrame()
        )

    if (
        risk_level is None
        or not isinstance(
            risk_level,
            str,
        )
        or risk_level.strip().casefold() == "all"
    ):
        return df.copy()

    if "risk_level" not in df.columns:
        return df.copy()

    target = risk_level.strip().casefold()

    values = (
        df["risk_level"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    return df[
        values.eq(target)
    ].copy()


# ============================================================
# Patient Records
# ============================================================

def get_patient_records(
    df: pd.DataFrame,
    patient_id,
) -> pd.DataFrame:
    """
    Return all records for one selected patient.

    Records are sorted chronologically when visit_date
    is available.
    """

    if (
        df is None
        or df.empty
        or "patient_id" not in df.columns
    ):
        return _empty_dataframe()

    if patient_id is None:
        return _empty_dataframe()

    target_id = str(
        patient_id
    ).strip()

    if not target_id:
        return _empty_dataframe()

    patient_ids = _clean_patient_id(
        df["patient_id"]
    )

    patient_df = df[
        patient_ids.eq(target_id)
    ].copy()

    if patient_df.empty:
        return patient_df

    return _sort_patient_records(
        patient_df
    ).reset_index(
        drop=True
    )


# ============================================================
# Latest Patient Record
# ============================================================

def get_latest_patient_record(
    df: pd.DataFrame,
    patient_id,
) -> pd.DataFrame:
    """
    Return the latest available record for a patient.

    If visit_date exists, the latest valid date is used.
    Otherwise the last available patient record is returned.
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    if patient_df.empty:
        return patient_df

    latest_row = _get_latest_row(
        patient_df
    )

    if latest_row is None:
        return _empty_dataframe()

    return pd.DataFrame(
        [latest_row]
    ).reset_index(
        drop=True
    )


# ============================================================
# Patient Vitals
# ============================================================

def get_patient_vitals(
    df: pd.DataFrame,
    patient_id,
) -> pd.DataFrame:
    """
    Return available vital/measurement fields for a patient.

    Only fields present in the uploaded dataset are returned.

    This function does not create or calculate missing
    clinical measurements.
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    if patient_df.empty:
        return _empty_dataframe()

    available_vitals = [
        field
        for field in VITAL_FIELDS
        if field in patient_df.columns
    ]

    columns = []

    if "visit_date" in patient_df.columns:
        columns.append("visit_date")

    columns.extend(
        available_vitals
    )

    if not columns:
        return _empty_dataframe()

    return patient_df[
        columns
    ].copy()


# ============================================================
# Patient Demographics
# ============================================================

def get_patient_demographics(
    df: pd.DataFrame,
    patient_id,
) -> dict:
    """
    Return available demographic information for a patient.

    Only fields actually present in the dataset are returned.
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    if patient_df.empty:
        return {}

    latest_record = _get_latest_row(
        patient_df
    )

    if latest_record is None:
        return {}

    result = {
        "patient_id": str(
            patient_id
        ).strip()
    }

    for field in DEMOGRAPHIC_FIELDS:

        if field not in latest_record.index:
            continue

        value = latest_record[field]

        if pd.isna(value):
            continue

        if isinstance(value, str):

            value = value.strip()

            if not value:
                continue

        result[field] = value

    return result


# ============================================================
# Patient Clinical Information
# ============================================================

def get_patient_clinical_info(
    df: pd.DataFrame,
    patient_id,
) -> dict:
    """
    Return available clinical information for a patient.

    This function only displays uploaded data. It does not
    infer diagnoses, conditions, or treatments.
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    if patient_df.empty:
        return {}

    latest_record = _get_latest_row(
        patient_df
    )

    if latest_record is None:
        return {}

    result = {}

    for field in CLINICAL_FIELDS:

        if field not in latest_record.index:
            continue

        value = latest_record[field]

        if pd.isna(value):
            continue

        if isinstance(value, str):

            value = value.strip()

            if not value:
                continue

        result[field] = value

    return result


# ============================================================
# Available Patient Fields
# ============================================================

def get_available_patient_fields(
    df: pd.DataFrame,
) -> dict[str, list[str]]:
    """
    Return healthcare fields available for patient analysis.

    The result is grouped into:
    - demographics
    - vitals
    - clinical
    - risk
    """

    available = {
        "demographics": [],
        "vitals": [],
        "clinical": [],
        "risk": [],
    }

    if df is None or df.empty:
        return available

    available["demographics"] = [
        field
        for field in DEMOGRAPHIC_FIELDS
        if field in df.columns
    ]

    available["vitals"] = [
        field
        for field in VITAL_FIELDS
        if field in df.columns
    ]

    available["clinical"] = [
        field
        for field in CLINICAL_FIELDS
        if field in df.columns
    ]

    available["risk"] = [
        field
        for field in RISK_FIELDS
        if field in df.columns
    ]

    return available


# ============================================================
# Available Trend Fields
# ============================================================

def get_available_trend_fields(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return available patient-level vital fields that can
    support trend visualization.

    visit_date is not required here because this function
    only identifies available measurements.
    """

    if df is None or df.empty:
        return []

    return [
        field
        for field in VITAL_FIELDS
        if field in df.columns
    ]


# ============================================================
# Patient Search
# ============================================================

def search_patients(
    df: pd.DataFrame,
    search_term: str | None,
) -> pd.DataFrame:
    """
    Search patients by patient ID or patient name.

    Search is case-insensitive.

    If no search term is supplied, the original DataFrame
    is returned unchanged.
    """

    if df is None or df.empty:
        return (
            df.copy()
            if df is not None
            else pd.DataFrame()
        )

    if (
        search_term is None
        or not str(search_term).strip()
    ):
        return df.copy()

    query = str(
        search_term
    ).strip().casefold()

    mask = pd.Series(
        False,
        index=df.index,
    )

    if "patient_id" in df.columns:

        patient_ids = (
            df["patient_id"]
            .astype("string")
            .str.strip()
            .str.casefold()
        )

        mask = mask | patient_ids.str.contains(
            query,
            na=False,
            regex=False,
        )

    if "patient_name" in df.columns:

        names = (
            df["patient_name"]
            .astype("string")
            .str.strip()
            .str.casefold()
        )

        mask = mask | names.str.contains(
            query,
            na=False,
            regex=False,
        )

    return df[
        mask
    ].copy()


# ============================================================
# Patient List
# ============================================================

def get_patient_list(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return unique valid patient IDs.

    Patient IDs are sorted for stable UI selection.
    """

    if df is None or df.empty:
        return []

    patient_ids = _valid_patient_ids(
        df
    )

    if patient_ids.empty:
        return []

    return sorted(
        patient_ids.unique().tolist()
    )


# ============================================================
# Patient Visit Count
# ============================================================

def get_patient_visit_count(
    df: pd.DataFrame,
    patient_id,
) -> int:
    """
    Return the number of records/visits for a patient.
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    return int(
        len(patient_df)
    )


# ============================================================
# Patient Date Range
# ============================================================

def get_patient_date_range(
    df: pd.DataFrame,
    patient_id,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    """
    Return the first and latest valid visit date for a patient.

    Returns
    -------
    tuple
        (first_visit, last_visit)
    """

    patient_df = get_patient_records(
        df,
        patient_id,
    )

    if (
        patient_df.empty
        or "visit_date" not in patient_df.columns
    ):
        return None, None

    dates = pd.to_datetime(
        patient_df["visit_date"],
        errors="coerce",
    ).dropna()

    if dates.empty:
        return None, None

    return (
        dates.min(),
        dates.max(),
    )


# ============================================================
# Patient Analytics Capabilities
# ============================================================

def get_patient_analytics(
    df: pd.DataFrame,
) -> dict[str, bool]:
    """
    Determine which patient-dashboard features are supported
    by the uploaded dataset.

    No unsupported feature is marked as available.
    """

    capabilities = {
        "patient_selection": False,
        "patient_summary": False,
        "patient_history": False,
        "patient_trends": False,
        "risk_filter": False,
        "patient_demographics": False,
        "patient_clinical_info": False,
    }

    if df is None or df.empty:
        return capabilities

    has_patient_id = (
        "patient_id" in df.columns
        and _valid_patient_ids(df).nunique() > 0
    )

    has_visit_date = False

    if "visit_date" in df.columns:

        dates = pd.to_datetime(
            df["visit_date"],
            errors="coerce",
        )

        has_visit_date = bool(
            dates.notna().any()
        )

    available_vitals = (
        get_available_trend_fields(
            df
        )
    )

    capabilities["patient_selection"] = (
        has_patient_id
    )

    capabilities["patient_summary"] = (
        has_patient_id
    )

    capabilities["patient_history"] = (
        has_patient_id
        and has_visit_date
    )

    capabilities["patient_trends"] = (
        has_patient_id
        and has_visit_date
        and bool(available_vitals)
    )

    capabilities["risk_filter"] = (
        has_patient_id
        and "risk_level" in df.columns
    )

    capabilities["patient_demographics"] = (
        has_patient_id
        and any(
            field in df.columns
            for field in DEMOGRAPHIC_FIELDS
        )
    )

    capabilities["patient_clinical_info"] = (
        has_patient_id
        and any(
            field in df.columns
            for field in CLINICAL_FIELDS
        )
    )

    return capabilities