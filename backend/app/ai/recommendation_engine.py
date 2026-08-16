"""Recommendation engine: maps a detected root cause to concrete action steps."""
from typing import List, Dict, Any

RECOMMENDATIONS: Dict[str, List[str]] = {
    "DATABASE_CONNECTION_EXHAUSTION": [
        "Inspect the database connection pool configuration.",
        "Check the number of active database connections against the pool limit.",
        "Review the most recent deployment for connection-handling changes.",
        "Verify connection timeout and retry configuration.",
        "Consider temporarily increasing the connection pool size as a mitigation.",
    ],
    "MEMORY_OVERLOAD": [
        "Inspect memory-intensive processes on the affected service.",
        "Check for memory leaks in recently deployed code paths.",
        "Review the most recent deployment for changes affecting memory usage.",
        "Restart the affected service only if immediate relief is required.",
        "Add memory usage alerts at a lower threshold to catch this earlier.",
    ],
    "HIGH_CPU_USAGE": [
        "Identify which processes or threads are consuming the most CPU.",
        "Check for inefficient queries, loops, or recent code changes.",
        "Consider horizontal scaling or autoscaling for the affected service.",
        "Review scheduled jobs or batch tasks that may be overlapping.",
    ],
    "API_TIMEOUT": [
        "Check downstream service response times and dependency health.",
        "Review API gateway and service timeout configuration.",
        "Inspect recent traffic patterns for unusual spikes.",
        "Verify circuit breaker and retry policies are configured correctly.",
    ],
    "NETWORK_FAILURE": [
        "Check network connectivity and DNS resolution between services.",
        "Review load balancer and firewall configuration for recent changes.",
        "Inspect network usage metrics for saturation.",
        "Verify service mesh / proxy health if applicable.",
    ],
    "BAD_DEPLOYMENT": [
        "Compare the current release with the previous stable version.",
        "Review deployment logs for errors during rollout.",
        "Check configuration and environment variable changes in this release.",
        "Consider rolling back the deployment after validating impact.",
    ],
    "DEPENDENCY_FAILURE": [
        "Identify which upstream or downstream dependency is failing.",
        "Check the health and status page of the affected dependency.",
        "Review circuit breaker and fallback behavior for this dependency.",
        "Contact the owning team of the dependent service if external.",
    ],
    "DISK_SPACE_EXHAUSTION": [
        "Identify what is consuming disk space (logs, temp files, core dumps).",
        "Clear or rotate old log files and temporary data.",
        "Increase disk allocation if usage growth is expected to continue.",
        "Add disk usage alerting at a lower threshold.",
    ],
    "UNKNOWN": [
        "Manually review recent logs, metrics, and deployments for the affected service.",
        "Check dependent services for cascading effects.",
        "Escalate to the on-call engineer for the affected service if impact is ongoing.",
    ],
}


class RecommendationEngine:
    """Generates recommended remediation steps for a given root cause."""

    def recommend(self, root_cause: str) -> List[str]:
        return RECOMMENDATIONS.get(root_cause, RECOMMENDATIONS["UNKNOWN"])
