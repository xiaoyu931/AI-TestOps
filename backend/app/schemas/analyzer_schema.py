from typing import Optional

from pydantic import BaseModel


class AnalyzerResult(BaseModel):
    matched: bool

    error_type: str
    root_cause: str
    solution: str
    category: str

    confidence: str
    confidence_score: float

    matched_rule_id: Optional[int] = None
    matched_pattern: Optional[str] = None

    rule_source: Optional[str] = None
    knowledge_source: Optional[str] = None

    error_summary: Optional[str] = None

    class Config:
        from_attributes = True
