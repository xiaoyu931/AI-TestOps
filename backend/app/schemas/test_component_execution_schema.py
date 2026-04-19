from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComponentExecutionOut(BaseModel):
    TEST_COMPONENT_EXE_ID: int
    TEST_CASE_EXE_ID: Optional[int]
    TEST_COMPONENT_ID: Optional[int]
    TEST_COMPONENT_NAME: Optional[str]
    STATE: Optional[int]

    CREATE_DATE: Optional[datetime]
    FINISH_DATE: Optional[datetime]

    class Config:
        from_attributes = True


class ComponentExecutionListResponse(BaseModel):
    total: int
    data: list[ComponentExecutionOut]