from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComponentParameterCreateRequest(BaseModel):
    component_id: int
    parameter_id: int
    sort: Optional[int] = 1
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ComponentParameterUpdateRequest(BaseModel):
    component_id: int
    parameter_id: int
    sort: Optional[int] = 1
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ComponentParameterItem(BaseModel):
    id: int
    component_id: int
    parameter_id: int
    sort: Optional[int]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: int
    active: bool
    create_date: Optional[datetime]

    class Config:
        from_attributes = True


class ComponentParameterListResponse(BaseModel):
    total: int
    data: list[ComponentParameterItem]


class ComponentParameterDetailResponse(BaseModel):
    id: int
    component_id: int
    parameter_id: int
    sort: Optional[int]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: Optional[int]
    create_date: Optional[datetime]
    update_date: Optional[datetime]

    class Config:
        from_attributes = True