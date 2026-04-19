from pydantic import BaseModel
from typing import Optional


# ======================
# 创建
# ======================
class ProvisionParameterCreateRequest(BaseModel):

    action_id: Optional[int] = None
    platform_code: Optional[str] = ""

    provision_type: Optional[str] = ""

    provision_mandatory_param: Optional[str] = ""
    provision_optional_param: Optional[str] = ""

    state: Optional[str] = "U"

    ext1: Optional[str] = ""
    ext2: Optional[str] = ""
    ext3: Optional[str] = ""

    product_line: Optional[str] = ""
    veris_code_status: Optional[str] = ""
    platform: Optional[str] = ""

    class Config:
        from_attributes = True
        extra = "ignore"


# ======================
# 返回项
# ======================
class ProvisionParameterItem(BaseModel):

    id: int
    action_id: Optional[int]

    platform_code: Optional[str]
    provision_type: Optional[str]

    mandatory: Optional[str]
    optional: Optional[str]

    state: Optional[str]
    active: bool

    product_line: Optional[str]

    class Config:
        from_attributes = True


# ======================
# 列表
# ======================
class ProvisionParameterListResponse(BaseModel):

    total: int
    data: list[ProvisionParameterItem]


# ======================
# 详情
# ======================
class ProvisionParameterDetailResponse(BaseModel):

    id: int
    action_id: Optional[int]

    platform_code: Optional[str]
    provision_type: Optional[str]

    mandatory: Optional[str]
    optional: Optional[str]

    state: Optional[str]

    ext1: Optional[str]
    ext2: Optional[str]
    ext3: Optional[str]

    product_line: Optional[str]
    veris_code_status: Optional[str]
    platform: Optional[str]

    class Config:
        from_attributes = True