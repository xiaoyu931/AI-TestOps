from pydantic import BaseModel
from typing import Optional, Dict, Any


class CaseCreateRequest(BaseModel):


    template_id: Optional[int] = 0
    test_case_name: Optional[str] = ""
    verify_template_id: Optional[int] = 0
    verify_template_name: Optional[str] = ""

    trigger_mode: Optional[int] = 2
    cron_expression: Optional[str] = ""

    task_status: Optional[int] = 1

    environment: Optional[str] = ""
    machine: Optional[str] = ""

    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    inst_id: Optional[str] = ""

    uipath_case_name: Optional[str] = ""
    uipath_entry: Optional[str] = ""

    case_id: Optional[str] = ""

    # 前端只维护一份 UiPath JSON
    test_data: Optional[Dict[str, Any]] = {}

    # 这两个字段保留兼容旧接口；如果前端不传，后端自动复制 test_data
    order_test_data: Optional[Dict[str, Any]] = None
    verify_test_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        extra = "ignore"


class CaseUpdateRequest(BaseModel):
    template_id: Optional[int] = 0
    test_case_name: Optional[str] = ""
    verify_template_id: Optional[int] = 0
    verify_template_name: Optional[str] = ""

    trigger_mode: Optional[int] = 2
    cron_expression: Optional[str] = ""

    task_status: Optional[int] = 1

    environment: Optional[str] = ""
    machine: Optional[str] = ""

    tenant_id: Optional[str] = ""
    state: Optional[int] = 1

    inst_id: Optional[str] = ""

    uipath_case_name: Optional[str] = ""
    uipath_entry: Optional[str] = ""

    case_id: Optional[str] = ""

    test_data: Optional[Dict[str, Any]] = {}

    order_test_data: Optional[Dict[str, Any]] = None
    verify_test_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        extra = "ignore"