# Great Lakes Water Quality Index

> COMP-3250 · Group 4 · University of Windsor

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.1-150458?logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-KNN-F7931E?logo=scikit-learn&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-Public-E97627?logo=tableau&logoColor=white)

End-to-end water quality analysis pipeline for the 5 Great Lakes. Pulls monitoring data from the [DataStream API](https://datastream.org/en-ca/documentation/api), calculates Water Quality Index (WQI) scores using the Purdue University formula, and uses KNN regression to predict water quality at unmonitored coordinates — all visualized in an interactive Tableau dashboard.

---

## Features

- **Data ingestion** — queries the DataStream API for 8 water quality parameters across Georgian Bay, Lake Huron, Lake Erie, Lake Ontario, and Lake Superior (2021–present)
- **WQI calculation** — Purdue University formula scoring temperature, dissolved oxygen, TSS, BOD, and conductivity on a 0–100 scale
- **KNN regression** — predicts all water quality characteristics at ~830 unmonitored coordinates across the Great Lakes using scikit-learn
- **Tableau-ready output** — `tableau_ready.csv` merges observed and predicted data with a `DataType` filter column for interactive map layers

---

## Pipeline

```
DataStream API
     │
     ▼
DataToCSV.py  ──►  data/milligram.csv
                   data/celsius.csv
                   data/ntu.csv
     │
     ▼
CombineData.py ──► data/combined_data.csv   (WQI calculated)
     │
     ▼
KNN.py ─────────►  data/knn_predictions.csv
                   data/tableau_ready.csv   (observed + predicted, for Tableau)
```

---

## Quick Start

**Prerequisites:** Python 3.9+, a [DataStream API key](https://datastream.org/en-ca/documentation/api)

```bash
# 1. Clone and install
git clone https://github.com/AaronSinn/3250-Group-Project.git
cd 3250-Group-Project
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Edit .env → set API_KEY=your_key_here

# 3. Fetch data from DataStream
python3 DataToCSV.py

# 4. Process and calculate WQI
python3 CombineData.py

# 5. Run KNN predictions
python3 KNN.py
```

After step 5, open **`data/tableau_ready.csv`** in Tableau to build the dashboard.

> **Note:** Steps 3–4 require an API key. Steps 4–5 can be run on the committed CSV files without one.

---

## Output Files

| File | Rows | Description |
|------|------|-------------|
| `data/combined_data.csv` | ~769 | Observed monitoring data with WQI scores |
| `data/knn_predictions.csv` | ~833 | Predicted water quality at unmonitored grid points |
| `data/tableau_ready.csv` | ~1602 | Observed + predicted merged — primary Tableau data source |

---

## Water Quality Parameters

| Parameter | Unit | Source |
|-----------|------|--------|
| Dissolved Oxygen (DO) | mg/L | DataStream API |
| Temperature | °C | DataStream API |
| Total Suspended Solids | mg/L | DataStream API |
| Turbidity | NTU | DataStream API |
| pH | — | DataStream API |
| Chloride | mg/L | DataStream API |
| Chlorophyll a | mg/L | DataStream API |
| BOD (std. conditions) | mg/L | DataStream API |

**WQI Rating scale:** Excellent ≥ 95 · Good ≥ 75 · Fair ≥ 50 · Poor < 50

---

## Project Structure

```
├── DataToCSV.py          # Step 1: API fetch → raw CSVs
├── CombineData.py        # Step 2: merge, pivot, impute, calculate WQI
├── WQI.py                # Purdue WQI formula (pure function)
├── KNN.py                # KNN regression → prediction grid + Tableau export
├── data/
│   ├── combined_data.csv
│   ├── knn_predictions.csv
│   └── tableau_ready.csv
├── requirements.txt
└── .env.example
```

---

## Tableau Dashboard

Connect Tableau Desktop to `data/tableau_ready.csv`:

- **Map view** — plot `MonitoringLocationLatitude` / `MonitoringLocationLongitude`, colour by `WQI` or `Rating`
- **DataType filter** — toggle between `Observed` and `Predicted` layers
- **Parameter filters** — drill down by `MonitoringLocationName`, `ActivityStartDate`, or any characteristic column

Publish to [Tableau Public](https://public.tableau.com) for a shareable link.

---

## Team

Group 4 — COMP-3250 Data Analytics & Intelligence, University of Windsor
