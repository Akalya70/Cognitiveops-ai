"""Anomaly detection over service metrics.

Uses an Isolation Forest model when enough historical data is available,
and falls back to simple statistical (z-score / threshold) detection
when the dataset is too small to train a reliable model.
"""
from typing import List, Dict, Any
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
except ImportError:  # pragma: no cover - sklearn should always be installed
    IsolationForest = None

FEATURE_COLUMNS = [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "network_usage",
    "api_latency",
    "error_rate",
    "db_connections",
]

MIN_RECORDS_FOR_MODEL = 30

# Reasonable "healthy" thresholds used for statistical fallback detection.
STATIC_THRESHOLDS = {
    "cpu_usage": 80.0,
    "memory_usage": 85.0,
    "disk_usage": 90.0,
    "network_usage": 80.0,
    "api_latency": 500.0,  # ms
    "error_rate": 5.0,  # percent
    "db_connections": 80.0,  # percent of pool
}


class AnomalyDetector:
    """Detects anomalous metric records using ML when possible."""

    def __init__(self):
        self.model = None
        self.trained = False
        self.feature_means = {}
        self.feature_stds = {}

    def _metrics_to_matrix(self, metrics: List[Dict[str, Any]]) -> np.ndarray:
        return np.array(
            [[float(m.get(col, 0.0) or 0.0) for col in FEATURE_COLUMNS] for m in metrics]
        )

    def train(self, historical_metrics: List[Dict[str, Any]]) -> bool:
        """Train the Isolation Forest on historical metric records.

        Returns True if a model was trained, False if it fell back to statistics.
        """
        if not historical_metrics or len(historical_metrics) < MIN_RECORDS_FOR_MODEL or IsolationForest is None:
            self._train_statistics(historical_metrics)
            self.trained = False
            return False

        matrix = self._metrics_to_matrix(historical_metrics)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42,
        )
        self.model.fit(matrix)
        self._train_statistics(historical_metrics)
        self.trained = True
        return True

    def _train_statistics(self, historical_metrics: List[Dict[str, Any]]) -> None:
        """Compute per-feature mean/std for use in statistical fallback scoring."""
        if not historical_metrics:
            self.feature_means = {col: 0.0 for col in FEATURE_COLUMNS}
            self.feature_stds = {col: 1.0 for col in FEATURE_COLUMNS}
            return

        matrix = self._metrics_to_matrix(historical_metrics)
        self.feature_means = {col: float(matrix[:, i].mean()) for i, col in enumerate(FEATURE_COLUMNS)}
        self.feature_stds = {
            col: float(matrix[:, i].std()) or 1.0 for i, col in enumerate(FEATURE_COLUMNS)
        }

    def score(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single metric record for anomalousness.

        Returns a dict with `anomaly_score` (0-100, higher = more anomalous),
        `is_anomaly` (bool), and `method` used.
        """
        if self.trained and self.model is not None:
            row = np.array([[float(metric.get(col, 0.0) or 0.0) for col in FEATURE_COLUMNS]])
            raw_score = self.model.decision_function(row)[0]  # higher = more normal
            prediction = self.model.predict(row)[0]  # -1 anomaly, 1 normal
            # Normalize raw_score (~ -0.5 to 0.5) into a 0-100 anomaly scale
            anomaly_score = float(np.clip((0.5 - raw_score) * 100, 0, 100))
            return {
                "anomaly_score": round(anomaly_score, 2),
                "is_anomaly": bool(prediction == -1),
                "method": "isolation_forest",
            }

        return self._statistical_score(metric)

    def _statistical_score(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scoring using z-scores against historical mean/std and static thresholds."""
        breached_thresholds = 0
        z_scores = []

        for col in FEATURE_COLUMNS:
            value = float(metric.get(col, 0.0) or 0.0)
            mean = self.feature_means.get(col, 0.0)
            std = self.feature_stds.get(col, 1.0)
            z = abs((value - mean) / std) if std else 0.0
            z_scores.append(z)

            if value >= STATIC_THRESHOLDS.get(col, float("inf")):
                breached_thresholds += 1

        avg_z = float(np.mean(z_scores)) if z_scores else 0.0
        # Combine z-score signal with threshold breaches into a 0-100 anomaly score
        anomaly_score = min(100.0, avg_z * 20 + breached_thresholds * 15)
        is_anomaly = anomaly_score >= 40 or breached_thresholds >= 2

        return {
            "anomaly_score": round(anomaly_score, 2),
            "is_anomaly": is_anomaly,
            "method": "statistical_threshold",
        }

    def score_batch(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score a batch of metric records."""
        return [self.score(m) for m in metrics]
