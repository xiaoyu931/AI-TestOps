from pydantic import BaseModel
from typing import Optional


# ======================
# 创建 SQL 模板
# ======================
class AutoSqlCreateRequest(BaseModel):

    sql_name: str
    db: str
    sql_content: str

    class Config:
        from_attributes = True
        extra = "ignore"


# ======================
# 返回项
# ======================
class AutoSqlItem(BaseModel):

    sql_name: str
    db: str
    sql_content: str

    class Config:
        from_attributes = True


# ======================
# 列表返回
# ======================
class AutoSqlListResponse(BaseModel):

    total: int
    data: list[AutoSqlItem]


# ======================
# 单个返回
# ======================
class AutoSqlDetailResponse(BaseModel):

    sql_name: str
    db: str
    sql_content: str

    class Config:
        from_attributes = True