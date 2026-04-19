# app/api/test_case_execution_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.test_case_execution_model import TestCaseExecution
from app.schemas.test_case_execution_schema import (
    ExecutionBase,
    ExecutionListResponse,
    ExecutionQueryRequest
)

router = APIRouter(prefix="/case-executions", tags=["Case Execution"])


@router.get("")
def get_list(
    test_case_exe_id: int | None = None,
    cfg_id: int | None = None,
    test_case_name: str | None = None,
    execution_machine: str | None = None,
    state: int | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(TestCaseExecution)

    if test_case_exe_id:
        query = query.filter(TestCaseExecution.TEST_CASE_EXE_ID == test_case_exe_id)

    if cfg_id:
        query = query.filter(TestCaseExecution.CFG_ID == cfg_id)

    if test_case_name:
        query = query.filter(TestCaseExecution.TEST_CASE_NAME.like(f"%{test_case_name}%"))

    if execution_machine:
        query = query.filter(TestCaseExecution.EXECUTION_MACHINE.like(f"%{execution_machine}%"))

    if state is not None:
        query = query.filter(TestCaseExecution.STATE == state)

    query = query.order_by(TestCaseExecution.TEST_CASE_EXE_ID.desc())

    total = query.count()

    data = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "data": data   # ⭐ 关键
    }