"""
tests/test_ml.py
Automated unit test suite for HydroThermal Analytics Core ML Engine.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ml_engine import HydroThermalAnalyticsCore


def test_telemetry_stream_generation():
    engine = HydroThermalAnalyticsCore()
    df = engine.generate_live_production_stream(periods=60)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 60
    assert "Electricity_kWh" in df.columns
    assert "Thermal_Temp_C" in df.columns


def test_predictive_anomaly_zscore():
    engine = HydroThermalAnalyticsCore()
    is_anomaly, risk_score = engine.compute_predictive_anomaly(
        current_val=5000.0, ambient_temp=35.0, humidity=60.0, stream_type="water"
    )
    assert is_anomaly is True
    assert risk_score > 50.0


def test_isolation_forest_training_and_serialization(tmp_path):
    engine = HydroThermalAnalyticsCore()
    df = engine.generate_sample_kaggle_dataset()
    
    scored_df, metrics = engine.train_custom_isolation_forest(
        df=df,
        feature_cols=["Vibration_mm_s", "Bearing_Temp_C", "Power_kW"],
        contamination=0.05
    )
    
    assert "IF_Anomaly" in scored_df.columns
    assert "IF_Score" in scored_df.columns
    assert metrics["anomalies_found"] >= 1

    model_file = tmp_path / "test_model.joblib"
    saved = engine.save_model(str(model_file))
    assert saved is True
    assert os.path.exists(model_file)

    # Test reloading into new engine instance
    new_engine = HydroThermalAnalyticsCore(model_path=str(model_file))
    reloaded_metrics = new_engine.get_model_metrics()
    assert reloaded_metrics["trained"] is True
