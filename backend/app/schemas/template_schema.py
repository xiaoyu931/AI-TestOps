from pydantic import BaseModel
from typing import List, Optional


class ComponentItem(BaseModel):
    component_id: int
    sort: int
    wait_time: int = 5
    loop_num: int = 1
    is_suspend: str = "Y"
    remark: Optional[str] = ""


class TemplateCreateRequest(BaseModel):
    template_name: str
    module: str

    test_case_type: str = "1"
    is_browser: int = 0
    tenant_id: str = "21"
    state: int = 1
    remark: Optional[str] = ""

    components: List[ComponentItem]

    class Config:
        extra = "ignore"


class TemplateUpdateRequest(BaseModel):
    template_name: str
    module: str

    test_case_type: str = "1"
    is_browser: int = 0
    tenant_id: str = "21"
    state: int = 1
    remark: Optional[str] = ""

    components: List[ComponentItem]

    class Config:
        extra = "ignore"