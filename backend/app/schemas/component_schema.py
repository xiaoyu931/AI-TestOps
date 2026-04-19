from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComponentCreateRequest(BaseModel):
    component_name: str
    component_type: Optional[str] = ""
    component_file: Optional[str] = ""
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ComponentUpdateRequest(BaseModel):
    component_name: str
    component_type: Optional[str] = ""
    component_file: Optional[str] = ""
    remark: Optional[str] = ""
    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    class Config:
        from_attributes = True
        extra = "ignore"


class ComponentItem(BaseModel):
    component_id: int
    component_name: str
    component_type: Optional[str]
    component_file: Optional[str]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: int
    active: bool
    create_date: Optional[datetime]

    class Config:
        from_attributes = True


class ComponentListResponse(BaseModel):
    total: int
    data: list[ComponentItem]


class ComponentDetailResponse(BaseModel):
    component_id: int
    component_name: str
    component_type: Optional[str]
    component_file: Optional[str]
    remark: Optional[str]
    tenant_id: Optional[str]
    state: int
    create_date: Optional[datetime]
    update_date: Optional[datetime]

    class Config:
        from_attributes = True