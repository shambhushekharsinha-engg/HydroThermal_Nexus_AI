# -*- coding: utf-8 -*-
"""
ml_engine.py — HydroThermal Nexus-AI ML Analytics Core
Provides telemetry simulation, dual-mode anomaly detection (Adaptive Z-Score & IsolationForest),
custom Kaggle CSV dataset scoring, model serialization, and explainable AI guidance.
"""

import os
import logging
import joblib
from typing import Tuple, Dict, List, Any, Optional

import numpy as np
import pandas as pd
import config
from functools import lru_cache

logger: logging.Logger = logging.getLogger("HydroThermalNexus.MLEngine")

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML anomaly scoring will fall back to rule-based logic.")


class HydroThermalAnalyticsCore:
    """
    Central ML/analytics engine for the HydroThermal Nexus-AI platform.
    Provides telemetry simulation, dual-mode anomaly detection, joblib model persistence,
    and explainable AI guidance for operations.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        self._iso_model: Optional[Any] = None
        self._scaler: Optional[Any] = None
        self._trained: bool = False
        self._train_df: pd.DataFrame = pd.DataFrame()
        self._feature_cols: List[str] = []
        self._metrics_meta: Dict[str, Any] = {}

        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "nexus_isolation_forest.joblib")

        if os.path.exists(model_path):
            self.load_model(model_path)

    @lru_cache(maxsize=4)
    def generate_live_production_stream(self, periods: int = 60) -> pd.DataFrame:
        """Generates realistic 60-step telemetry stream with embedded anomaly spikes."""
        np.random.seed(42)
        dates = pd.date_range(start="2026-07-01", periods=periods, freq="6h")

        electricity = np.random.normal(loc=config.ELEC_BASE_MEAN, scale=config.ELEC_BASE_STD, size=periods)
        water = np.random.normal(loc=config.WATER_BASE_MEAN, scale=config.WATER_BASE_STD, size=periods)
        outdoor_temp = np.random.uniform(28.0, 38.0, size=periods)
        humidity = np.random.uniform(45.0, 85.0, size=periods)
        pressure_psi = np.random.normal(42.5, 1.2, size=periods)
        thermal_temp = np.random.normal(68.4, 2.5, size=periods)

        # Inject realistic anomalies
        electricity[18] = config.ELEC_BASE_MEAN * 1.55
        water[42] = config.WATER_BASE_MEAN * 1.85
        pressure_psi[18] = 28.0
        thermal_temp[42] = 105.0

        return pd.DataFrame({
            "Timestamp": dates,
            "Electricity_kWh": electricity,
            "Water_Litres": water,
            "Outdoor_Temp_C": outdoor_temp,
            "Humidity_Pct": humidity,
            "Pressure_PSI": pressure_psi,
            "Thermal_Temp_C": thermal_temp,
        })

    @lru_cache(maxsize=1)
    def get_eda_summary(self) -> pd.DataFrame:
        """Returns descriptive statistics of the telemetry stream."""
        df = self.generate_live_production_stream()
        numeric = df.drop(columns=["Timestamp"])
        stats = numeric.describe().T
        stats["missing_pct"] = 0.0
        stats["completeness"] = 100.0
        return stats.round(2)

    @lru_cache(maxsize=1)
    def get_data_dictionary(self) -> pd.DataFrame:
        """Returns data dictionary describing telemetry fields."""
        return pd.DataFrame([
            {"Field": "Electricity_kWh", "Unit": "kWh", "Description": "Electricity consumption over 6-hour interval", "Normal Range": "2,000 – 2,400", "Alert Threshold": "> 3,000 (CRITICAL)", "Source": "Smart meter / SCADA"},
            {"Field": "Water_Litres", "Unit": "Litres", "Description": "Water volume consumed / circulated", "Normal Range": "2,900 – 3,300", "Alert Threshold": "> 4,500 (CRITICAL), < 1,500 (FLOW DROP)", "Source": "Flow meter"},
            {"Field": "Outdoor_Temp_C", "Unit": "°C", "Description": "Ambient outdoor temperature", "Normal Range": "28 – 38", "Alert Threshold": "> 42 (HVAC stress warning)", "Source": "Roof sensor"},
            {"Field": "Humidity_Pct", "Unit": "%", "Description": "Relative humidity", "Normal Range": "45 – 85", "Alert Threshold": "> 90 (corrosion risk)", "Source": "Humidity sensor"},
            {"Field": "Pressure_PSI", "Unit": "PSI", "Description": "Main header hydraulic pressure", "Normal Range": "38 – 46", "Alert Threshold": "< 30 (rupture), > 52 (over-pressure)", "Source": "Pressure transducer"},
            {"Field": "Thermal_Temp_C", "Unit": "°C", "Description": "Thermal loop return temperature", "Normal Range": "60 – 75", "Alert Threshold": "> 89 (WARNING), > 100 (CRITICAL)", "Source": "Thermocouple"},
        ])

    def compute_predictive_anomaly(
        self, current_val: float, ambient_temp: float, humidity: float, stream_type: str = "water"
    ) -> Tuple[bool, float]:
        """Adaptive Z-score anomaly detection. Returns (is_anomaly, risk_score)."""
        if stream_type == "water":
            adjusted_mean = config.WATER_BASE_MEAN + (humidity * 0.15)
            z_score = (current_val - adjusted_mean) / config.WATER_BASE_STD
            return bool(z_score > 3.5), min(100.0, max(0.0, float(z_score * 12.5)))
        else:
            temp_offset = max(0.0, ambient_temp - 30.0) * 85.0
            adjusted_mean = config.ELEC_BASE_MEAN + temp_offset
            z_score = (current_val - adjusted_mean) / config.ELEC_BASE_STD
            return bool(z_score > 3.5), min(100.0, max(0.0, float(z_score * 14.2)))

    def train_isolation_forest(
        self, contamination: float = 0.05, n_estimators: int = 100
    ) -> Dict[str, Any]:
        """Trains IsolationForest on generated telemetry stream."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed."}

        df = self.generate_live_production_stream()
        features = ["Electricity_kWh", "Water_Litres", "Pressure_PSI", "Thermal_Temp_C", "Outdoor_Temp_C", "Humidity_Pct"]
        X = df[features].values

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._iso_model = IsolationForest(
            n_estimators=n_estimators, contamination=contamination, random_state=42
        )
        preds = self._iso_model.fit_predict(X_scaled)

        y_true = np.ones(len(df))
        y_true[[18, 42]] = -1

        y_pred_binary = (preds == -1).astype(int)
        y_true_binary = (y_true == -1).astype(int)

        self._trained = True
        self._train_df = df

        metrics = {
            "model": "IsolationForest",
            "n_estimators": n_estimators,
            "contamination": contamination,
            "training_rows": len(df),
            "features": features,
            "anomalies_found": int(y_pred_binary.sum()),
            "precision": round(float(precision_score(y_true_binary, y_pred_binary, zero_division=0)), 3),
            "recall": round(float(recall_score(y_true_binary, y_pred_binary, zero_division=0)), 3),
            "f1_score": round(float(f1_score(y_true_binary, y_pred_binary, zero_division=0)), 3),
        }
        logger.info("IsolationForest trained successfully: F1 score %s", metrics["f1_score"])
        return metrics

    def train_custom_isolation_forest(
        self, df: pd.DataFrame, feature_cols: Optional[List[str]] = None, contamination: float = 0.05, n_estimators: int = 100
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Trains IsolationForest on custom DataFrame (CSV upload / Kaggle datasets)."""
        if not SKLEARN_AVAILABLE:
            df_ret = df.copy()
            df_ret["IF_Anomaly"] = False
            df_ret["IF_Score"] = 0.0
            return df_ret, {"error": "scikit-learn not installed."}

        if df.empty:
            return df, {"error": "Uploaded dataset is empty."}

        if not feature_cols:
            feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not feature_cols:
            df_ret = df.copy()
            df_ret["IF_Anomaly"] = False
            df_ret["IF_Score"] = 0.0
            return df_ret, {"error": "No numeric feature columns found in dataset."}

        df_clean = df.copy()
        for c in feature_cols:
            if df_clean[c].isnull().any():
                df_clean[c] = df_clean[c].fillna(df_clean[c].median())

        X = df_clean[feature_cols].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        iso_model = IsolationForest(
            n_estimators=n_estimators, contamination=contamination, random_state=42
        )
        raw_preds = iso_model.fit_predict(X_scaled)
        scores = iso_model.score_samples(X_scaled)

        s_min, s_max = scores.min(), scores.max()
        denom = (s_max - s_min) if (s_max != s_min) else 1e-9
        anomaly_score = 1.0 - ((scores - s_min) / denom)

        df_scored = df.copy()
        df_scored["IF_Anomaly"] = (raw_preds == -1)
        df_scored["IF_Score"] = np.round(anomaly_score * 100, 1)

        anomalies_count = int((raw_preds == -1).sum())

        metrics = {
            "model": "IsolationForest (Custom Dataset)",
            "n_estimators": n_estimators,
            "contamination": contamination,
            "training_rows": len(df),
            "features_used": feature_cols,
            "anomalies_found": anomalies_count,
            "anomaly_pct": round((anomalies_count / max(1, len(df))) * 100, 2),
            "avg_risk_score": round(float(df_scored["IF_Score"].mean()), 1),
            "max_risk_score": round(float(df_scored["IF_Score"].max()), 1),
        }

        self._feature_cols = feature_cols
        self._metrics_meta = metrics
        self._iso_model = iso_model
        self._scaler = scaler
        self._trained = True

        logger.info("Custom IsolationForest trained on %d rows. Found %d anomalies.", len(df), anomalies_count)
        return df_scored, metrics

    def save_model(self, model_path: str) -> bool:
        """Serializes model artifact to disk."""
        if not self._trained or self._iso_model is None:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(model_path)), exist_ok=True)
        artifact = {
            "model": self._iso_model,
            "scaler": self._scaler,
            "feature_cols": self._feature_cols,
            "metrics_meta": self._metrics_meta,
            "trained": True,
        }
        joblib.dump(artifact, model_path)
        logger.info("Saved model artifact to %s", model_path)
        return True

    def load_model(self, model_path: str) -> bool:
        """Loads pre-trained model artifact from disk."""
        if not os.path.exists(model_path):
            return False
        try:
            artifact = joblib.load(model_path)
            self._iso_model = artifact.get("model")
            self._scaler = artifact.get("scaler")
            self._feature_cols = artifact.get("feature_cols", [])
            self._metrics_meta = artifact.get("metrics_meta", {})
            self._trained = artifact.get("trained", True)
            logger.info("Loaded model artifact from %s", model_path)
            return True
        except Exception as e:
            logger.warning("Failed to load model artifact from %s: %s", model_path, e)
            return False

    def get_model_metrics(self) -> Dict[str, Any]:
        """Returns metadata about active model."""
        return {
            "trained": self._trained,
            "model_type": "IsolationForest",
            "feature_count": len(self._feature_cols),
            "features": self._feature_cols,
            "metrics": self._metrics_meta,
            "status": "ready" if self._trained else "uninitialized"
        }

    def generate_sample_kaggle_dataset(self) -> pd.DataFrame:
        """Generates sample turbine sensor dataset."""
        np.random.seed(123)
        n = 200
        timestamps = pd.date_range("2026-07-01", periods=n, freq="15min")
        vibration_mm_s = np.random.normal(2.5, 0.4, n)
        bearing_temp_c = np.random.normal(55.0, 3.2, n)
        rotational_rpm = np.random.normal(3000, 45, n)
        lubricant_flow = np.random.normal(12.0, 0.8, n)
        power_kw = np.random.normal(450.0, 15.0, n)

        vibration_mm_s[15] = 9.8
        bearing_temp_c[15] = 98.4
        rotational_rpm[45] = 3450
        lubricant_flow[90] = 2.1
        vibration_mm_s[120] = 8.5
        bearing_temp_c[150] = 105.2
        power_kw[180] = 620.0

        return pd.DataFrame({
            "Timestamp": timestamps,
            "Turbine_ID": "TURB-A04",
            "Vibration_mm_s": np.round(vibration_mm_s, 2),
            "Bearing_Temp_C": np.round(bearing_temp_c, 2),
            "Rotational_RPM": np.round(rotational_rpm, 1),
            "Lubricant_Flow_L_min": np.round(lubricant_flow, 2),
            "Power_kW": np.round(power_kw, 1),
        })