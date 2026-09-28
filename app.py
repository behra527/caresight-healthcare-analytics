from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    filter_by_risk,
    get_available_patient_fields,
    get_dashboard_metrics,
    get_latest_patient_record,
    get_patient_date_range,
    get_patient_demographics,
    get_patient_records,
    get_patient_summary,
    get_patient_visit_count,
    search_patients,
)
from src.charts import (
    create_patient_trend_charts,
)
from src.data_loader import (
    load_csv,
)
from src.schema import (
    apply_column_mapping,
)
from src.validation import (
    get_data_quality_report,
    normalize_data,
    validate_data_quality,
)

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="CareSight Healthcare Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom Ultra-Clean SaaS UI Theme
# ============================================================

st.markdown(
    """
    <!-- Font Awesome CDN for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        /* Global Styling */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #0F172A !important;
        }

        .stApp {
            background-color: #F8FAFC !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
            padding-top: 1rem;
        }

        /* Premium Brand Box in Sidebar */
        .sidebar-brand-card {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-radius: 12px;
            padding: 1.25rem 1rem;
            margin-bottom: 1.5rem;
            color: #FFFFFF;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sidebar-brand-icon {
            background: rgba(2, 132, 199, 0.2);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            flex-shrink: 0;
        }

        .sidebar-brand-text {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .sidebar-brand-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }

        /* Section Title in Sidebar */
        .sidebar-section-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Hero Banner */
        .hero-container {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #0369A1 100%);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            color: #FFFFFF;
        }

        .dashboard-title {
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.4rem;
            color: #FFFFFF;
        }

        .dashboard-subtitle {
            color: #94A3B8;
            font-size: 0.9rem;
            font-weight: 400;
            line-height: 1.5;
        }

        /* Section Headers */
        .section-header {
            font-size: 1.1rem;
            font-weight: 800;
            color: #0F172A;
            margin-top: 1.25rem;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-header::before {
            content: "";
            display: inline-block;
            width: 4px;
            height: 18px;
            background: #0284C7;
            border-radius: 2px;
        }

        /* Metrics Overhaul */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 1rem 1.25rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        div[data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
        }

        /* Patient Card Styling */
        .patient-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #0284C7;
            border-radius: 10px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
        }

        .patient-name {
            font-size: 1.35rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.75rem;
        }

        .patient-meta-pills {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }

        .pill {
            background-color: #F1F5F9;
            color: #334155;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1px solid #E2E8F0;
            display: inline-block;
            line-height: 1.2;
        }

        .pill-primary {
            background-color: #E0F2FE;
            color: #0369A1;
            border-color: #BAE6FD;
        }

        .pill-high {
            background-color: #FEF2F2;
            color: #DC2626;
            border-color: #FCA5A5;
        }

        .pill-medium {
            background-color: #FFFBEB;
            color: #D97706;
            border-color: #FCD34D;
        }

        .pill-low {
            background-color: #ECFDF5;
            color: #059669;
            border-color: #6EE7B7;
        }

        .pill-alert {
            background-color: #FEF2F2;
            color: #991B1B;
            border: 1px solid #F87171;
            font-weight: 700;
        }

        /* Clean Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #E2E8F0;
        }

        .stTabs [data-baseweb="tab"] {
            font-weight: 700 !important;
            font-size: 0.88rem !important;
            color: #64748B !important;
            padding: 8px 16px !important;
        }

        .stTabs [aria-selected="true"] {
            color: #0284C7 !important;
            border-bottom: 2px solid #0284C7 !important;
            background-color: transparent !important;
        }

        .sub-header {
            font-size: 0.82rem;
            font-weight: 800;
            color: #475569;
            margin-top: 1.25rem;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Field Labels Mapping
# ============================================================

FIELD_LABELS = {
    "patient_id": "Patient ID",
    "patient_name": "Patient Name",
    "age": "Age",
    "gender": "Gender",
    "blood_group": "Blood Group",
    "visit_date": "Visit Date",
    "risk_level": "Risk Stratification",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "heart_rate": "Heart Rate (BPM)",
    "spo2": "SpO2 (%)",
    "respiratory_rate": "Respiratory Rate",
    "temperature": "Temperature (°F)",
    "glucose": "Blood Glucose",
    "hba1c": "HbA1c (%)",
    "cholesterol": "Cholesterol",
    "wbc": "WBC Count",
    "height_cm": "Height (cm)",
    "weight_kg": "Weight (kg)",
    "bmi": "BMI Index",
    "diabetes": "Diabetes",
    "hypertension": "Hypertension",
    "heart_disease": "Heart Disease",
    "asthma": "Asthma",
    "kidney_disease": "Kidney Disease",
    "smoking_status": "Smoking Status",
    "visit_type": "Encounter Type",
    "department": "Department",
    "diagnosis": "Primary Diagnosis",
    "medication": "Prescribed Medication",
    "allergies": "Known Allergies",
}


def format_field_name(field_name: str) -> str:
    if field_name in FIELD_LABELS:
        return FIELD_LABELS[field_name]
    return str(field_name).replace("_", " ").replace("-", " ").strip().title()


def format_value(value, field_key: str = "") -> str:
    if value is None:
        return "N/A"
    try:
        if pd.isna(value):
            return "N/A"
    except (TypeError, ValueError):
        pass

    if field_key == "temperature":
        try:
            val_float = float(value)
            if val_float <= 45.0:
                val_float = (val_float * 9 / 5) + 32
            return f"{val_float:.1f}"
        except (ValueError, TypeError):
            pass

    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def format_metric_value(value) -> str:
    if value is None:
        return "N/A"
    try:
        if pd.isna(value):
            return "N/A"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def apply_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family="Plus Jakarta Sans", color="#0F172A"),
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            title_font=dict(size=11, color="#64748B"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            title_font=dict(size=11, color="#64748B"),
        ),
    )
    fig.update_traces(line=dict(width=2.5, color="#0284C7"))
    return fig


def check_critical_vitals(latest_row: pd.Series) -> list[str]:
    alerts = []
    try:
        if "systolic_bp" in latest_row and pd.notna(latest_row["systolic_bp"]):
            if float(latest_row["systolic_bp"]) >= 140:
                alerts.append(f"High BP ({latest_row['systolic_bp']} mmHg)")
        if "heart_rate" in latest_row and pd.notna(latest_row["heart_rate"]):
            if float(latest_row["heart_rate"]) >= 100:
                alerts.append(f"Tachycardia ({latest_row['heart_rate']} BPM)")
        if "spo2" in latest_row and pd.notna(latest_row["spo2"]):
            if float(latest_row["spo2"]) <= 92:
                alerts.append(f"Low SpO2 ({latest_row['spo2']}%)")
    except (ValueError, TypeError):
        pass
    return alerts


# ============================================================
# Sidebar Data Controls
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-icon">
                <i class="fa-solid fa-stethoscope"></i>
            </div>
            <div class="sidebar-brand-text">
                <div class="sidebar-brand-title">CareSight</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section-label"><i class="fa-solid fa-file-csv"></i> Data Source</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload Clinical Dataset (CSV)",
        type=["csv"],
    )

    st.divider()

    use_demo_data = st.checkbox(
        "Use demo patient dataset",
        value=uploaded_file is None,
    )

# ============================================================
# Dataset Loading & Dynamic Mapping
# ============================================================

df: pd.DataFrame | None = None

if uploaded_file is not None:
    try:
        raw_uploaded_df = load_csv(uploaded_file)
        df = apply_column_mapping(raw_uploaded_df)
    except Exception as exc:
        st.error(f"Error loading file: {exc}")
        st.stop()

elif use_demo_data:
    try:
        demo_path = "data/sample_patients.csv"
        raw_demo_df = pd.read_csv(demo_path, keep_default_na=False)
        df = apply_column_mapping(raw_demo_df)
    except Exception as exc:
        st.error(f"Error loading demo dataset: {exc}")
        st.stop()
else:
    st.info("Upload dataset or activate demo dataset.")
    st.stop()

# Auto-detect Risk Column if not mapped directly
risk_col = None
possible_risk_cols = ["risk_level", "risk", "risk_category", "risklevel"]
for col in df.columns:
    if col.lower().strip() in possible_risk_cols:
        risk_col = col
        break

if risk_col and risk_col != "risk_level":
    df["risk_level"] = df[risk_col]

# ============================================================
# Data Normalization & Quality Checks
# ============================================================

df = normalize_data(df)
quality_result = validate_data_quality(df)

if not quality_result["is_valid"]:
    st.error("Validation failed.")
    for err in quality_result["errors"]:
        st.error(err)
    st.stop()

# ============================================================
# Executive Hero Banner
# ============================================================

st.markdown(
    """
    <div class="hero-container">
        <div class="dashboard-title">Clinical & Patient Health Intelligence</div>
        <div class="dashboard-subtitle">
            Real-time population health monitoring, vital signs analytics, and clinical risk stratification platform.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Tabbed Main Navigation
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Dashboard",
        "Population Registry",
        "Patient Deep-Dive",
        "Data Integrity Audit",
    ]
)

dashboard_metrics = get_dashboard_metrics(df)
has_patient_id = (
    "patient_id" in df.columns
    and dashboard_metrics["total_patients"] is not None
)
has_risk = "risk_level" in df.columns and df["risk_level"].dropna().shape[0] > 0

# ------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ------------------------------------------------------------
with tab1:
    st.markdown(
        '<div class="section-header">Population Metrics</div>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(5 if has_risk else 2)

    with metric_columns[0]:
        st.metric(
            "Total Patients",
            (
                format_metric_value(dashboard_metrics["total_patients"])
                if has_patient_id
                else "N/A"
            ),
        )

    with metric_columns[1]:
        st.metric(
            "Total Encounters",
            format_metric_value(dashboard_metrics["total_visits"]),
        )

    if has_risk:
        with metric_columns[2]:
            st.metric(
                "High Risk Patients",
                format_metric_value(dashboard_metrics["high_risk_patients"]),
            )
        with metric_columns[3]:
            st.metric(
                "Medium Risk Patients",
                format_metric_value(
                    dashboard_metrics["medium_risk_patients"]
                ),
            )
        with metric_columns[4]:
            st.metric(
                "Low Risk Patients",
                format_metric_value(dashboard_metrics["low_risk_patients"]),
            )

        st.markdown(
            '<div class="sub-header">Risk Stratification Breakdown</div>',
            unsafe_allow_html=True,
        )

        risk_series = df["risk_level"].dropna().astype(str).str.strip().str.title()
        risk_counts = risk_series.value_counts().reset_index()
        risk_counts.columns = ["Risk Category", "Count"]

        if not risk_counts.empty:
            col_chart, _ = st.columns([2, 1])
            with col_chart:
                color_map = {
                    "High Risk": "#EF4444",
                    "High": "#EF4444",
                    "Medium Risk": "#F59E0B",
                    "Medium": "#F59E0B",
                    "Low Risk": "#10B981",
                    "Low": "#10B981",
                }
                fig_risk = px.pie(
                    risk_counts,
                    names="Risk Category",
                    values="Count",
                    hole=0.5,
                    color="Risk Category",
                    color_discrete_map=color_map,
                )
                fig_risk.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font=dict(family="Plus Jakarta Sans", color="#0F172A"),
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("No valid risk categories found in the uploaded file.")
    else:
        st.info("Upload a dataset with a 'risk_level' column to view Risk Breakdown.")

# ------------------------------------------------------------
# TAB 2: POPULATION REGISTRY
# ------------------------------------------------------------
with tab2:
    st.markdown(
        '<div class="section-header">Filter & Search Engine</div>',
        unsafe_allow_html=True,
    )

    filter_cols = st.columns(2)

    if has_risk:
        with filter_cols[0]:
            risk_values = (
                df["risk_level"].dropna().astype("string").str.strip().tolist()
            )
            observed_risks = sorted(set(risk_values))
            risk_options = ["All Risk Categories"] + observed_risks
            selected_risk_input = st.selectbox(
                "Filter by Risk Level", risk_options
            )
            selected_risk = (
                "All"
                if selected_risk_input == "All Risk Categories"
                else selected_risk_input
            )
    else:
        selected_risk = "All"

    with filter_cols[1]:
        search_term = st.text_input(
            "Search Registry", placeholder="Search by Patient ID or Name..."
        )

    filtered_df = filter_by_risk(df, selected_risk)
    if search_term.strip():
        filtered_df = search_patients(filtered_df, search_term.strip())

    st.markdown(
        '<div class="section-header">Patient Population Table</div>',
        unsafe_allow_html=True,
    )

    summary_df = get_patient_summary(filtered_df)

    if summary_df.empty:
        st.info("No clinical records match the specified search/filter criteria.")
    else:
        display_summary = summary_df.rename(
            columns={col: format_field_name(col) for col in summary_df.columns}
        )
        st.dataframe(display_summary, use_container_width=True, hide_index=True)

        csv_data = display_summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Filtered Registry (CSV)",
            data=csv_data,
            file_name="patient_registry_export.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------
# TAB 3: PATIENT DEEP-DIVE
# ------------------------------------------------------------
with tab3:
    if has_patient_id:
        patient_series = (
            df["patient_id"].astype("string").str.strip().dropna()
        )
        patient_ids = sorted(set(patient_series))

        if patient_ids:
            st.markdown(
                '<div class="section-header">Select Clinical Record</div>',
                unsafe_allow_html=True,
            )

            selected_patient = st.selectbox("Search Patient ID", patient_ids)
            patient_df = get_patient_records(df, selected_patient)
            latest_record = get_latest_patient_record(df, selected_patient)

            if not latest_record.empty:
                latest = latest_record.iloc[0]
                patient_name = format_value(
                    latest.get("patient_name", "Patient")
                )
                visit_count = get_patient_visit_count(df, selected_patient)
                date_range = get_patient_date_range(df, selected_patient)

                risk_level_val = str(latest.get("risk_level", "")).lower()
                risk_pill_class = "pill-primary"
                if "high" in risk_level_val:
                    risk_pill_class = "pill-high"
                elif "medium" in risk_level_val:
                    risk_pill_class = "pill-medium"
                elif "low" in risk_level_val:
                    risk_pill_class = "pill-low"

                date_text = "N/A"
                if date_range and pd.notna(date_range[0]):
                    date_text = (
                        f"{date_range[0]:%d %b %Y} – {date_range[1]:%d %b %Y}"
                    )

                critical_alerts = check_critical_vitals(latest)
                alert_html = ""
                if critical_alerts:
                    alert_html = f'<span class="pill pill-alert">Alert: {", ".join(critical_alerts)}</span>'

                risk_text = format_value(latest.get("risk_level", "Unassigned"))

                card_html = (
                    f'<div class="patient-card">'
                    f'<div class="patient-name">{patient_name}</div>'
                    f'<div class="patient-meta-pills">'
                    f'<span class="pill pill-primary">ID: {selected_patient}</span>'
                    f'<span class="pill {risk_pill_class}">Risk: {risk_text}</span>'
                    f'<span class="pill">Total Encounters: {visit_count}</span>'
                    f'<span class="pill">Active Span: {date_text}</span>'
                    f'{alert_html}'
                    f'</div></div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                demographics = get_patient_demographics(df, selected_patient)
                filtered_demographics = {
                    k: v
                    for k, v in demographics.items()
                    if k not in ["patient_id", "patient_name"]
                }

                if filtered_demographics:
                    st.markdown(
                        '<div class="sub-header">Patient Profile & Demographics</div>',
                        unsafe_allow_html=True,
                    )
                    demo_cols = st.columns(min(len(filtered_demographics), 4))
                    for idx, (field, val) in enumerate(filtered_demographics.items()):
                        with demo_cols[idx % len(demo_cols)]:
                            st.metric(
                                format_field_name(field), format_value(val, field)
                            )

                available_fields = get_available_patient_fields(df)
                available_vitals = [
                    f
                    for f in available_fields.get("vitals", [])
                    if f in latest.index
                ]

                if available_vitals:
                    st.markdown(
                        '<div class="sub-header">Recent Clinical Vitals</div>',
                        unsafe_allow_html=True,
                    )
                    vital_cols = st.columns(min(len(available_vitals), 4))
                    for idx, vital in enumerate(available_vitals):
                        with vital_cols[idx % len(vital_cols)]:
                            st.metric(
                                format_field_name(vital),
                                format_value(latest[vital], vital),
                            )

                st.markdown(
                    '<div class="sub-header">Longitudinal Clinical Trends</div>',
                    unsafe_allow_html=True,
                )
                trend_charts = create_patient_trend_charts(patient_df)
                if trend_charts:
                    chart_items = list(trend_charts.items())
                    for i in range(0, len(chart_items), 2):
                        c_cols = st.columns(2)
                        for offset in range(2):
                            if i + offset < len(chart_items):
                                ckey, chart = chart_items[i + offset]
                                themed_chart = apply_chart_theme(chart)
                                with c_cols[offset]:
                                    st.plotly_chart(
                                        themed_chart, use_container_width=True
                                    )
    else:
        st.info("Patient ID field not found in dataset.")

# ------------------------------------------------------------
# TAB 4: DATA INTEGRITY AUDIT
# ------------------------------------------------------------
with tab4:
    st.markdown(
        '<div class="section-header">Data Integrity & Audit Log</div>',
        unsafe_allow_html=True,
    )

    quality_report = get_data_quality_report(df)
    q_cols = st.columns(4)
    with q_cols[0]:
        st.metric("Total Records", f"{quality_report['rows']:,}")
    with q_cols[1]:
        st.metric("Tracked Attributes", f"{quality_report['columns']:,}")
    with q_cols[2]:
        st.metric("Duplicate Entries", f"{quality_report['duplicate_rows']:,}")
    with q_cols[3]:
        st.metric("Null Cells", f"{quality_report['missing_cells']:,}")