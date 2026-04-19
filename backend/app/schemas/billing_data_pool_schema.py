from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ======================
# 创建
# ======================
class BillingDataCreateRequest(BaseModel):

    cfg_id: str
    test_case_name: Optional[str] = ""

    cust_id: str
    account_id: Optional[str] = ""
    order_id: Optional[str] = ""

    class Config:
        from_attributes = True
        extra = "ignore"


# ======================
# 返回项
# ======================
class BillingDataItem(BaseModel):

    id: int

    cfg_id: str
    test_case_name: Optional[str]

    cust_id: str
    account_id: Optional[str]
    order_id: Optional[str]

    status: int
    used: bool

    create_time: Optional[datetime]
    used_time: Optional[datetime]

    class Config:
        from_attributes = True


# ======================
# 列表
# ======================
class BillingDataListResponse(BaseModel):

    total: int
    data: list[BillingDataItem]