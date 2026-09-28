from __future__ import annotations

import re

import pandas as pd


# ============================================================
# Canonical Healthcare Fields
# ============================================================

COLUMN_ALIASES: dict[str, list[str]] = {
    # --------------------------------------------------------
    # Patient Identity
    # --------------------------------------------------------
    "patient_id": [
        "patient_id",
        "patient id",
        "patientid",
        "patient_identifier",
        "patient identifier",
        "patient number",
        "patient no",
        "patient_no",
        "patient code",
        "patient_code",
        "patient reference",
        "patient ref",
        "subject id",
        "subject_id",
        "subject identifier",
        "member id",
        "member_id",
        "medical record number",
        "medical_record_number",
        "medical record no",
        "mrn",
        "mr number",
        "record id",
        "record_id",
    ],

    "patient_name": [
        "patient_name",
        "patient name",
        "patientname",
        "patient full name",
        "patient fullname",
        "full name",
        "full_name",
        "name",
    ],

    # --------------------------------------------------------
    # Demographics
    # --------------------------------------------------------
    "age": [
        "age",
        "patient_age",
        "patient age",
        "age years",
        "age in years",
        "age_years",
        "age_yrs",
        "age yrs",
        "years old",
        "patient years",
    ],

    "gender": [
        "gender",
        "sex",
        "patient gender",
        "patient sex",
        "biological sex",
    ],

    "blood_group": [
        "blood_group",
        "blood group",
        "bloodgroup",
        "blood_type",
        "blood type",
        "blood group type",
        "abo blood group",
        "abo type",
    ],

    # --------------------------------------------------------
    # Visit / Date
    # --------------------------------------------------------
    "visit_date": [
        "visit_date",
        "visit date",
        "visitdate",
        "date",
        "date of visit",
        "visit day",
        "encounter_date",
        "encounter date",
        "encounter date time",
        "encounter datetime",
        "appointment date",
        "appointment datetime",
        "admission date",
        "admission datetime",
        "record date",
        "record datetime",
        "timestamp",
        "time stamp",
        "datetime",
        "date time",
        "date_time",
        "encounter timestamp",
        "visit timestamp",
        "event date",
        "event datetime",
        "observation date",
        "observation datetime",
        "measurement date",
        "measurement datetime",
        "discharge date",
        "discharge datetime",
        "followup date",
        "follow up date",
    ],

    "visit_type": [
        "visit_type",
        "visit type",
        "encounter type",
        "appointment type",
        "visit category",
        "encounter category",
    ],

    "department": [
        "department",
        "dept",
        "medical department",
        "clinic",
        "hospital department",
        "department name",
        "clinic name",
        "specialty",
        "medical specialty",
    ],

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------
    "risk_level": [
        "risk_level",
        "risk level",
        "risk",
        "risk_category",
        "risk category",
        "risk status",
        "risk_status",
        "patient risk",
        "patient risk level",
        "risk classification",
        "risk class",
        "risk group",
        "risk score category",
        "risk category label",
    ],

    # --------------------------------------------------------
    # Vital Signs
    # --------------------------------------------------------
    "systolic_bp": [
        "systolic_bp",
        "systolic bp",
        "systolic blood pressure",
        "systolic blood pressure mmhg",
        "sbp",
        "systolic",
        "systolic pressure",
        "systolic bp mmhg",
        "systolicbp",
        "systolic_blood_pressure",
        "bp systolic",
        "bp_systolic",
        "blood pressure systolic",
        "bloodpressure systolic",
    ],

    "diastolic_bp": [
        "diastolic_bp",
        "diastolic bp",
        "diastolic blood pressure",
        "diastolic blood pressure mmhg",
        "dbp",
        "diastolic",
        "diastolic pressure",
        "diastolic bp mmhg",
        "diastolicbp",
        "diastolic_blood_pressure",
        "bp diastolic",
        "bp_diastolic",
        "blood pressure diastolic",
        "bloodpressure diastolic",
    ],

    "heart_rate": [
        "heart_rate",
        "heart rate",
        "heartrate",
        "pulse",
        "pulse rate",
        "pulse_rate",
        "heart rate bpm",
        "heart_rate_bpm",
        "pulse bpm",
        "pulse_rate_bpm",
        "hr",
        "hr bpm",
        "heart beats per minute",
        "beats per minute",
        "bpm",
    ],

    "spo2": [
        "spo2",
        "sp_o2",
        "sp o2",
        "oxygen saturation",
        "oxygen_sat",
        "oxygen saturation percent",
        "oxygen saturation percentage",
        "o2 saturation",
        "o2 sat",
        "oxygen level",
        "oxygen saturation spo2",
        "oxygen saturation pct",
        "saturation",
    ],

    "respiratory_rate": [
        "respiratory_rate",
        "respiratory rate",
        "respiration rate",
        "breathing rate",
        "rr",
        "respiratory rate bpm",
        "respiratory_rate_bpm",
        "respiratoryrate",
        "resp rate",
        "respiration",
        "breaths per minute",
        "breathing frequency",
    ],

    "temperature": [
        "temperature",
        "body temperature",
        "body temp",
        "body_temperature",
        "temp",
        "temp c",
        "temperature c",
        "temperature_c",
        "body temperature c",
        "temperature fahrenheit",
        "temperature f",
        "temp f",
        "temp_c",
        "temp_f",
        "bodytemp",
    ],

    "glucose": [
        "glucose",
        "blood glucose",
        "blood glucose level",
        "blood sugar",
        "blood sugar level",
        "blood_sugar",
        "blood_sugar_level",
        "glucose level",
        "glucose_level",
        "glucose reading",
        "blood glucose reading",
        "blood glucose mg dl",
        "blood sugar mg dl",
        "fasting glucose",
        "random glucose",
        "glucose mg dl",
        "blood glucose mg/dl",
        "blood sugar mg/dl",
        "bloodglucose",
        "bloodsugar",
        "fasting blood glucose",
        "random blood glucose",
        "fasting blood sugar",
        "random blood sugar",
        "serum glucose",
    ],

    # --------------------------------------------------------
    # Laboratory / Measurements
    # --------------------------------------------------------
    "hba1c": [
        "hba1c",
        "hb_a1c",
        "hb a1c",
        "hb a1c level",
        "glycated hemoglobin",
        "glycated haemoglobin",
        "hemoglobin a1c",
        "haemoglobin a1c",
        "a1c",
        "a1c level",
        "glycosylated hemoglobin",
        "glycosylated haemoglobin",
    ],

    "cholesterol": [
        "cholesterol",
        "total cholesterol",
        "cholesterol level",
        "total cholesterol level",
        "cholesterol total",
        "serum cholesterol",
        "cholesterol mg dl",
    ],

    "wbc": [
        "wbc",
        "white blood cells",
        "white blood cell count",
        "white blood cell",
        "wbc count",
        "white blood cells count",
        "leukocyte count",
        "leukocytes",
        "white cell count",
    ],

    # --------------------------------------------------------
    # Body Measurements
    # --------------------------------------------------------
    "height_cm": [
        "height_cm",
        "height cm",
        "height",
        "patient height",
        "height in cm",
        "height centimeters",
        "height centimetres",
    ],

    "weight_kg": [
        "weight_kg",
        "weight kg",
        "weight",
        "patient weight",
        "weight in kg",
        "weight kilograms",
        "body weight",
    ],

    "bmi": [
        "bmi",
        "body mass index",
        "body_mass_index",
        "body mass index value",
    ],

    # --------------------------------------------------------
    # Medical Conditions
    # --------------------------------------------------------
    "diabetes": [
        "diabetes",
        "diabetic",
        "diabetes status",
        "diabetic status",
        "diabetes condition",
        "diabetes diagnosis",
        "diabetes history",
    ],

    "hypertension": [
        "hypertension",
        "high blood pressure",
        "hypertension status",
        "high bp",
        "high blood pressure status",
        "hypertension condition",
        "hypertension diagnosis",
        "hypertension history",
    ],

    "heart_disease": [
        "heart_disease",
        "heart disease",
        "cardiac disease",
        "cardiovascular disease",
        "heart condition",
        "cardiac condition",
        "cardiovascular condition",
        "heart disease status",
        "cardiac disease status",
    ],

    "asthma": [
        "asthma",
        "asthma status",
        "asthma condition",
        "asthma diagnosis",
        "asthma history",
    ],

    "kidney_disease": [
        "kidney_disease",
        "kidney disease",
        "renal disease",
        "kidney condition",
        "renal condition",
        "kidney disease status",
        "renal disease status",
        "kidney diagnosis",
    ],

    "smoking_status": [
        "smoking_status",
        "smoking status",
        "smoker",
        "smoking",
        "smoking history",
        "smoking habit",
        "smoker status",
        "tobacco use",
        "tobacco usage",
    ],

    # --------------------------------------------------------
    # Clinical Information
    # --------------------------------------------------------
    "diagnosis": [
        "diagnosis",
        "medical diagnosis",
        "primary diagnosis",
        "medical condition",
        "diagnosis name",
        "disease",
        "disease name",
        "diagnostic condition",
    ],

    "medication": [
        "medication",
        "medicine",
        "medicines",
        "medication name",
        "drug",
        "drug name",
        "prescribed medication",
        "prescription",
        "prescribed drug",
        "medication description",
    ],

    "allergies": [
        "allergies",
        "allergy",
        "allergy information",
        "known allergies",
        "allergy history",
        "allergic conditions",
    ],
}


# ============================================================
# Required Canonical Fields
# ============================================================

# Patient ID is required because the application is a
# patient-level dashboard.
#
# Other healthcare fields remain optional. The dashboard
# displays details/charts only when the corresponding fields
# are available in the uploaded CSV.

REQUIRED_CANONICAL_COLUMNS: set[str] = {
    "patient_id",
}


# ============================================================
# Optional Healthcare Fields
# ============================================================

OPTIONAL_CANONICAL_COLUMNS: set[str] = {
    canonical_name
    for canonical_name in COLUMN_ALIASES
    if canonical_name not in REQUIRED_CANONICAL_COLUMNS
}


# ============================================================
# Fields Used for Patient Trend Charts
# ============================================================

TREND_FIELDS: set[str] = {
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
}


# ============================================================
# Numeric Healthcare Fields
# ============================================================

NUMERIC_CANONICAL_FIELDS: set[str] = {
    "age",
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
    "height_cm",
    "weight_kg",
    "bmi",
}


# ============================================================
# Date Fields
# ============================================================

DATE_CANONICAL_FIELDS: set[str] = {
    "visit_date",
}


# ============================================================
# Heuristic Patterns
# ============================================================

# Heuristics are intentionally conservative.
#
# Exact aliases are always preferred. Heuristics are used only
# when a real-world CSV uses a slightly different column name.

HEURISTIC_PATTERNS: dict[str, list[str]] = {
    "patient_id": [
        r"patient.*(id|identifier|number|no|code|key|ref)",
        r"(subject|member).*id",
        r"(medical|health).*record.*(id|number|no)",
        r"mrn",
    ],

    "patient_name": [
        r"patient.*name",
        r"full.*name",
        r"patient.*fullname",
    ],

    "age": [
        r"^age$",
        r"patient.*age",
        r"age.*(year|yr)",
        r"(year|yr).*age",
    ],

    "gender": [
        r"^gender$",
        r"^sex$",
        r"patient.*(gender|sex)",
        r"biological.*sex",
    ],

    "blood_group": [
        r"blood.*(group|type)",
        r"abo.*type",
    ],

    "visit_date": [
        r".*visit.*date.*",
        r".*encounter.*date.*",
        r".*appointment.*date.*",
        r".*admission.*date.*",
        r".*discharge.*date.*",
        r".*observation.*date.*",
        r".*measurement.*date.*",
        r".*record.*date.*",
        r".*event.*date.*",
        r".*timestamp.*",
        r".*datetime.*",
    ],

    "risk_level": [
        r"^risk$",
        r".*risk.*level.*",
        r".*risk.*category.*",
        r".*risk.*status.*",
        r".*risk.*class.*",
        r".*risk.*group.*",
    ],

    "systolic_bp": [
        r".*systolic.*",
        r".*sbp.*",
        r".*(bp|blood.*pressure).*systolic.*",
    ],

    "diastolic_bp": [
        r".*diastolic.*",
        r".*dbp.*",
        r".*(bp|blood.*pressure).*diastolic.*",
    ],

    "heart_rate": [
        r".*(heart.*rate|heartrate).*",
        r"^hr.*",
        r".*pulse.*",
        r".*bpm.*",
    ],

    "spo2": [
        r".*spo2.*",
        r".*sp.*o2.*",
        r".*oxygen.*saturation.*",
        r".*o2.*sat.*",
        r".*oxygen.*level.*",
    ],

    "respiratory_rate": [
        r".*(respiratory|respiration).*rate.*",
        r".*breathing.*rate.*",
        r"^rr.*",
        r".*breaths.*minute.*",
    ],

    "temperature": [
        r".*temperature.*",
        r".*body.*temp.*",
        r"^temp.*",
    ],

    "glucose": [
        r".*glucose.*",
        r".*blood.*sugar.*",
        r".*blood.*glucose.*",
        r".*serum.*glucose.*",
    ],

    "hba1c": [
        r".*hba1c.*",
        r".*hb.*a1c.*",
        r".*glycated.*hemoglobin.*",
        r".*glycosylated.*hemoglobin.*",
        r".*hemoglobin.*a1c.*",
        r".*haemoglobin.*a1c.*",
        r"^a1c.*",
    ],

    "cholesterol": [
        r".*cholesterol.*",
    ],

    "wbc": [
        r"^wbc.*",
        r".*white.*blood.*cell.*",
        r".*leukocyte.*",
    ],

    "height_cm": [
        r".*height.*",
    ],

    "weight_kg": [
        r".*weight.*",
        r".*body.*weight.*",
    ],

    "bmi": [
        r"^bmi.*",
        r".*body.*mass.*index.*",
    ],

    "diabetes": [
        r".*diabet.*",
    ],

    "hypertension": [
        r".*hypertension.*",
        r".*high.*blood.*pressure.*",
    ],

    "heart_disease": [
        r".*heart.*disease.*",
        r".*cardiac.*disease.*",
        r".*cardiovascular.*disease.*",
        r".*heart.*condition.*",
    ],

    "asthma": [
        r".*asthma.*",
    ],

    "kidney_disease": [
        r".*kidney.*disease.*",
        r".*renal.*disease.*",
    ],

    "smoking_status": [
        r".*smok.*",
        r".*tobacco.*",
    ],

    "visit_type": [
        r".*visit.*type.*",
        r".*encounter.*type.*",
        r".*appointment.*type.*",
    ],

    "department": [
        r".*department.*",
        r".*dept.*",
        r".*clinic.*",
        r".*specialty.*",
    ],

    "diagnosis": [
        r".*diagnos.*",
        r".*medical.*condition.*",
        r"^condition$",
    ],

    "medication": [
        r".*medication.*",
        r".*medicine.*",
        r".*drug.*",
        r".*prescription.*",
    ],

    "allergies": [
        r".*allerg.*",
    ],
}


# ============================================================
# Normalize Column Name
# ============================================================

def normalize_column_name(column_name: str) -> str:
    """
    Normalize a raw CSV column name.

    Examples
    --------
    Patient_ID
        -> patient id

    Heart-Rate
        -> heart rate

    SpO₂
        -> spo2

    BP_Systolic
        -> bp systolic
    """

    value = str(column_name).strip().lower()

    # Medical notation
    value = value.replace("spo₂", "spo2")
    value = value.replace("o₂", "o2")
    value = value.replace("°", "")

    # Underscore, hyphen and symbols become spaces.
    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# Compact Column Name
# ============================================================

def compact_column_name(column_name: str) -> str:
    """
    Return a compact normalized representation.

    Examples
    --------
    Systolic_BP
        -> systolicbp

    Heart-Rate
        -> heartrate
    """

    return normalize_column_name(
        column_name
    ).replace(" ", "")


# ============================================================
# Build Normalized Alias Lookup
# ============================================================

def build_alias_lookup() -> dict[str, str]:
    """
    Build:

        normalized alias -> canonical field

    Raises ValueError if an alias is ambiguous.
    """

    lookup: dict[str, str] = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            normalized_alias = normalize_column_name(
                alias
            )

            if not normalized_alias:
                continue

            existing_mapping = lookup.get(
                normalized_alias
            )

            if (
                existing_mapping is not None
                and existing_mapping != canonical_name
            ):
                raise ValueError(
                    "Ambiguous healthcare column alias "
                    f"'{alias}' maps to both "
                    f"'{existing_mapping}' and "
                    f"'{canonical_name}'."
                )

            lookup[normalized_alias] = canonical_name

    return lookup


# ============================================================
# Build Compact Alias Lookup
# ============================================================

def build_compact_alias_lookup() -> dict[str, str]:
    """
    Build:

        compact alias -> canonical field

    Used for cases such as:

        Heart Rate
        Heart_Rate
        Heart-Rate
        HeartRate

    """

    lookup: dict[str, str] = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            compact_alias = compact_column_name(
                alias
            )

            if not compact_alias:
                continue

            existing_mapping = lookup.get(
                compact_alias
            )

            if (
                existing_mapping is not None
                and existing_mapping != canonical_name
            ):
                # Ambiguous compact aliases are ignored.
                continue

            lookup[compact_alias] = canonical_name

    return lookup


# ============================================================
# Column Value Profile
# ============================================================

def _column_profile(
    series: pd.Series,
) -> dict[str, float]:
    """
    Create a lightweight profile used during schema detection.

    Returns:
        numeric_ratio
        date_ratio
        non_empty_ratio
        unique_ratio
    """

    if series is None:
        return {
            "numeric_ratio": 0.0,
            "date_ratio": 0.0,
            "non_empty_ratio": 0.0,
            "unique_ratio": 0.0,
        }

    values = series.dropna()

    if values.empty:
        return {
            "numeric_ratio": 0.0,
            "date_ratio": 0.0,
            "non_empty_ratio": 0.0,
            "unique_ratio": 0.0,
        }

    text_values = (
        values.astype("string")
        .str.strip()
    )

    non_empty = text_values[
        text_values != ""
    ].dropna()

    if non_empty.empty:
        return {
            "numeric_ratio": 0.0,
            "date_ratio": 0.0,
            "non_empty_ratio": 0.0,
            "unique_ratio": 0.0,
        }

    numeric_values = pd.to_numeric(
        non_empty,
        errors="coerce",
    )

    numeric_ratio = float(
        numeric_values.notna().mean()
    )

    # "mixed" handles real CSVs containing both dates and
    # timestamps more reliably.
    try:
        date_values = pd.to_datetime(
            non_empty,
            errors="coerce",
            format="mixed",
        )
    except (TypeError, ValueError):
        date_values = pd.to_datetime(
            non_empty,
            errors="coerce",
        )

    date_ratio = float(
        date_values.notna().mean()
    )

    unique_ratio = float(
        non_empty.nunique(
            dropna=True
        )
        / len(non_empty)
    )

    return {
        "numeric_ratio": numeric_ratio,
        "date_ratio": date_ratio,
        "non_empty_ratio": float(
            len(non_empty) / len(values)
        ),
        "unique_ratio": unique_ratio,
    }


# ============================================================
# Heuristic Score
# ============================================================

def _heuristic_score(
    raw_column: str,
    canonical_name: str,
) -> int:
    """
    Calculate a semantic name-match score.

    Higher score = stronger evidence.
    """

    normalized = normalize_column_name(
        raw_column
    )

    compact = normalized.replace(
        " ",
        "",
    )

    patterns = HEURISTIC_PATTERNS.get(
        canonical_name,
        [],
    )

    score = 0

    for pattern in patterns:

        if re.fullmatch(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        ):
            score = max(score, 80)

        elif re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        ):
            score = max(score, 60)

    canonical_compact = canonical_name.replace(
        "_",
        "",
    )

    if compact == canonical_compact:
        score = max(score, 90)

    return score


# ============================================================
# Candidate Validation
# ============================================================

def _is_plausible_candidate(
    df: pd.DataFrame,
    raw_column: str,
    canonical_name: str,
) -> bool:
    """
    Check whether a detected column is broadly compatible
    with the expected healthcare field.

    This is schema validation only. It does not perform
    clinical interpretation.
    """

    if raw_column not in df.columns:
        return False

    profile = _column_profile(
        df[raw_column]
    )

    numeric_ratio = float(
        profile["numeric_ratio"]
    )

    date_ratio = float(
        profile["date_ratio"]
    )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    if canonical_name in NUMERIC_CANONICAL_FIELDS:

        return numeric_ratio >= 0.50

    # --------------------------------------------------------
    # Date/time field
    # --------------------------------------------------------

    if canonical_name == "visit_date":

        return date_ratio >= 0.50

    # --------------------------------------------------------
    # Patient ID
    # --------------------------------------------------------

    if canonical_name == "patient_id":

        series = (
            df[raw_column]
            .astype("string")
            .str.strip()
        )

        non_empty = series[
            series != ""
        ].dropna()

        if non_empty.empty:
            return False

        # Patient IDs can be:
        # P001
        # PT-1001
        # 1001
        # MRN-5002
        #
        # Therefore no numeric/date restriction is applied.
        return True

    # --------------------------------------------------------
    # Text / categorical fields
    # --------------------------------------------------------

    return True


# ============================================================
# Detect Columns
# ============================================================

def detect_columns(
    df: pd.DataFrame,
) -> dict[str, str]:
    """
    Detect healthcare fields from an uploaded CSV.

    Detection priority:

    1. Exact normalized alias
    2. Compact alias
    3. Conservative heuristic matching
    4. Basic value/type validation

    Returns
    -------
    dict[str, str]
        {
            "Patient_ID": "patient_id",
            "Heart_Rate": "heart_rate",
            ...
        }

    Unknown columns are never removed.
    """

    if df is None:
        return {}

    if df.empty and len(df.columns) == 0:
        return {}

    if len(df.columns) == 0:
        return {}

    alias_lookup = build_alias_lookup()
    compact_lookup = build_compact_alias_lookup()

    detected_columns: dict[str, str] = {}
    detected_canonical: dict[str, str] = {}

    # ========================================================
    # Pass 1: Exact normalized aliases
    # ========================================================

    for raw_column in df.columns:

        raw_name = str(raw_column)

        normalized_column = normalize_column_name(
            raw_name
        )

        canonical_name = alias_lookup.get(
            normalized_column
        )

        if canonical_name is None:
            continue

        if canonical_name in detected_canonical:
            continue

        if not _is_plausible_candidate(
            df,
            raw_name,
            canonical_name,
        ):
            continue

        detected_columns[
            raw_name
        ] = canonical_name

        detected_canonical[
            canonical_name
        ] = raw_name

    # ========================================================
    # Pass 2: Compact aliases
    # ========================================================

    for raw_column in df.columns:

        raw_name = str(raw_column)

        if raw_name in detected_columns:
            continue

        compact_name = compact_column_name(
            raw_name
        )

        canonical_name = compact_lookup.get(
            compact_name
        )

        if canonical_name is None:
            continue

        if canonical_name in detected_canonical:
            continue

        if not _is_plausible_candidate(
            df,
            raw_name,
            canonical_name,
        ):
            continue

        detected_columns[
            raw_name
        ] = canonical_name

        detected_canonical[
            canonical_name
        ] = raw_name

    # ========================================================
    # Pass 3: Heuristic Detection
    # ========================================================

    remaining_columns = [
        str(column)
        for column in df.columns
        if str(column)
        not in detected_columns
    ]

    heuristic_candidates: list[
        tuple[int, str, str]
    ] = []

    for raw_column in remaining_columns:

        for canonical_name in COLUMN_ALIASES:

            if canonical_name in detected_canonical:
                continue

            score = _heuristic_score(
                raw_column,
                canonical_name,
            )

            # Conservative threshold.
            if score < 60:
                continue

            if not _is_plausible_candidate(
                df,
                raw_column,
                canonical_name,
            ):
                continue

            heuristic_candidates.append(
                (
                    score,
                    raw_column,
                    canonical_name,
                )
            )

    # Strongest semantic matches first.
    heuristic_candidates.sort(
        key=lambda item: (
            -item[0],
            item[1].lower(),
        )
    )

    for (
        score,
        raw_column,
        canonical_name,
    ) in heuristic_candidates:

        if raw_column in detected_columns:
            continue

        if canonical_name in detected_canonical:
            continue

        detected_columns[
            raw_column
        ] = canonical_name

        detected_canonical[
            canonical_name
        ] = raw_column

    return detected_columns


# ============================================================
# Missing Required Fields
# ============================================================

def get_missing_required_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return required canonical fields missing from the dataset.

    Currently patient_id is the only required field.
    """

    if df is None:
        return sorted(
            REQUIRED_CANONICAL_COLUMNS
        )

    detected_columns = detect_columns(
        df
    )

    detected_canonical = set(
        detected_columns.values()
    )

    return sorted(
        REQUIRED_CANONICAL_COLUMNS
        - detected_canonical
    )


# ============================================================
# Available Canonical Fields
# ============================================================

def get_available_canonical_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return recognized healthcare fields available
    in the uploaded dataset.
    """

    if df is None:
        return []

    detected_columns = detect_columns(
        df
    )

    return sorted(
        set(
            detected_columns.values()
        )
    )


# ============================================================
# Available Trend Fields
# ============================================================

def get_available_trend_fields(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return vital/measurement fields available for
    patient-level trend charts.
    """

    if df is None:
        return []

    available_fields = set(
        get_available_canonical_columns(df)
    )

    return [
        field
        for field in (
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
        )
        if field in available_fields
    ]


# ============================================================
# Missing Optional Fields
# ============================================================

def get_missing_optional_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return known optional healthcare fields that are not
    present in the uploaded dataset.

    Informational only.
    """

    if df is None:
        return sorted(
            OPTIONAL_CANONICAL_COLUMNS
        )

    detected_columns = detect_columns(
        df
    )

    detected_canonical = set(
        detected_columns.values()
    )

    return sorted(
        OPTIONAL_CANONICAL_COLUMNS
        - detected_canonical
    )


# ============================================================
# Unmapped / Additional Columns
# ============================================================

def get_unmapped_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return raw CSV columns that were not recognized.

    Unknown columns are preserved and are not treated as
    an error.
    """

    if df is None:
        return []

    detected_columns = detect_columns(
        df
    )

    detected_raw_columns = set(
        detected_columns.keys()
    )

    return [
        str(column)
        for column in df.columns
        if str(column)
        not in detected_raw_columns
    ]


# ============================================================
# Apply Column Mapping
# ============================================================

def apply_column_mapping(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rename recognized healthcare columns to canonical names.

    Example
    -------
    Patient_ID
        -> patient_id

    Heart_Rate
        -> heart_rate

    Unknown/additional columns are preserved.

    No values are fabricated.
    No missing columns are created.
    """

    if df is None:
        return pd.DataFrame()

    detected_columns = detect_columns(
        df
    )

    if not detected_columns:
        return df.copy()

    normalized_df = df.rename(
        columns=detected_columns
    ).copy()

    return normalized_df