import re
from typing import Optional

from sqlalchemy.orm import Session

from app.models.error_rule_model import ErrorRule


def _contains_keyword(error_text: str, keyword: Optional[str]) -> bool:
    if not keyword:
        return True

    return keyword.strip().lower() in error_text


def _matches_pattern(error_text: str, pattern: Optional[str]) -> bool:
    if not pattern:
        return False

    pattern_text = pattern.strip()
    if not pattern_text:
        return False

    try:
        return re.search(pattern_text, error_text, flags=re.IGNORECASE) is not None
    except re.error:
        return pattern_text.lower() in error_text


def load_active_rules(db: Session) -> list[ErrorRule]:
    return (
        db.query(ErrorRule)
        .filter(ErrorRule.is_active == True)
        .order_by(ErrorRule.priority.desc(), ErrorRule.id.asc())
        .all()
    )


def match_rule(db: Session, clean_error: str) -> Optional[ErrorRule]:
    rules = load_active_rules(db)

    for rule in rules:
        pattern_matched = _matches_pattern(clean_error, rule.pattern)
        match_text_matched = _contains_keyword(clean_error, rule.match_text)

        if pattern_matched and match_text_matched:
            return rule

    return None
