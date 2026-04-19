from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TemplateRelCreateRequest(BaseModel):
    test_case_template_id: int
    pre_test_case_template_id: int
    tenant_id: Optional[int] = 21
    state: Optional[int] = 1


class TemplateRelUpdateRequest(BaseModel):
    test_case_template_id: int
    pre_test_case_template_id: int
    tenant_id: Optional[int] = 21
    state: Optional[int] = 1


class TemplateRelItem(BaseModel):
    rel_id: int
    test_case_template_id: int
    pre_test_case_template_id: int
    tenant_id: Optional[int] = None
    state: Optional[int] = 0
    create_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateRelListResponse(BaseModel):
    total: int
    data: List[TemplateRelItem]


class TemplateRelDetailResponse(BaseModel):
    rel_id: int
    test_case_template_id: int
    pre_test_case_template_id: int
    tenant_id: Optional[int] = None
    state: Optional[int] = 0
    create_date: Optional[datetime] = None

    class Config:
        from_attributes = True