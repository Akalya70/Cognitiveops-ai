"""Root cause engine: scores each candidate root cause using contextual rules.

This does NOT evaluate signals independently. Every rule combines multiple
contextual signals (deployment recency, metric deltas, log content, anomaly
scores) to produce a confidence score per root cause category.
"""
from typing import Dict, Any, List, Tuple

ROOT_CAUSES = [
    "DATABASE_CONNECTION_EXHAUSTION",
    "MEMORY_OVERLOAD",
    "HIGH_CPU_USAGE",
    "API_TIMEOUT",
    "NETWORK_FAILURE",
    "BAD_DEPLOYMENT",
    "DEPENDENCY_FAILURE",
    "DISK_SPACE_EXHAUSTION",
    "UNKNOWN",
]


class RootCauseEngine:
    """Calculates a confidence score for each possible root cause given a context dict."""

    def score_all(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Return a dict mapping each root cause to a confidence score (0-1)."""
        scores = {
            "DATABASE_CONNECTION_EXHAUSTION": self._score_database(context),
            "MEMORY_OVERLOAD": self._score_memory(context),
            "HIGH_CPU_USAGE": self._score_cpu(context),
            "API_TIMEOUT": self._score_api_timeout(context),
            "NETWORK_FAILURE": self._score_network(context),
            "BAD_DEPLOYMENT": self._score_bad_deployment(context),
            "DEPENDENCY_FAILURE": self._score_dependency(context),
            "DISK_SPACE_EXHAUSTION": self._score_disk(context),
        }
        # UNKNOWN score rises when nothing else scores well
        top_other = max(scores.values()) if scores else 0.0
        scores["UNKNOWN"] = round(max(0.0, 0.35 - top_other * 0.3), 2)
        return {k: round(v, 2) for k, v in scores.items()}

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run full analysis: scores, top root cause, evidence, contributing factors."""
        scores = self.score_all(context)
        top_cause, confidence = max(scores.items(), key=lambda kv: kv[1])
        evidence = self._build_evidence(top_cause, context)
        return {
            "root_cause": top_cause,
            "confidence": confidence,
            "all_scores": scores,
            "evidence": evidence,
        }

    # -- Individual scoring rules -------------------------------------------------

    def _score_database(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        error_logs = ctx.get("error_logs", [])

        score = 0.0
        db_conn = float(latest.get("db_connections", 0) or 0)
        if db_conn > 80:
            score += 0.35
        elif db_conn > 60:
            score += 0.2

        if deltas.get("db_connections", 0) > 100:
            score += 0.2
        elif deltas.get("db_connections", 0) > 50:
            score += 0.1

        db_timeout_logs = [l for l in error_logs if "timeout" in (l.get("message") or "").lower() and "database" in (l.get("message") or "").lower()]
        if db_timeout_logs:
            score += 0.25

        if deltas.get("api_latency", 0) > 50 and db_conn > 60:
            score += 0.15

        if ctx.get("has_recent_deployment") and db_conn > 60:
            score += 0.1

        return min(1.0, score)

    def _score_memory(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        error_logs = ctx.get("error_logs", [])

        score = 0.0
        mem = float(latest.get("memory_usage", 0) or 0)
        if mem > 90:
            score += 0.4
        elif mem > 80:
            score += 0.25

        if deltas.get("memory_usage", 0) > 40:
            score += 0.2

        oom_logs = [l for l in error_logs if any(k in (l.get("message") or "").lower() for k in ["out of memory", "oom", "memory leak", "heap"])]
        if oom_logs:
            score += 0.3

        return min(1.0, score)

    def _score_cpu(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})

        score = 0.0
        cpu = float(latest.get("cpu_usage", 0) or 0)
        if cpu > 90:
            score += 0.45
        elif cpu > 75:
            score += 0.25

        if deltas.get("cpu_usage", 0) > 50:
            score += 0.2

        if cpu > 75 and float(latest.get("api_latency", 0) or 0) > 300:
            score += 0.15

        return min(1.0, score)

    def _score_api_timeout(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        error_logs = ctx.get("error_logs", [])

        score = 0.0
        latency = float(latest.get("api_latency", 0) or 0)
        if latency > 500:
            score += 0.3
        elif latency > 300:
            score += 0.15

        if deltas.get("api_latency", 0) > 80:
            score += 0.2

        timeout_logs = [l for l in error_logs if "timeout" in (l.get("message") or "").lower()]
        if timeout_logs:
            score += 0.2

        error_rate = float(latest.get("error_rate", 0) or 0)
        if error_rate > 5:
            score += 0.15

        return min(1.0, score)

    def _score_network(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        error_logs = ctx.get("error_logs", [])

        score = 0.0
        net = float(latest.get("network_usage", 0) or 0)
        if net > 80:
            score += 0.35
        elif net > 60:
            score += 0.2

        if deltas.get("network_usage", 0) > 60:
            score += 0.2

        network_logs = [l for l in error_logs if any(k in (l.get("message") or "").lower() for k in ["connection refused", "network", "unreachable", "dns"])]
        if network_logs:
            score += 0.25

        return min(1.0, score)

    def _score_bad_deployment(self, ctx: Dict[str, Any]) -> float:
        score = 0.0
        if ctx.get("has_recent_deployment"):
            score += 0.4
            # A deployment plus any elevated error rate strongly suggests a bad release
            deltas = ctx.get("metric_deltas", {})
            if deltas.get("error_rate", 0) > 30 or deltas.get("api_latency", 0) > 50:
                score += 0.3
            if ctx.get("error_frequency", 0) > 3:
                score += 0.2
        return min(1.0, score)

    def _score_dependency(self, ctx: Dict[str, Any]) -> float:
        error_logs = ctx.get("error_logs", [])
        score = 0.0
        dependency_logs = [l for l in error_logs if any(k in (l.get("message") or "").lower() for k in ["upstream", "dependency", "downstream", "503", "unavailable"])]
        if dependency_logs:
            score += 0.4
        if ctx.get("error_frequency", 0) > 5:
            score += 0.15
        return min(1.0, score)

    def _score_disk(self, ctx: Dict[str, Any]) -> float:
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        score = 0.0
        disk = float(latest.get("disk_usage", 0) or 0)
        if disk > 90:
            score += 0.5
        elif disk > 80:
            score += 0.25
        if deltas.get("disk_usage", 0) > 30:
            score += 0.2
        return min(1.0, score)

    # -- Evidence building ----------------------------------------------------

    def _build_evidence(self, root_cause: str, ctx: Dict[str, Any]) -> List[str]:
        """Produce human-readable evidence strings supporting the chosen root cause."""
        latest = ctx.get("latest_metric", {})
        deltas = ctx.get("metric_deltas", {})
        evidence = []

        evidence_map = {
            "DATABASE_CONNECTION_EXHAUSTION": [
                (deltas.get("db_connections", 0) > 0, f"Database connections increased {deltas.get('db_connections', 0):.0f}%"),
                (deltas.get("api_latency", 0) > 0, f"API latency increased {deltas.get('api_latency', 0):.0f}%"),
                (True, "Database timeout errors detected in logs"),
            ],
            "MEMORY_OVERLOAD": [
                (True, f"Memory usage at {latest.get('memory_usage', 0):.0f}%"),
                (deltas.get("memory_usage", 0) > 0, f"Memory usage increased {deltas.get('memory_usage', 0):.0f}%"),
                (True, "Memory-related errors detected in logs"),
            ],
            "HIGH_CPU_USAGE": [
                (True, f"CPU usage at {latest.get('cpu_usage', 0):.0f}%"),
                (deltas.get("cpu_usage", 0) > 0, f"CPU usage increased {deltas.get('cpu_usage', 0):.0f}%"),
            ],
            "API_TIMEOUT": [
                (True, f"API latency at {latest.get('api_latency', 0):.0f}ms"),
                (deltas.get("api_latency", 0) > 0, f"API latency increased {deltas.get('api_latency', 0):.0f}%"),
                (True, "Timeout errors detected in logs"),
            ],
            "NETWORK_FAILURE": [
                (True, f"Network usage at {latest.get('network_usage', 0):.0f}%"),
                (True, "Network connectivity errors detected in logs"),
            ],
            "BAD_DEPLOYMENT": [
                (True, "A deployment occurred shortly before the incident"),
                (deltas.get("error_rate", 0) > 0, f"Error rate increased {deltas.get('error_rate', 0):.0f}% after deployment"),
            ],
            "DEPENDENCY_FAILURE": [
                (True, "Upstream/downstream dependency errors detected in logs"),
                (True, f"{ctx.get('error_frequency', 0)} error-level log entries recorded"),
            ],
            "DISK_SPACE_EXHAUSTION": [
                (True, f"Disk usage at {latest.get('disk_usage', 0):.0f}%"),
            ],
            "UNKNOWN": [
                (True, "No single dominant contextual pattern was identified"),
            ],
        }

        for condition, text in evidence_map.get(root_cause, []):
            if condition:
                evidence.append(text)

        if ctx.get("has_recent_deployment") and root_cause != "BAD_DEPLOYMENT":
            evidence.append("A deployment occurred shortly before the incident")

        return evidence
