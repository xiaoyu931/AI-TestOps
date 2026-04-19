from fastapi import APIRouter
from sqlalchemy import asc, desc
from datetime import datetime

from app.database import SessionLocal
from app.models.test_plan_model import TestPlan
from app.schemas.test_plan_schema import TestPlanListResponse

router = APIRouter(prefix="/test-plans", tags=["Test Plans"])


@router.get("", response_model=TestPlanListResponse)
def get_test_plan_list(
    batch_id: int = None,
    batch_name: str = None,
    plan_id: int = None,
    execution_machine: str = None,
    task_status: int = None,
    status: int = None,
    create_date_from: str = None,
    create_date_to: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "batch_id",
    sort_order: str = "desc"
):
    db = SessionLocal()
    try:
        query = db.query(TestPlan)

        # ===== 查询条件 =====
        if batch_id:
            query = query.filter(TestPlan.BATCH_ID == batch_id)

        if batch_name:
            query = query.filter(TestPlan.BATCH_NAME.like(f"%{batch_name}%"))

        if plan_id is not None:
            query = query.filter(TestPlan.PLAN_ID == plan_id)

        if execution_machine:
            query = query.filter(TestPlan.EXECUTION_MACHINE.like(f"%{execution_machine}%"))

        if task_status is not None:
            query = query.filter(TestPlan.TASK_STATUS == task_status)

        if status is not None:
            query = query.filter(TestPlan.STATUS == status)

        if create_date_from:
            try:
                dt_from = datetime.fromisoformat(create_date_from)
                query = query.filter(TestPlan.CREATE_DATE >= dt_from)
            except ValueError:
                pass

        if create_date_to:
            try:
                dt_to = datetime.fromisoformat(create_date_to)
                query = query.filter(TestPlan.CREATE_DATE <= dt_to)
            except ValueError:
                pass

        # ===== 排序 =====
        sort_column = {
            "batch_id": TestPlan.BATCH_ID,
            "batch_name": TestPlan.BATCH_NAME,
            "plan_id": TestPlan.PLAN_ID,
            "execution_machine": TestPlan.EXECUTION_MACHINE,
            "task_status": TestPlan.TASK_STATUS,
            "status": TestPlan.STATUS,
            "pass_rate": TestPlan.PASS_RATE,
            "re_run": TestPlan.RE_RUN,
            "create_date": TestPlan.CREATE_DATE,
            "finish_date": TestPlan.FINISH_DATE,
        }.get(sort_field.lower(), TestPlan.BATCH_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestPlan.BATCH_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestPlan.BATCH_ID))

        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "data": [
                {
                    "batch_id": x.BATCH_ID,
                    "batch_name": x.BATCH_NAME,
                    "task_status": x.TASK_STATUS if x.TASK_STATUS is not None else 0,
                    "status": x.STATUS if x.STATUS is not None else 0,
                    "send_email": x.SEND_EMAIL if x.SEND_EMAIL is not None else 0,
                    "plan_id": x.PLAN_ID if x.PLAN_ID is not None else 0,
                    "omp_batch_id": x.OMP_BATCH_ID if x.OMP_BATCH_ID is not None else 0,
                    "pass_rate_switch": x.PASS_RATE_SWITCH if x.PASS_RATE_SWITCH is not None else 0,
                    "pass_rate": x.PASS_RATE,
                    "re_run": x.RE_RUN if x.RE_RUN is not None else 0,
                    "default_msg_to_list": x.DEFAULT_MSG_TO_LIST,
                    "msg_cc_list": x.MSG_CC_LIST,
                    "msg_to_list": x.MSG_TO_LIST,
                    "execution_machine": x.EXECUTION_MACHINE,
                    "create_date": x.CREATE_DATE,
                    "finish_date": x.FINISH_DATE,
                    "update_jira": x.update_jira,
                    "billing_issue": x.billing_issue if x.billing_issue is not None else 0,
                    "create_bug": x.CREATE_BUG,
                }
                for x in rows
            ]
        }

    finally:
        db.close()