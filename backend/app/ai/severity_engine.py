"""Severity engine: converts contextual signals into an impact score and level."""
from typing import Dict, Any

BUSINESS_CRITICAL_SERVICES = {"payment service", "payment api", "database", "api gateway", "authentication service"}


class SeverityEngine:
    """Calculates incident severity (LOW/MEDIUM/HIGH/CRITICAL) from context."""

    def calculate(self, context: Dict[str, Any], affected_services_count: int = 1) -> Dict[str, Any]:
        """Return dict with `impact_score` (0-100) and `severity` label."""
        latest = context.get("latest_metric", {})

        score = 0.0

        # Number of affected services
        score += min(20, affected_services_count * 7)

        # Error rate
        error_rate = float(latest.get("error_rate", 0) or 0)
        score += min(20, error_rate * 1.5)

        # API latency
        latency = float(latest.get("api_latency", 0) or 0)
        score += min(15, (latency / 1000) * 15)

        # Anomaly score contribution
        score += min(20, context.get("max_anomaly_score", 0) * 0.2)

        # Business-critical service bump
        service_name = (context.get("service_name") or "").lower()
        if service_name in BUSINESS_CRITICAL_SERVICES:
            score += 15

        # Error frequency (volume of ERROR/CRITICAL logs)
        score += min(10, context.get("error_frequency", 0) * 1.5)

        score = round(min(100.0, score), 1)
        severity = self._score_to_severity(score)

        return {"impact_score": score, "severity": severity}

    def _score_to_severity(self, score: float) -> str:
        if score <= 25:
            return "LOW"
        if score <= 50:
            return "MEDIUM"
        if score <= 75:
            return "HIGH"
        return "CRITICAL"
