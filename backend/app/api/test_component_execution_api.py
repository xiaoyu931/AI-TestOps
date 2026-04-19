from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.test_component_execution_model import TestComponentExecution
from app.schemas.test_component_execution_schema import ComponentExecutionListResponse

router = APIRouter(prefix="/component-executions", tags=["Component Execution"])


@router.get("/", response_model=ComponentExecutionListResponse)
def get_component_executions(
    test_case_exe_id: Optional[int] = None,
    test_component_id: Optional[int] = None,
    test_component_name: Optional[str] = None,
    state: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(TestComponentExecution)

    if test_case_exe_id:
        query = query.filter(TestComponentExecution.TEST_CASE_EXE_ID == test_case_exe_id)

    if test_component_id:
        query = query.filter(TestComponentExecution.TEST_COMPONENT_ID == test_component_id)

    if test_component_name:
        query = query.filter(TestComponentExecution.TEST_COMPONENT_NAME.like(f"%{test_component_name}%"))

    if state is not None:
        query = query.filter(TestComponentExecution.STATE == state)

    total = query.count()

    rows = (
        query.order_by(TestComponentExecution.CREATE_DATE.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "data": rows
    }