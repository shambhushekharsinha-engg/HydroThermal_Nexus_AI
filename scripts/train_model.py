"""
scripts/train_model.py
CLI script to train and serialize the HydroThermal Nexus-AI IsolationForest model pipeline.
Uses historical Kaggle SKAB / MetroPT-3 formatted telemetry dataset to output 'models/nexus_isolation_forest.joblib'.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ml_engine import HydroThermalAnalyticsCore

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "hydrothermal_telemetry_historical.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "nexus_isolation_forest.joblib")


def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Benchmark dataset not found at {DATA_PATH}. Please generate data first.")
        sys.exit(1)
        
    print(f"Loading benchmark dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

    feature_cols = [
        "Electricity_kWh", "Water_Litres", "Pressure_PSI",
        "Thermal_Temp_C", "Outdoor_Temp_C", "Humidity_Pct", "Vibration_mm_s"
    ]
    
    available_features = [f for f in feature_cols if f in df.columns]
    print(f"Using feature columns: {available_features}")

    engine = HydroThermalAnalyticsCore()
    scored_df, metrics = engine.train_custom_isolation_forest(
        df=df,
        feature_cols=available_features,
        contamination=0.04,
        n_estimators=150
    )

    print("\n--- Training Results & Metrics ---")
    for k, v in metrics.items():
        print(f"  • {k}: {v}")

    # Save model artifact to disk
    save_result = engine.save_model(MODEL_PATH)
    print(f"\n[SUCCESS] Model artifact saved to: {MODEL_PATH}")
    return save_result


if __name__ == "__main__":
    train_and_save()
