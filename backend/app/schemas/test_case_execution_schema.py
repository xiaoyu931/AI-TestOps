from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExecutionBase(BaseModel):
    TEST_CASE_EXE_ID: Optional[int]
    CFG_ID: Optional[int]
    TEST_CASE_NAME: Optional[str]
    EXECUTION_MACHINE: Optional[str]
    STATE: Optional[int]
    TASK_STATUS: Optional[int]
    CREATE_DATE: Optional[datetime]
    FINISH_DATE: Optional[datetime]

    class Config:
        from_attributes = True   # ✅ Pydantic v2 写法


# ✅ 查询
class ExecutionQueryRequest(BaseModel):
    test_case_exe_id: Optional[int]
    cfg_id: Optional[int]
    test_case_name: Optional[str]
    execution_machine: Optional[str]
    state: Optional[int]

    page: int = 1
    page_size: int = 10


# ✅ 返回
class ExecutionListResponse(BaseModel):
    total: int
    data: list[ExecutionBase]


# ❗ 如果你 API 里用了 create（但其实你现在不需要）
class ExecutionCreateRequest(BaseModel):
    TEST_CASE_NAME: Optional[str]