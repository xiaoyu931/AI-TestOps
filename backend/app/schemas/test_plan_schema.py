from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TestPlanListItem(BaseModel):
    batch_id: int
    batch_name: Optional[str] = None
    task_status: Optional[int] = 0
    status: Optional[int] = 0
    send_email: Optional[int] = 0
    plan_id: Optional[int] = 0
    omp_batch_id: Optional[int] = 0
    pass_rate_switch: Optional[int] = 0
    pass_rate: Optional[str] = None
    re_run: Optional[int] = 0
    default_msg_to_list: Optional[str] = None
    msg_cc_list: Optional[str] = None
    msg_to_list: Optional[str] = None
    execution_machine: Optional[str] = None
    create_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    update_jira: Optional[str] = None
    billing_issue: Optional[int] = 0
    create_bug: Optional[str] = None


class TestPlanListResponse(BaseModel):
    total: int
    data: List[TestPlanListItem]