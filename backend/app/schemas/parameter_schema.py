from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ParameterCreateRequest(BaseModel):
    parameter_name: str
    parameter_path: Optional[str] = ""
    parameter_type: Optional[str] = ""
    default_value: Optional[str] = ""
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ParameterUpdateRequest(BaseModel):
    parameter_name: str
    parameter_path: Optional[str] = ""
    parameter_type: Optional[str] = ""
    default_value: Optional[str] = ""
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ParameterItem(BaseModel):
    parameter_id: int
    parameter_name: str
    parameter_path: Optional[str]
    parameter_type: Optional[str]
    default_value: Optional[str]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: int
    active: bool
    create_date: Optional[datetime]

    class Config:
        from_attributes = True


class ParameterListResponse(BaseModel):
    total: int
    data: list[ParameterItem]


class ParameterDetailResponse(BaseModel):
    parameter_id: int
    parameter_name: str
    parameter_path: Optional[str]
    parameter_type: Optional[str]
    default_value: Optional[str]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: int
    create_date: Optional[datetime]
    update_date: Optional[datetime]

    class Config:
        from_attributes = True