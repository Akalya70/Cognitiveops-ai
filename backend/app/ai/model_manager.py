"""Model manager: orchestrates the full AI analysis pipeline.

Ties together the context engine, root cause engine, severity engine, and
recommendation engine into a single `analyze()` call. Designed so that an
external LLM could later be plugged in to enrich or re-rank results without
changing the pipeline's public interface.
"""
from typing import List, Dict, Any

from app.ai.context_engine import ContextEngine
from app.ai.root_cause_engine import RootCauseEngine
from app.ai.severity_engine import SeverityEngine
from app.ai.recommendation_engine import RecommendationEngine


class ModelManager:
    """Single entry point for running the full incident analysis pipeline."""

    def __init__(self):
        self.context_engine = ContextEngine()
        self.root_cause_engine = RootCauseEngine()
        self.severity_engine = SeverityEngine()
        self.recommendation_engine = RecommendationEngine()
        # Placeholder for future optional LLM integration.
        self.llm_client = None

    def analyze(
        self,
        service_name: str,
        current_metrics: List[Dict[str, Any]],
        historical_metrics: List[Dict[str, Any]],
        logs: List[Dict[str, Any]],
        deployments: List[Dict[str, Any]],
        recent_incidents: List[Dict[str, Any]],
        affected_services_count: int = 1,
        window_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Run the complete analysis pipeline and return a structured result."""
        context = self.context_engine.build_context(
            service_name=service_name,
            current_metrics=current_metrics,
            historical_metrics=historical_metrics,
            logs=logs,
            deployments=deployments,
            recent_incidents=recent_incidents,
            window_minutes=window_minutes,
        )

        root_cause_result = self.root_cause_engine.analyze(context)
        severity_result = self.severity_engine.calculate(context, affected_services_count)
        recommendations = self.recommendation_engine.recommend(root_cause_result["root_cause"])

        result = {
            "root_cause": root_cause_result["root_cause"],
            "confidence": root_cause_result["confidence"],
            "contributing_factors": root_cause_result["all_scores"],
            "evidence": root_cause_result["evidence"],
            "severity": severity_result["severity"],
            "impact_score": severity_result["impact_score"],
            "recommendations": recommendations,
            "timeline": context["timeline"],
        }

        # Optional future hook: if an LLM client is configured, enrich the result.
        if self.llm_client is not None:
            result = self._enrich_with_llm(result, context)

        return result

    def _enrich_with_llm(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder hook for optional LLM-based enrichment. Not used by default."""
        return result


# Singleton instance used across the application
model_manager = ModelManager()
