from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TestDispatcherBase(BaseModel):
    que_name: Optional[str] = None
    exe_machine: Optional[str] = None
    plan_id: Optional[int] = 0
    batch_name: Optional[str] = None

    send_email: Optional[int] = 0
    pass_rate_switch: Optional[int] = 0
    pass_rate: Optional[str] = None

    default_msg_to_list: Optional[str] = None
    msg_cc_list: Optional[str] = None
    msg_to_list: Optional[str] = None

    case_list: Optional[str] = None
    actual_case_list: Optional[str] = None

    explanation: Optional[str] = None

    update_jira: Optional[str] = None
    create_bug: Optional[str] = None

    uipath_exe_machone: Optional[str] = None


class TestDispatcherCreateRequest(TestDispatcherBase):
    pass


class TestDispatcherUpdateRequest(TestDispatcherBase):
    pass


class TestDispatcherDetailResponse(TestDispatcherBase):
    dispatcher_plan_id: int
    create_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestDispatcherListItem(BaseModel):
    dispatcher_plan_id: int
    que_name: Optional[str] = None
    exe_machine: Optional[str] = None
    plan_id: Optional[int] = 0
    batch_name: Optional[str] = None

    send_email: Optional[int] = 0
    pass_rate_switch: Optional[int] = 0
    pass_rate: Optional[str] = None

    default_msg_to_list: Optional[str] = None
    msg_cc_list: Optional[str] = None
    msg_to_list: Optional[str] = None

    case_list: Optional[str] = None
    actual_case_list: Optional[str] = None

    explanation: Optional[str] = None

    update_jira: Optional[str] = None
    create_bug: Optional[str] = None

    uipath_exe_machone: Optional[str] = None

    create_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None


class TestDispatcherListResponse(BaseModel):
    total: int
    data: List[TestDispatcherListItem]