"""
KNN.py — K-Nearest Neighbours regression for predicting water quality
at unmonitored coordinates across the Great Lakes.

Pipeline:
  1. Load observed data from combined_data.csv
  2. Train one KNNRegressor per characteristic (lat, lon, month as features)
  3. Generate a lat/lon prediction grid across each lake
  4. Predict all characteristics at every grid point
  5. Recalculate WQI from predicted values using the Purdue formula
  6. Write knn_predictions.csv  — predicted points only
     Write tableau_ready.csv    — observed + predicted merged (DataType column for filtering)
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from WQI import calculate_wqi

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Number of nearest neighbours to use for regression
K = 5

# Characteristics to predict — these are the columns present in combined_data.csv
CHARACTERISTICS = [
    "Chloride",
    "Dissolved oxygen (DO)",
    "Temperature, water",
    "Total suspended solids",
    "Turbidity",
    "pH",
]

# Column order that matches combined_data.csv (+ DataType for Tableau filtering)
OUTPUT_COLUMNS = [
    "MonitoringLocationID",
    "MonitoringLocationName",
    "MonitoringLocationLatitude",
    "MonitoringLocationLongitude",
    "ActivityStartDate",
    "Chloride",
    "Dissolved oxygen (DO)",
    "Temperature, water",
    "Total suspended solids",
    "Turbidity",
    "pH",
    "WQI",
    "Rating",
    "DataType",
]

# Approximate bounding boxes for each Great Lakes body.
# These define where prediction grid points are generated.
# Step resolution is controlled by GRID_STEP in run().
LAKE_BOUNDS = {
    "Lake Superior":  {"lat": (46.5, 49.0), "lon": (-92.0, -84.5)},
    "Lake Michigan":  {"lat": (41.5, 46.0), "lon": (-88.0, -84.5)},
    "Lake Huron":     {"lat": (43.0, 46.5), "lon": (-84.5, -79.0)},
    "Georgian Bay":   {"lat": (44.5, 46.0), "lon": (-81.5, -79.0)},
    "Lake Erie":      {"lat": (41.5, 43.0), "lon": (-83.5, -78.5)},
    "Lake Ontario":   {"lat": (43.0, 44.5), "lon": (-79.5, -75.5)},
}

# Representative prediction month (July = peak summer, most comparable to observed data)
PREDICTION_MONTH = 7
PREDICTION_DATE = "2024-07-01"


# ---------------------------------------------------------------------------
# Grid generation
# ---------------------------------------------------------------------------

def generate_grid(step: float = 0.3) -> pd.DataFrame:
    """
    Build a lat/lon grid across all lake bounding boxes.

    Parameters
    ----------
    step : float
        Grid resolution in decimal degrees. 0.3° ≈ 33 km.

    Returns
    -------
    pd.DataFrame with columns: MonitoringLocationName, MonitoringLocationLatitude,
    MonitoringLocationLongitude, Month
    """
    rows = []
    for lake_name, bounds in LAKE_BOUNDS.items():
        lats = np.arange(bounds["lat"][0], bounds["lat"][1], step)
        lons = np.arange(bounds["lon"][0], bounds["lon"][1], step)
        for lat in lats:
            for lon in lons:
                rows.append({
                    "MonitoringLocationName": lake_name,
                    "MonitoringLocationLatitude": round(float(lat), 4),
                    "MonitoringLocationLongitude": round(float(lon), 4),
                    "Month": PREDICTION_MONTH,
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Model training and prediction
# ---------------------------------------------------------------------------

def train_and_predict(df_observed: pd.DataFrame, df_grid: pd.DataFrame) -> pd.DataFrame:
    """
    Train one KNeighborsRegressor per characteristic and predict values at
    every grid point.

    Features used: Latitude, Longitude, Month (captures seasonal variation).
    All features are scaled with StandardScaler before fitting.

    Parameters
    ----------
    df_observed : DataFrame — the processed observed data (combined_data.csv)
    df_grid     : DataFrame — the prediction grid from generate_grid()

    Returns
    -------
    df_grid with predicted characteristic columns filled in.
    """
    feature_cols = ["MonitoringLocationLatitude", "MonitoringLocationLongitude", "Month"]

    # Add Month column extracted from ActivityStartDate
    df_obs = df_observed.copy()
    df_obs["Month"] = pd.to_datetime(df_obs["ActivityStartDate"]).dt.month

    X_train = df_obs[feature_cols].values
    X_pred = df_grid[feature_cols].values

    # Scale features so lat/lon/month differences are comparable
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_pred_scaled = scaler.transform(X_pred)

    results = df_grid.copy()

    for char in CHARACTERISTICS:
        if char not in df_obs.columns:
            print(f"  Warning: '{char}' not found in observed data — skipping.")
            continue

        y_train = df_obs[char].values

        # Cap K to the number of training samples (guards against tiny datasets)
        k = min(K, len(X_train))
        model = KNeighborsRegressor(n_neighbors=k, weights="distance", metric="euclidean")
        model.fit(X_train_scaled, y_train)

        results[char] = np.round(model.predict(X_pred_scaled), 3)
        print(f"  Predicted {char} at {len(results)} grid points (k={k})")

    return results


# ---------------------------------------------------------------------------
# WQI calculation for predicted rows
# ---------------------------------------------------------------------------

def apply_wqi(df: pd.DataFrame) -> pd.DataFrame:
    """Apply calculate_wqi() row-wise and add WQI and Rating columns."""
    df = df.copy()
    wqi_results = df.apply(
        lambda row: calculate_wqi(
            temp=row["Temperature, water"],
            tss=row["Total suspended solids"],
            do=row["Dissolved oxygen (DO)"],
        ),
        axis=1,
    )
    df["WQI"] = [r["WQI"] for r in wqi_results]
    df["Rating"] = [r["Rating"] for r in wqi_results]
    return df


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(
    input_csv: str = "data/combined_data.csv",
    predictions_csv: str = "data/knn_predictions.csv",
    tableau_csv: str = "data/tableau_ready.csv",
    grid_step: float = 0.3,
) -> pd.DataFrame:
    """
    Full KNN pipeline: load → train → predict → save.

    Outputs
    -------
    data/knn_predictions.csv  — predicted points only
    data/tableau_ready.csv    — observed + predicted merged, ready for Tableau
                                 Use the DataType column to toggle layers.
    """
    print(f"Loading observed data from {input_csv}...")
    df_observed = pd.read_csv(input_csv)
    print(f"  {len(df_observed)} observed rows, {df_observed['MonitoringLocationName'].nunique()} locations")

    print(f"\nGenerating prediction grid (step={grid_step}°)...")
    df_grid = generate_grid(step=grid_step)
    print(f"  {len(df_grid)} grid points across {len(LAKE_BOUNDS)} lake regions")

    print("\nTraining KNN models and predicting characteristics...")
    df_predicted = train_and_predict(df_observed, df_grid)

    print("\nCalculating WQI for predicted points...")
    df_predicted = apply_wqi(df_predicted)

    # Add metadata to match combined_data.csv schema
    df_predicted["MonitoringLocationID"] = "predicted"
    df_predicted["ActivityStartDate"] = PREDICTION_DATE
    df_predicted["DataType"] = "Predicted"

    df_predicted = df_predicted[OUTPUT_COLUMNS]
    df_predicted.to_csv(predictions_csv, index=False)
    print(f"\nSaved {len(df_predicted)} predicted points → {predictions_csv}")

    # Build merged file for Tableau: tag observed rows then concatenate
    df_obs_tagged = df_observed.copy()
    df_obs_tagged["DataType"] = "Observed"
    df_obs_tagged = df_obs_tagged[OUTPUT_COLUMNS]

    df_tableau = pd.concat([df_obs_tagged, df_predicted], ignore_index=True)
    df_tableau.to_csv(tableau_csv, index=False)
    print(f"Saved {len(df_tableau)} total rows (observed + predicted) → {tableau_csv}")
    print("\nDone. Connect Tableau to data/tableau_ready.csv for the full map view.")

    return df_predicted


if __name__ == "__main__":
    run()
