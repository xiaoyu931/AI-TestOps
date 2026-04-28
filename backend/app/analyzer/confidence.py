CONFIDENCE_SCORE_MAP = {
    "high": 0.9,
    "medium": 0.6,
    "low": 0.3,
}


def normalize_confidence(value: str | None) -> str:
    if not value:
        return "low"

    normalized = str(value).strip().lower()

    if normalized in CONFIDENCE_SCORE_MAP:
        return normalized

    return "low"


def confidence_to_score(value: str | None) -> float:
    normalized = normalize_confidence(value)
    return CONFIDENCE_SCORE_MAP.get(normalized, 0.3)
