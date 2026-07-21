"""
ml_engine.py  —  HydroThermal Nexus-AI v2.0
ML Analytics Core:
  - Live production telemetry stream generator
  - Adaptive Z-score anomaly detector (rule-based, fast)
  - IsolationForest anomaly detector (sklearn, trained model)
  - Model performance metrics (precision, recall, F1)
  - Predictive guidance assistant hook
"""

import numpy as np
import pandas as pd
import config
from typing import Tuple, Dict

# sklearn IsolationForest — optional, graceful fallback if not installed
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class HydroThermalAnalyticsCore:
    """
    Central ML/analytics engine for the HydroThermal Nexus-AI platform.
    Provides telemetry simulation, dual-mode anomaly detection, and
    explainable AI guidance for operations.
    """

    def __init__(self):
        self._iso_model: object   = None
        self._scaler:    object   = None
        self._trained:   bool     = False
        self._train_df:  pd.DataFrame = pd.DataFrame()

    # ── Telemetry Simulation ──────────────────────────────────────────
    def generate_live_production_stream(self, periods: int = 60) -> pd.DataFrame:
        """
        Generates a realistic 60-step (6h interval) telemetry dataset
        with mild natural variance and embedded anomaly spikes.
        """
        np.random.seed(42)
        dates = pd.date_range(start="2026-07-01", periods=periods, freq="6h")

        electricity = np.random.normal(
            loc=config.ELEC_BASE_MEAN, scale=config.ELEC_BASE_STD, size=periods
        )
        water = np.random.normal(
            loc=config.WATER_BASE_MEAN, scale=config.WATER_BASE_STD, size=periods
        )
        outdoor_temp = np.random.uniform(28.0, 38.0, size=periods)
        humidity     = np.random.uniform(45.0, 85.0, size=periods)
        pressure_psi = np.random.normal(42.5, 1.2, size=periods)
        thermal_temp = np.random.normal(68.4, 2.5, size=periods)

        # Inject realistic anomaly spikes at indices 18 and 42
        electricity[18] = config.ELEC_BASE_MEAN * 1.55   # energy spike
        water[42]       = config.WATER_BASE_MEAN * 1.85   # flow anomaly
        pressure_psi[18] = 28.0                           # pressure drop
        thermal_temp[42] = 105.0                          # thermal exceedance

        df = pd.DataFrame({
            "Timestamp":       dates,
            "Electricity_kWh": electricity,
            "Water_Litres":    water,
            "Outdoor_Temp_C":  outdoor_temp,
            "Humidity_Pct":    humidity,
            "Pressure_PSI":    pressure_psi,
            "Thermal_Temp_C":  thermal_temp,
        })
        return df

    def get_eda_summary(self) -> pd.DataFrame:
        """Returns descriptive statistics of the telemetry stream."""
        df = self.generate_live_production_stream()
        numeric = df.drop(columns=["Timestamp"])
        stats   = numeric.describe().T
        stats["missing_pct"] = 0.0          # simulated — no NaNs in generated data
        stats["completeness"] = 100.0
        return stats.round(2)

    def get_data_dictionary(self) -> pd.DataFrame:
        """Returns a data dictionary describing each telemetry field."""
        return pd.DataFrame([
            {
                "Field":         "Electricity_kWh",
                "Unit":          "kWh",
                "Description":   "Total electricity consumption over the 6-hour interval",
                "Normal Range":  "2,000 – 2,400",
                "Alert Threshold": "> 3,000 (CRITICAL)",
                "Source":        "Smart energy meter / SCADA",
            },
            {
                "Field":         "Water_Litres",
                "Unit":          "Litres",
                "Description":   "Total water volume consumed / circulated in thermal loop",
                "Normal Range":  "2,900 – 3,300",
                "Alert Threshold": "> 4,500 (CRITICAL), < 1,500 (FLOW DROP)",
                "Source":        "Electromagnetic flow meter",
            },
            {
                "Field":         "Outdoor_Temp_C",
                "Unit":          "°C",
                "Description":   "Ambient outdoor temperature at facility",
                "Normal Range":  "28 – 38",
                "Alert Threshold": "> 42 (HVAC stress warning)",
                "Source":        "Weather API / roof-mounted sensor",
            },
            {
                "Field":         "Humidity_Pct",
                "Unit":          "%",
                "Description":   "Relative humidity — affects thermal loop efficiency",
                "Normal Range":  "45 – 85",
                "Alert Threshold": "> 90 (corrosion risk)",
                "Source":        "Hall-effect humidity sensor",
            },
            {
                "Field":         "Pressure_PSI",
                "Unit":          "PSI",
                "Description":   "Main header hydraulic pressure in the pipe network",
                "Normal Range":  "38 – 46",
                "Alert Threshold": "< 30 (rupture), > 52 (over-pressure)",
                "Source":        "Differential pressure transducer",
            },
            {
                "Field":         "Thermal_Temp_C",
                "Unit":          "°C",
                "Description":   "Cooling tower / thermal loop return temperature",
                "Normal Range":  "60 – 75",
                "Alert Threshold": "> 89 (WARNING), > 100 (CRITICAL — fan relay stall)",
                "Source":        "RTD / thermocouple on heat exchanger",
            },
        ])

    # ── Z-Score Anomaly Detector (fast, rule-based) ───────────────────
    def compute_predictive_anomaly(
        self,
        current_val: float,
        ambient_temp: float,
        humidity: float,
        stream_type: str = "water",
    ) -> Tuple[bool, float]:
        """
        Adaptive Z-score anomaly detection.
        Returns (is_anomaly: bool, risk_score: float 0-100).
        """
        if stream_type == "water":
            adjusted_mean = config.WATER_BASE_MEAN + (humidity * 0.15)
            z_score = (current_val - adjusted_mean) / config.WATER_BASE_STD
            return z_score > 3.5, min(100.0, max(0.0, float(z_score * 12.5)))
        else:
            temp_offset   = max(0, ambient_temp - 30.0) * 85.0
            adjusted_mean = config.ELEC_BASE_MEAN + temp_offset
            z_score = (current_val - adjusted_mean) / config.ELEC_BASE_STD
            return z_score > 3.5, min(100.0, max(0.0, float(z_score * 14.2)))

    # ── IsolationForest Detector (trained ML model) ───────────────────
    def train_isolation_forest(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
    ) -> Dict:
        """
        Trains an IsolationForest on the generated telemetry stream.
        Returns training summary with model performance metrics.
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed. Run: pip install scikit-learn"}

        df       = self.generate_live_production_stream()
        features = ["Electricity_kWh", "Water_Litres", "Pressure_PSI",
                    "Thermal_Temp_C", "Outdoor_Temp_C", "Humidity_Pct"]
        X        = df[features].values

        self._scaler    = StandardScaler()
        X_scaled        = self._scaler.fit_transform(X)

        self._iso_model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42,
            n_jobs=None,
        )
        preds           = self._iso_model.fit_predict(X_scaled)

        # Ground-truth labels: indices 18 and 42 are injected anomalies
        y_true = np.ones(len(df))
        y_true[[18, 42]] = -1

        # Map IsolationForest: -1 = anomaly, +1 = normal
        y_pred_binary = (preds == -1).astype(int)
        y_true_binary = (y_true == -1).astype(int)

        self._trained  = True
        self._train_df = df

        return {
            "model":          "IsolationForest",
            "n_estimators":   n_estimators,
            "contamination":  contamination,
            "training_rows":  len(df),
            "features":       features,
            "anomalies_found": int(y_pred_binary.sum()),
            "precision":      round(precision_score(y_true_binary, y_pred_binary, zero_division=0), 3),
            "recall":         round(recall_score(y_true_binary, y_pred_binary, zero_division=0), 3),
            "f1_score":       round(f1_score(y_true_binary, y_pred_binary, zero_division=0), 3),
        }

    def score_with_isolation_forest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scores a DataFrame using the trained IsolationForest model.
        Adds 'IF_Anomaly' (bool) and 'IF_Score' (float) columns.
        Returns df with new columns.
        """
        if not self._trained or not SKLEARN_AVAILABLE:
            df["IF_Anomaly"] = False
            df["IF_Score"]   = 0.0
            return df

        features = ["Electricity_kWh", "Water_Litres", "Pressure_PSI",
                    "Thermal_Temp_C", "Outdoor_Temp_C", "Humidity_Pct"]
        available = [c for c in features if c in df.columns]
        if len(available) < 4:
            df["IF_Anomaly"] = False
            df["IF_Score"]   = 0.0
            return df

        # Fill missing feature cols with baseline means
        for f in features:
            if f not in df.columns:
                df[f] = config.WATER_BASE_MEAN if "Water" in f else config.ELEC_BASE_MEAN

        X_scaled      = self._scaler.transform(df[features].fillna(0).values)
        raw_preds     = self._iso_model.predict(X_scaled)
        scores        = self._iso_model.score_samples(X_scaled)    # more negative = more anomalous
        anomaly_score = 1.0 - ((scores - scores.min()) / (scores.max() - scores.min() + 1e-9))

        df = df.copy()
        df["IF_Anomaly"] = (raw_preds == -1)
        df["IF_Score"]   = np.round(anomaly_score * 100, 1)
        return df

    def train_custom_isolation_forest(
        self,
        df: pd.DataFrame,
        feature_cols: list = None,
        contamination: float = 0.05,
        n_estimators: int = 100,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Trains IsolationForest on any custom DataFrame (e.g. Kaggle datasets / CSV uploads).
        Dynamically handles numeric feature selection, missing values, and scaling.
        Returns (scored_df: pd.DataFrame, metrics: Dict).
        """
        if not SKLEARN_AVAILABLE:
            df = df.copy()
            df["IF_Anomaly"] = False
            df["IF_Score"]   = 0.0
            return df, {"error": "scikit-learn not installed. Run: pip install scikit-learn"}

        if df.empty:
            return df, {"error": "Uploaded dataset is empty."}

        # Auto-select numeric features if none provided
        if not feature_cols:
            feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not feature_cols:
            df = df.copy()
            df["IF_Anomaly"] = False
            df["IF_Score"]   = 0.0
            return df, {"error": "No numeric feature columns found in dataset."}

        df_clean = df.copy()
        # Impute missing values with column median
        for c in feature_cols:
            if df_clean[c].isnull().any():
                df_clean[c] = df_clean[c].fillna(df_clean[c].median())

        X = df_clean[feature_cols].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        iso_model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42,
            n_jobs=None,
        )
        raw_preds = iso_model.fit_predict(X_scaled)
        scores = iso_model.score_samples(X_scaled)

        # Normalize score to 0–100% (higher = more anomalous)
        s_min, s_max = scores.min(), scores.max()
        denom = (s_max - s_min) if (s_max != s_min) else 1e-9
        anomaly_score = 1.0 - ((scores - s_min) / denom)

        df_scored = df.copy()
        df_scored["IF_Anomaly"] = (raw_preds == -1)
        df_scored["IF_Score"]   = np.round(anomaly_score * 100, 1)

        anomalies_count = int((raw_preds == -1).sum())

        metrics = {
            "model":           "IsolationForest (Custom Dataset)",
            "n_estimators":    n_estimators,
            "contamination":   contamination,
            "training_rows":   len(df),
            "features_used":   feature_cols,
            "anomalies_found": anomalies_count,
            "anomaly_pct":     round((anomalies_count / max(1, len(df))) * 100, 2),
            "avg_risk_score":  round(float(df_scored["IF_Score"].mean()), 1),
            "max_risk_score":  round(float(df_scored["IF_Score"].max()), 1),
        }
        return df_scored, metrics

    # ── Assistant Guidance (legacy hook) ─────────────────────────────
    def get_assistant_guidance(
        self, context_mode: str, valve_state: int, hvac_state: str
    ) -> str:
        if context_mode == "simulation":
            if valve_state == 100 and "OPTIMIZED" in hvac_state:
                return (
                    "All parameters nominal. Try injecting a failure scenario "
                    "from the Telemetry tab to see the full incident response chain."
                )
            return (
                "Incident isolated. The IsolationForest model flagged the deviation, "
                "the RCA engine identified root cause, and automated mitigation "
                "was triggered within the response SLA."
            )
        return (
            "Secure Ingestion Vault active. Drop your CSV/XLSX file to run an "
            "automated anomaly audit. All PII is hashed locally before storage."
        )

    def generate_sample_kaggle_dataset(self) -> pd.DataFrame:
        """Generates a sample industrial turbine sensor dataset (Kaggle-style)."""
        np.random.seed(123)
        n = 200
        timestamps = pd.date_range("2026-07-01", periods=n, freq="15min")
        vibration_mm_s = np.random.normal(2.5, 0.4, n)
        bearing_temp_c = np.random.normal(55.0, 3.2, n)
        rotational_rpm = np.random.normal(3000, 45, n)
        lubricant_flow = np.random.normal(12.0, 0.8, n)
        power_kw = np.random.normal(450.0, 15.0, n)

        # Inject anomaly spikes (approx 4% contamination)
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