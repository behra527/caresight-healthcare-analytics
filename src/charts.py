from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


# ============================================================
# Configuration
# ============================================================

TREND_FIELDS = [
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


FIELD_LABELS = {
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "heart_rate": "Heart Rate",
    "spo2": "SpO2",
    "respiratory_rate": "Respiratory Rate",
    "temperature": "Temperature",
    "glucose": "Glucose",
    "hba1c": "HbA1c",
    "cholesterol": "Cholesterol",
    "wbc": "WBC",
    "bmi": "BMI",
    "weight_kg": "Weight",
}


FIELD_UNITS = {
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
    "heart_rate": "bpm",
    "spo2": "%",
    "respiratory_rate": "breaths/min",
    "temperature": "°C / °F",
    "glucose": "mg/dL",
    "hba1c": "%",
    "cholesterol": "mg/dL",
    "wbc": "count",
    "bmi": "kg/m²",
    "weight_kg": "kg",
}


# ============================================================
# Display Helpers
# ============================================================

def _format_field_name(
    field_name: str,
) -> str:
    """
    Convert a canonical field name into a readable label.
    """

    if field_name in FIELD_LABELS:
        return FIELD_LABELS[field_name]

    return (
        str(field_name)
        .replace("_", " ")
        .replace("-", " ")
        .strip()
        .title()
    )


def _get_field_unit(
    field_name: str,
) -> str:
    """
    Return the display unit for a known healthcare field.
    """

    return FIELD_UNITS.get(
        field_name,
        "",
    )


# ============================================================
# Chart Data Preparation
# ============================================================

def _prepare_trend_data(
    patient_df: pd.DataFrame,
    fields: list[str],
) -> pd.DataFrame:
    """
    Prepare patient time-series data for charting.

    Invalid dates and invalid numeric observations are removed.
    """

    if (
        patient_df is None
        or patient_df.empty
        or "visit_date" not in patient_df.columns
    ):
        return pd.DataFrame()

    valid_fields = [
        field
        for field in fields
        if field in patient_df.columns
    ]

    if not valid_fields:
        return pd.DataFrame()

    columns = [
        "visit_date",
        *valid_fields,
    ]

    chart_df = patient_df[
        columns
    ].copy()

    chart_df["visit_date"] = pd.to_datetime(
        chart_df["visit_date"],
        errors="coerce",
    )

    for field in valid_fields:

        chart_df[field] = pd.to_numeric(
            chart_df[field],
            errors="coerce",
        )

    chart_df = chart_df.dropna(
        subset=["visit_date"]
    )

    if chart_df.empty:
        return pd.DataFrame()

    chart_df = chart_df.sort_values(
        "visit_date",
        kind="stable",
    )

    return chart_df.reset_index(
        drop=True
    )


# ============================================================
# Empty Figure
# ============================================================

def create_empty_chart(
    title: str = "No chart data available",
    message: str = "Required data is not available.",
) -> go.Figure:
    """
    Create an informational Plotly figure for unavailable
    or insufficient chart data.
    """

    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=14,
        ),
    )

    fig.update_layout(
        title=dict(
            text=title,
            x=0,
        ),
        xaxis=dict(
            visible=False,
        ),
        yaxis=dict(
            visible=False,
        ),
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20,
        ),
        height=340,
    )

    return fig


# ============================================================
# Common Chart Layout
# ============================================================

def _apply_chart_layout(
    fig: go.Figure,
    title: str,
    yaxis_title: str,
) -> go.Figure:
    """
    Apply consistent dashboard chart layout.
    """

    fig.update_layout(
        title=dict(
            text=title,
            x=0,
            xanchor="left",
        ),
        xaxis=dict(
            title="Visit Date",
            showgrid=True,
            type="date",
        ),
        yaxis=dict(
            title=yaxis_title,
            showgrid=True,
        ),
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20,
        ),
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    return fig


# ============================================================
# Single Vital Trend Chart
# ============================================================

def create_vital_trend_chart(
    patient_df: pd.DataFrame,
    vital: str,
    title: str | None = None,
) -> go.Figure:
    """
    Create a time-series chart for one patient measurement.

    Requirements
    ------------
    - visit_date must exist
    - selected field must exist
    - valid numeric measurements must exist

    No values are calculated or fabricated.
    """

    # --------------------------------------------------------
    # Validate DataFrame
    # --------------------------------------------------------

    if patient_df is None or patient_df.empty:

        return create_empty_chart(
            title=title or "Vital Trend",
            message="No patient records available.",
        )

    # --------------------------------------------------------
    # Validate field
    # --------------------------------------------------------

    if (
        not isinstance(vital, str)
        or not vital.strip()
    ):

        return create_empty_chart(
            title=title or "Vital Trend",
            message="No measurement field was selected.",
        )

    vital = vital.strip()

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    chart_df = _prepare_trend_data(
        patient_df,
        [vital],
    )

    if chart_df.empty:

        return create_empty_chart(
            title=title or "Vital Trend",
            message=(
                f"No valid {_format_field_name(vital).lower()} "
                "measurements are available."
            ),
        )

    # --------------------------------------------------------
    # Remove missing measurement values
    # --------------------------------------------------------

    chart_df = chart_df.dropna(
        subset=[vital]
    )

    if chart_df.empty:

        return create_empty_chart(
            title=title or "Vital Trend",
            message=(
                f"No valid {_format_field_name(vital).lower()} "
                "measurements are available."
            ),
        )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    display_name = _format_field_name(
        vital
    )

    unit = _get_field_unit(
        vital
    )

    chart_title = (
        title
        if title
        else f"{display_name} Trend"
    )

    yaxis_title = (
        f"{display_name} ({unit})"
        if unit
        else display_name
    )

    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["visit_date"],
            y=chart_df[vital],
            mode="lines+markers",
            name=display_name,
            line=dict(
                width=2,
            ),
            marker=dict(
                size=7,
            ),
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b>"
                "<br>"
                f"{display_name}: "
                "%{y:.2f}"
                + (
                    f" {unit}"
                    if unit
                    else ""
                )
                + "<extra></extra>"
            ),
            connectgaps=False,
        )
    )

    return _apply_chart_layout(
        fig=fig,
        title=chart_title,
        yaxis_title=yaxis_title,
    )


# ============================================================
# Blood Pressure Trend Chart
# ============================================================

def create_blood_pressure_chart(
    patient_df: pd.DataFrame,
) -> go.Figure:
    """
    Create a combined systolic/diastolic blood pressure
    trend chart.

    If only one blood-pressure measurement exists, only that
    measurement is displayed.
    """

    available_fields = [
        field
        for field in [
            "systolic_bp",
            "diastolic_bp",
        ]
        if (
            patient_df is not None
            and field in patient_df.columns
        )
    ]

    if not available_fields:

        return create_empty_chart(
            title="Blood Pressure Trend",
            message=(
                "Blood pressure measurements are "
                "not available."
            ),
        )

    chart_df = _prepare_trend_data(
        patient_df,
        available_fields,
    )

    if chart_df.empty:

        return create_empty_chart(
            title="Blood Pressure Trend",
            message=(
                "No valid blood pressure observations "
                "are available."
            ),
        )

    fig = go.Figure()

    for field in available_fields:

        field_df = chart_df.dropna(
            subset=[field]
        )

        if field_df.empty:
            continue

        display_name = _format_field_name(
            field
        )

        fig.add_trace(
            go.Scatter(
                x=field_df["visit_date"],
                y=field_df[field],
                mode="lines+markers",
                name=display_name,
                line=dict(
                    width=2,
                ),
                marker=dict(
                    size=7,
                ),
                hovertemplate=(
                    "<b>%{x|%d %b %Y}</b>"
                    "<br>"
                    f"{display_name}: "
                    "%{y:.1f} mmHg"
                    "<extra></extra>"
                ),
                connectgaps=False,
            )
        )

    if not fig.data:

        return create_empty_chart(
            title="Blood Pressure Trend",
            message=(
                "No valid blood pressure observations "
                "are available."
            ),
        )

    return _apply_chart_layout(
        fig=fig,
        title="Blood Pressure Trend",
        yaxis_title="Blood Pressure (mmHg)",
    )


# ============================================================
# Available Trend Fields
# ============================================================

def get_available_trend_fields(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return available healthcare measurements that contain
    at least one valid numeric observation.

    Only supported healthcare trend fields are returned.
    """

    if df is None or df.empty:
        return []

    available_fields = []

    for field in TREND_FIELDS:

        if field not in df.columns:
            continue

        numeric_values = pd.to_numeric(
            df[field],
            errors="coerce",
        )

        if numeric_values.notna().any():

            available_fields.append(
                field
            )

    return available_fields


# ============================================================
# Create Multiple Vital Charts
# ============================================================

def create_vital_charts(
    patient_df: pd.DataFrame,
    vitals: list[str] | None = None,
) -> dict[str, go.Figure]:
    """
    Create multiple patient vital trend charts.

    Blood pressure is combined into one chart when either
    systolic or diastolic BP is requested.

    Other measurements receive individual charts.

    Missing/invalid fields are skipped safely.
    """

    charts: dict[str, go.Figure] = {}

    if (
        patient_df is None
        or patient_df.empty
    ):
        return charts

    available_fields = get_available_trend_fields(
        patient_df
    )

    if vitals is None:

        selected_fields = available_fields

    else:

        selected_fields = [
            field
            for field in vitals
            if field in available_fields
        ]

    if not selected_fields:
        return charts

    # --------------------------------------------------------
    # Blood pressure
    # --------------------------------------------------------

    blood_pressure_fields = {
        "systolic_bp",
        "diastolic_bp",
    }

    requested_bp = (
        blood_pressure_fields
        & set(selected_fields)
    )

    if requested_bp:

        charts["blood_pressure"] = (
            create_blood_pressure_chart(
                patient_df
            )
        )

    # --------------------------------------------------------
    # Individual measurements
    # --------------------------------------------------------

    for field in selected_fields:

        if field in blood_pressure_fields:
            continue

        charts[field] = (
            create_vital_trend_chart(
                patient_df=patient_df,
                vital=field,
            )
        )

    return charts


# ============================================================
# Create All Available Clinical Charts
# ============================================================

def create_patient_trend_charts(
    patient_df: pd.DataFrame,
) -> dict[str, go.Figure]:
    """
    Create all supported clinical trend charts available
    for the selected patient.

    This is the main chart helper for the dashboard.
    """

    available_fields = get_available_trend_fields(
        patient_df
    )

    return create_vital_charts(
        patient_df=patient_df,
        vitals=available_fields,
    )