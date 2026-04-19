from fastapi import APIRouter, HTTPException, Query
from app.database import SessionLocal
from app.models.cfg_test_case_task_model import TestCaseTask
from app.models.cfg_test_case_data_model import TestCaseData
from app.schemas.case_task_schema import CaseCreateRequest, CaseUpdateRequest
from datetime import datetime
import json

router = APIRouter(tags=["Case"])


def _has_value(v):
    return v is not None and v != 0 and v != ""


def _build_order_data(req):
    if req.order_test_data is not None:
        return req.order_test_data
    return req.test_data or {}


def _build_verify_data(req):
    if req.verify_test_data is not None:
        return req.verify_test_data
    return req.test_data or {}


def _insert_case_data_rows(db, cfg_id: int, req):
    """
    规则：
    1. UiPath 入参永远插入一条
    2. 如果 template_id 有值，则插入 order 一条
    3. 如果 verify_template_id 有值，则插入 verify 一条
    """

    now = datetime.now()

    # 1) UiPath
    db.add(TestCaseData(
        CFG_ID=cfg_id,
        TEST_CASE_TEMPLATE_ID=None,
        TEST_DATA=json.dumps(req.test_data or {}, ensure_ascii=False),
        TENANT_ID=req.tenant_id,
        STATE=1,
        UIPATH_FLAG=1,
        CREATE_DATE=now,
        EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
    ))

    # 2) Order
    if _has_value(req.template_id):
        db.add(TestCaseData(
            CFG_ID=cfg_id,
            TEST_CASE_TEMPLATE_ID=req.template_id,
            TEST_DATA=json.dumps(_build_order_data(req), ensure_ascii=False),
            TENANT_ID=req.tenant_id,
            STATE=1,
            UIPATH_FLAG=0,
            CREATE_DATE=now,
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        ))

    # 3) Verify
    if _has_value(req.verify_template_id):
        db.add(TestCaseData(
            CFG_ID=cfg_id,
            TEST_CASE_TEMPLATE_ID=req.verify_template_id,
            TEST_DATA=json.dumps(_build_verify_data(req), ensure_ascii=False),
            TENANT_ID=req.tenant_id,
            STATE=1,
            UIPATH_FLAG=0,
            CREATE_DATE=now,
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        ))


@router.post("/case-tasks")
def create_case(case: CaseCreateRequest):
    db = SessionLocal()

    try:
        new_case = TestCaseTask(
            TEST_CASE_TEMPLATE_ID=case.template_id if _has_value(case.template_id) else None,
            TEST_CASE_NAME=case.test_case_name if _has_value(case.template_id) else "",
            VERIFY_TEST_CASE_TEMPLATE_ID=case.verify_template_id if _has_value(case.verify_template_id) else None,
            VERIFY_TEST_CASE_NAME=case.verify_template_name if _has_value(case.verify_template_id) else "",
            TRIGGER_MODE=case.trigger_mode,
            CRON_EXPRESSION=case.cron_expression,
            TASK_STATUS=case.task_status,
            EXECUTION_ENVIRONMENT=case.environment,
            EXECUTION_MACHINE=case.machine,
            TENANT_ID=case.tenant_id,
            STATE=case.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59),
            TEST_INST_ID=case.inst_id,
            UIPATH_ENTRY=case.uipath_entry,
            UIPATH_CASE_NAME=case.uipath_case_name,
            CASE_ID=case.case_id
        )

        db.add(new_case)
        db.flush()

        cfg_id = new_case.CFG_ID

        _insert_case_data_rows(db, cfg_id, case)

        db.commit()

        return {
            "message": "success",
            "cfg_id": cfg_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


from sqlalchemy import desc, asc

@router.get("/case-tasks")
def get_case_list(
    cfg_id: int = None,
    uipath_case_name: str = Query(None),
    environment: str = None,
    machine: str = None,
    template_id: int = None,
    verify_template_id: int = None,

    page: int = 1,
    page_size: int = 10,

    sort_field: str = "CFG_ID",
    sort_order: str = "desc"
):
    db = SessionLocal()

    try:
        query = db.query(TestCaseTask)

        # ===== 查询条件 =====
        if cfg_id:
            query = query.filter(TestCaseTask.CFG_ID == cfg_id)

        if uipath_case_name:
            query = query.filter(
                TestCaseTask.UIPATH_CASE_NAME.like(f"%{uipath_case_name}%")
            )

        if environment:
            query = query.filter(
                TestCaseTask.EXECUTION_ENVIRONMENT == environment
            )

        if machine:
            query = query.filter(
                TestCaseTask.EXECUTION_MACHINE.like(f"%{machine}%")
            )

        if template_id:
            query = query.filter(
                TestCaseTask.TEST_CASE_TEMPLATE_ID == template_id
            )

        if verify_template_id:
            query = query.filter(
                TestCaseTask.VERIFY_TEST_CASE_TEMPLATE_ID == verify_template_id
            )

        # ===== 排序 =====
        sort_column = {
            "cfg_id": TestCaseTask.CFG_ID,
            "case_name": TestCaseTask.UIPATH_CASE_NAME
        }.get(sort_field.lower(), TestCaseTask.CFG_ID)

        if sort_order == "asc":
            query = query.order_by(
                asc(sort_column),
                asc(TestCaseTask.CFG_ID)  # 保证稳定
            )
        else:
            query = query.order_by(
                desc(sort_column),
                desc(TestCaseTask.CFG_ID)  # 保证稳定
            )

        # ===== 总数 =====
        total = query.count()

        # ===== 分页 =====
        tasks = query.offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()

        # ===== 返回数据 =====
        result = []
        for t in tasks:
            result.append({
                "cfg_id": t.CFG_ID,
                "uipath_case_name": t.UIPATH_CASE_NAME,
                "test_case_name": t.TEST_CASE_NAME,
                "verify_template_name": t.VERIFY_TEST_CASE_NAME,
                "environment": t.EXECUTION_ENVIRONMENT,
                "machine": t.EXECUTION_MACHINE,
                "uipath_entry": t.UIPATH_ENTRY,
                "task_status": t.TASK_STATUS,
                "create_date": t.CREATE_DATE
            })

        return {
            "total": total,
            "data": result
        }

    finally:
        db.close()

@router.get("/case-tasks/{cfg_id}")
def get_case_detail(cfg_id: int):
    db = SessionLocal()

    try:
        task = db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID == cfg_id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Not found")

        datas = db.query(TestCaseData).filter(
            TestCaseData.CFG_ID == cfg_id
        ).all()

        uipath_data = {}
        order_data = {}
        verify_data = {}

        for d in datas:
            raw = json.loads(d.TEST_DATA) if d.TEST_DATA else {}

            if d.UIPATH_FLAG == 1:
                uipath_data = raw
            elif task.TEST_CASE_TEMPLATE_ID and d.TEST_CASE_TEMPLATE_ID == task.TEST_CASE_TEMPLATE_ID:
                order_data = raw
            elif task.VERIFY_TEST_CASE_TEMPLATE_ID and d.TEST_CASE_TEMPLATE_ID == task.VERIFY_TEST_CASE_TEMPLATE_ID:
                verify_data = raw

        return {
            "cfg_id": task.CFG_ID,
            "template_id": task.TEST_CASE_TEMPLATE_ID,
            "test_case_name": task.TEST_CASE_NAME,
            "verify_template_id": task.VERIFY_TEST_CASE_TEMPLATE_ID,
            "verify_template_name": task.VERIFY_TEST_CASE_NAME,
            "trigger_mode": task.TRIGGER_MODE,
            "cron_expression": task.CRON_EXPRESSION,
            "task_status": task.TASK_STATUS,
            "environment": task.EXECUTION_ENVIRONMENT,
            "machine": task.EXECUTION_MACHINE,
            "tenant_id": task.TENANT_ID,
            "state": task.STATE,
            "inst_id": task.TEST_INST_ID,
            "uipath_entry": task.UIPATH_ENTRY,
            "uipath_case_name": task.UIPATH_CASE_NAME,
            "case_id": task.CASE_ID,

            # 前端编辑页主要使用这一份
            "test_data": uipath_data,

            # 返回出来便于调试
            "uipath_data": uipath_data,
            "order_data": order_data,
            "verify_data": verify_data
        }

    finally:
        db.close()


@router.put("/case-tasks/{cfg_id}")
def update_case(cfg_id: int, case: CaseUpdateRequest):
    db = SessionLocal()

    try:
        task = db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID == cfg_id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Case not found")


        task.TEST_CASE_TEMPLATE_ID = case.template_id if _has_value(case.template_id) else None,
        task.TEST_CASE_NAME = case.test_case_name if _has_value(case.template_id) else "",
        task.VERIFY_TEST_CASE_TEMPLATE_ID = case.verify_template_id if _has_value(case.verify_template_id) else None,
        task.VERIFY_TEST_CASE_NAME = case.verify_template_name if _has_value(case.verify_template_id) else "",

        task.TRIGGER_MODE = case.trigger_mode
        task.CRON_EXPRESSION = case.cron_expression
        task.TASK_STATUS = case.task_status
        task.EXECUTION_ENVIRONMENT = case.environment
        task.EXECUTION_MACHINE = case.machine
        task.TENANT_ID = case.tenant_id
        task.STATE = case.state
        task.TEST_INST_ID = case.inst_id
        task.UIPATH_ENTRY = case.uipath_entry
        task.UIPATH_CASE_NAME = case.uipath_case_name
        task.CASE_ID = case.case_id

        # 先删旧数据，再按最新配置重建
        db.query(TestCaseData).filter(
            TestCaseData.CFG_ID == cfg_id
        ).delete()

        _insert_case_data_rows(db, cfg_id, case)

        db.commit()

        return {"message": "updated", "cfg_id": cfg_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.delete("/case-tasks/{cfg_id}")
def delete_case(cfg_id: int):
    db = SessionLocal()

    try:
        task = db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID == cfg_id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Case not found")

        db.query(TestCaseData).filter(
            TestCaseData.CFG_ID == cfg_id
        ).delete()

        db.delete(task)
        db.commit()

        return {"message": "deleted", "cfg_id": cfg_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()