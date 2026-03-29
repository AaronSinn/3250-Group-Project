# CLAUDE.md — COMP-3250 Group 4: Great Lakes Water Quality

## Project Overview

Water Quality Index (WQI) analysis tool for the 5 Great Lakes. Fetches monitoring data
from the DataStream API, calculates WQI scores using the Purdue University formula, and
(in progress) predicts water quality at unmonitored locations via KNN regression, all
surfaced through a Tableau dashboard.

**Submission deadline: March 29, 2026 (D.3 Code + D.4 Report + D.5 Presentation)**

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Data Fetching | `datastream-py` SDK (OData v4 wrapper) |
| Data Processing | `pandas 2.1.1` |
| ML (planned) | `scikit-learn` — KNN regression |
| Visualization | Tableau Desktop → publish to Tableau Public |
| Config | `python-dotenv` (`.env` file) |

## Key Directories & Files

```
3250-Group-Project/
├── DataToCSV.py          # Step 1 — queries DataStream API, writes 3 raw CSVs
├── CombineData.py        # Step 2 — merges CSVs, pivots, imputes, calculates WQI
├── WQI.py                # Purdue WQI formula (pure function, no I/O)
├── data/                 # Raw + processed CSVs (gitignored large files)
│   ├── milligram.csv     # pH, Chloride, DO, Chl-a, TSS, BOD
│   ├── celsius.csv       # Temperature, water
│   ├── ntu.csv           # Turbidity
│   └── combined_data.csv # Final dataset fed into Tableau & KNN
├── context/              # PDFs: proposal, submission rubrics, Gantt chart
├── .env                  # API_KEY (never commit — gitignored)
└── requirements.txt      # pip dependencies
```

Key line references:
- WQI formula entry point: `WQI.py:3`
- API filter constants (Great Lakes scope): `DataToCSV.py:18-26`
- Pivot + imputation logic: `CombineData.py:15-27`
- WQI application loop: `CombineData.py:29-37`

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # then add your DataStream API key

# Step 1: Fetch data from DataStream API (~few minutes, rate-limited at 2 req/s)
python DataToCSV.py    # outputs: data/milligram.csv, celsius.csv, ntu.csv

# Step 2: Process data and calculate WQI
python CombineData.py  # outputs: data/combined_data.csv
```

## Features Still Needed (from Project Proposal)

- [ ] **KNN regression** — predict WQI at unmonitored coordinates using scikit-learn
- [ ] **Tableau dashboard** — interactive map + filters by lake/date/parameter
  - Use Tableau Desktop (Windows/Mac) → publish to Tableau Public for shareable URL
  - The submission requires a live cloud platform link (Tableau Public URL qualifies)

## Additional Documentation

Check these files when working on specific areas:

| Topic | File |
|---|---|
| Architecture, design patterns, data flow | `.claude/docs/architectural_patterns.md` |
| DataStream API — endpoints, OData filters, pagination, SDK | `.claude/docs/datastream_api.md` |
| Submission requirements (D.3/D.4 rubric, report structure) | `.claude/docs/submission_requirements.md` |
