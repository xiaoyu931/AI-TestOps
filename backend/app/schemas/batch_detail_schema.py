from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BatchDetailListItem(BaseModel):
    batch_detail_id: int
    batch_id: Optional[int] = None
    cfg_id: Optional[int] = None

    uipath_case_exe_id: Optional[int] = None
    order_case_exe_id: Optional[int] = None
    verify_case_exe_id: Optional[int] = None

    status: Optional[int] = 0
    task_status: Optional[int] = 0

    create_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None


class BatchDetailListResponse(BaseModel):
    total: int
    data: List[BatchDetailListItem]