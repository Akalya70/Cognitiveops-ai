"""Context engine: assembles a unified, timestamp-ordered view of an incident.

Combines current + historical metrics, logs, deployments, and anomaly scores
into a single contextual timeline and a structured "context" dictionary that
downstream engines (root cause, severity, recommendation) consume.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.ai.anomaly_detector import AnomalyDetector


class ContextEngine:
    """Builds a contextual picture of what happened around a service/time window."""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()

    def build_context(
        self,
        service_name: str,
        current_metrics: List[Dict[str, Any]],
        historical_metrics: List[Dict[str, Any]],
        logs: List[Dict[str, Any]],
        deployments: List[Dict[str, Any]],
        recent_incidents: List[Dict[str, Any]],
        window_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Build the full context dictionary used for root cause analysis."""

        # Train anomaly detector on historical data, score current metrics
        self.anomaly_detector.train(historical_metrics)
        scored_metrics = []
        for m in current_metrics:
            score_result = self.anomaly_detector.score(m)
            scored_metrics.append({**m, **score_result})

        anomaly_scores = [m["anomaly_score"] for m in scored_metrics] if scored_metrics else [0.0]
        avg_anomaly_score = sum(anomaly_scores) / len(anomaly_scores)
        max_anomaly_score = max(anomaly_scores)

        error_logs = [l for l in logs if l.get("level") in ("ERROR", "CRITICAL")]
        error_frequency = len(error_logs)

        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        recent_deployments = [
            d for d in deployments if self._parse_ts(d.get("timestamp")) >= window_start
        ]

        timeline = self._build_timeline(
            scored_metrics, logs, deployments, window_start
        )

        latest_metric = current_metrics[-1] if current_metrics else {}
        first_metric = current_metrics[0] if current_metrics else {}

        context = {
            "service_name": service_name,
            "window_minutes": window_minutes,
            "current_metrics": scored_metrics,
            "latest_metric": latest_metric,
            "first_metric": first_metric,
            "avg_anomaly_score": round(avg_anomaly_score, 2),
            "max_anomaly_score": round(max_anomaly_score, 2),
            "detection_method": scored_metrics[0]["method"] if scored_metrics else "statistical_threshold",
            "error_logs": error_logs,
            "error_frequency": error_frequency,
            "total_logs": len(logs),
            "recent_deployments": recent_deployments,
            "has_recent_deployment": len(recent_deployments) > 0,
            "recent_incidents": recent_incidents,
            "timeline": timeline,
            "metric_deltas": self._compute_deltas(first_metric, latest_metric),
        }
        return context

    def _parse_ts(self, ts) -> datetime:
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                return datetime.min
        return datetime.min

    def _compute_deltas(self, first: Dict[str, Any], latest: Dict[str, Any]) -> Dict[str, float]:
        """Compute percentage change between the first and latest metric snapshot."""
        deltas = {}
        for col in ["cpu_usage", "memory_usage", "api_latency", "error_rate", "db_connections", "network_usage", "disk_usage"]:
            start = float(first.get(col, 0.0) or 0.0)
            end = float(latest.get(col, 0.0) or 0.0)
            if start == 0:
                deltas[col] = 100.0 if end > 0 else 0.0
            else:
                deltas[col] = round(((end - start) / start) * 100, 1)
        return deltas

    def _build_timeline(
        self,
        scored_metrics: List[Dict[str, Any]],
        logs: List[Dict[str, Any]],
        deployments: List[Dict[str, Any]],
        window_start: datetime,
    ) -> List[Dict[str, Any]]:
        """Merge deployments, error logs, and anomaly spikes into one ordered timeline."""
        events = []

        for d in deployments:
            ts = self._parse_ts(d.get("timestamp"))
            if ts < window_start:
                continue
            events.append({
                "timestamp": d.get("timestamp"),
                "type": "deployment",
                "description": f"Deployment {d.get('version')} to {d.get('service_name')} ({d.get('status')})",
            })

        for log in logs:
            if log.get("level") not in ("ERROR", "CRITICAL", "WARNING"):
                continue
            events.append({
                "timestamp": log.get("timestamp"),
                "type": "log",
                "description": f"{log.get('level')}: {log.get('message')}",
            })

        for m in scored_metrics:
            if m.get("is_anomaly"):
                events.append({
                    "timestamp": m.get("timestamp"),
                    "type": "anomaly",
                    "description": f"Anomalous metrics detected (score {m.get('anomaly_score')})",
                })

        events.sort(key=lambda e: self._parse_ts(e["timestamp"]))
        return events
