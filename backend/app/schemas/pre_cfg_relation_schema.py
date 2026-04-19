from pydantic import BaseModel
from typing import Optional


# ======================
# 创建关系
# ======================
class PreCfgRelationCreateRequest(BaseModel):

    pre_cfg_id: str
    cfg_id: str

    class Config:
        from_attributes = True
        extra = "ignore"


# ======================
# 返回项
# ======================
class PreCfgRelationItem(BaseModel):

    pre_cfg_id: str
    cfg_id: str

    class Config:
        from_attributes = True


# ======================
# 列表
# ======================
class PreCfgRelationListResponse(BaseModel):

    total: int
    data: list[PreCfgRelationItem]