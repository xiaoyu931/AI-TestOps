from typing import Optional

from sqlalchemy.orm import Session

from app.analyzer.confidence import confidence_to_score, normalize_confidence
from app.models.error_knowledge_model import ErrorKnowledge


def find_knowledge(
    db: Session,
    error_type: Optional[str],
    root_cause: Optional[str],
) -> Optional[ErrorKnowledge]:
    if not error_type or not root_cause:
        return None

    return (
        db.query(ErrorKnowledge)
        .filter(ErrorKnowledge.error_type == error_type)
        .filter(ErrorKnowledge.root_cause == root_cause)
        .first()
    )


def build_knowledge_result(knowledge: Optional[ErrorKnowledge]) -> dict:
    if not knowledge:
        return {
            "solution": "Review the detailed error log and add reusable rules if this issue happens repeatedly.",
            "category": "UNKNOWN",
            "confidence": "low",
            "confidence_score": 0.3,
            "knowledge_source": None,
        }

    confidence = normalize_confidence(knowledge.confidence)

    return {
        "solution": knowledge.solution,
        "category": knowledge.category,
        "confidence": confidence,
        "confidence_score": confidence_to_score(confidence),
        "knowledge_source": knowledge.source,
    }
