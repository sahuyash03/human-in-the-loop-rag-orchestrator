from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class EvaluationResult:
    query_id: str
    grounding_score: float
    relevance_score: float
    routing_decision: str
    escalation_reason: Optional[str] = None


class DecisionGate:
    """
    Evaluates generated output quality against strict enterprise SLAs.
    Prevents hallucinations from reaching end-users by enforcing dual-metric thresholds.
    """
    def __init__(self, min_grounding: float = 0.85, min_relevance: float = 0.88):
        self.min_grounding = min_grounding
        self.min_relevance = min_relevance

    def evaluate(self, query_id: str, grounding_score: float, relevance_score: float) -> EvaluationResult:
        reasons = []
        if grounding_score < self.min_grounding:
            reasons.append(f"Grounding score {grounding_score:.2f} < threshold {self.min_grounding}")
        if relevance_score < self.min_relevance:
            reasons.append(f"Relevance score {relevance_score:.2f} < threshold {self.min_relevance}")

        if reasons:
            return EvaluationResult(
                query_id=query_id,
                grounding_score=grounding_score,
                relevance_score=relevance_score,
                routing_decision="ESCALATE_TO_SME",
                escalation_reason=" | ".join(reasons)
            )

        return EvaluationResult(
            query_id=query_id,
            grounding_score=grounding_score,
            relevance_score=relevance_score,
            routing_decision="AUTO_DELIVERY",
            escalation_reason=None
        )


class HumanReviewQueue:
    """Mock interface for dispatching low-confidence answers to SME reviewers."""
    @staticmethod
    def enqueue(payload: Dict[str, Any]) -> str:
        # In production: pushes ticket to Slack webhook, Zendesk, or custom review dashboard
        ticket_id = f"REV-{payload['query_id'][:8].upper()}"
        return ticket_id