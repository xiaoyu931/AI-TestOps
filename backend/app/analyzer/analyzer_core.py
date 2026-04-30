from typing import Optional

from sqlalchemy.orm import Session

from app.analyzer.error_normalizer import normalize_error, shorten_text
from app.analyzer.knowledge_mapper import build_knowledge_result, find_knowledge
from app.analyzer.rule_matcher import match_rule
from app.schemas.analyzer_schema import AnalyzerResult


UNKNOWN_SOLUTION = (
    "Review the detailed error log and classify this issue into a reusable rule "
    "if it happens repeatedly."
)


def build_unknown_result(error_text: Optional[str]) -> dict:
    result = AnalyzerResult(
        matched=False,
        error_type="OTHER",
        root_cause="Unknown",
        solution=UNKNOWN_SOLUTION,
        category="UNKNOWN",
        confidence="low",
        confidence_score=0.3,
        matched_rule_id=None,
        matched_pattern=None,
        rule_source=None,
        knowledge_source=None,
        error_summary=shorten_text(error_text),
    )

    return result.model_dump()


def analyze_error(db: Session, error_text: Optional[str]) -> dict:
    normalized = normalize_error(error_text)

    if not normalized["clean_error"]:
        return build_unknown_result(error_text)

    rule = match_rule(db, normalized["clean_error"])

    if not rule:
        return build_unknown_result(normalized["raw_error"])

    knowledge = find_knowledge(
        db=db,
        error_type=rule.error_type,
        root_cause=rule.root_cause,
    )
    knowledge_result = build_knowledge_result(knowledge)

    result = AnalyzerResult(
        matched=True,
        error_type=rule.error_type,
        root_cause=rule.root_cause,
        solution=knowledge_result["solution"],
        category=knowledge_result["category"],
        confidence=knowledge_result["confidence"],
        confidence_score=knowledge_result["confidence_score"],
        matched_rule_id=rule.id,
        matched_pattern=rule.pattern,
        rule_source=rule.source,
        knowledge_source=knowledge_result["knowledge_source"],
        error_summary=shorten_text(normalized["raw_error"]),
    )

    return result.model_dump()
