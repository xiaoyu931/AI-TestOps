from pydantic import BaseModel
from typing import List, Optional


class SummaryItem(BaseModel):
    total: int
    failed: int
    success: int
    success_rate: float


class StageDistributionItem(BaseModel):
    stage: str
    count: int


class ErrorTypeDistributionItem(BaseModel):
    error_type: str
    count: int


class PatternItem(BaseModel):
    pattern: str
    title: str
    suggestion: str
    count: int
    percent: float


class FailureDetailItem(BaseModel):
    test_case_exe_id: int
    batch_id: Optional[int] = None
    cfg_id: Optional[int] = None
    uipath_case_name: Optional[str] = None
    stage: str
    state: int
    state_text: str
    error_type: str
    error_reason: Optional[str] = None
    suggestion: Optional[str] = None
    error_pattern: Optional[str] = None
    error_summary: Optional[str] = None
    component_name: Optional[str] = None
    create_date: Optional[str] = None
    finish_date: Optional[str] = None


class FailureAnalysisResponse(BaseModel):
    summary: SummaryItem
    stage_distribution: List[StageDistributionItem]
    error_type_distribution: List[ErrorTypeDistributionItem]
    error_pattern_distribution: List[PatternItem]
    top_issue: Optional[PatternItem] = None
    failure_details: List[FailureDetailItem]