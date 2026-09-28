# Healthcare Patient Analytics

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64+-FF4B4B?logo=streamlit\&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-3.x-150458?logo=pandas\&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly\&logoColor=white)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-style Streamlit dashboard for analyzing healthcare patient records, clinical measurements, risk levels, patient history, and longitudinal trends.

## Features

* Healthcare CSV upload and demo dataset
* Automatic column mapping and schema recognition
* Data normalization and validation
* Patient search and risk-level filtering
* Clinical overview metrics
* Patient demographics and latest measurements
* Risk assessment
* Patient visit history
* Interactive clinical trend charts
* Data quality and validation reporting
* Responsive enterprise-style dashboard UI

## Tech Stack

* Python
* Streamlit
* Pandas
* Plotly

## Project Structure

```text
healthcare-patient-analytics/
├── app.py
├── data/
│   └── sample_patients.csv
├── src/
│   ├── analytics.py
│   ├── charts.py
│   ├── data_loader.py
│   ├── schema.py
│   └── validation.py
├── requirements.txt
└── README.md
```

## Run Locally

```bash
git clone <repository-url>
cd healthcare-patient-analytics

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

The application will open in the browser at the local Streamlit address.

## Data Workflow

```text
CSV Dataset
     ↓
Data Loading
     ↓
Schema Mapping
     ↓
Normalization
     ↓
Validation
     ↓
Analytics
     ↓
Patient Dashboard
     ↓
Clinical Trends & Data Quality
```

## Data Privacy

This project is designed for demo and development purposes. Do not upload real patient-identifiable or sensitive healthcare data to an untrusted environment.

## License

MIT License
