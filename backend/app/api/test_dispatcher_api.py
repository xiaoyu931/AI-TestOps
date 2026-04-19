from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from datetime import datetime

from app.database import SessionLocal
from app.models.test_dispatcher_model import TestDispatcherData
from app.schemas.test_dispatcher_schema import (
    TestDispatcherCreateRequest,
    TestDispatcherUpdateRequest,
    TestDispatcherDetailResponse,
    TestDispatcherListResponse
)

router = APIRouter(prefix="/test-dispatcher", tags=["Test Dispatcher"])


@router.post("")
def create_test_dispatcher(req: TestDispatcherCreateRequest):
    db = SessionLocal()
    try:
        new_item = TestDispatcherData(
            QUE_NAME=req.que_name,
            EXE_MACHINE=req.exe_machine,
            PLAN_ID=req.plan_id if req.plan_id is not None else 0,
            BATCH_NAME=req.batch_name,

            SEND_EMAIL=req.send_email if req.send_email is not None else 0,
            PASS_RATE_SWITCH=req.pass_rate_switch if req.pass_rate_switch is not None else 0,
            PASS_RATE=req.pass_rate,

            DEFAULT_MSG_TO_LIST=req.default_msg_to_list,
            MSG_CC_LIST=req.msg_cc_list,
            MSG_TO_LIST=req.msg_to_list,

            CASE_LIST=req.case_list,
            ACTUAL_CASE_LIST=req.actual_case_list,

            EXPLANATION=req.explanation,

            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59),

            UPDATE_JIRA=req.update_jira,
            CREATE_BUG=req.create_bug,

            UIPATH_EXE_MACHONE=req.uipath_exe_machone
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return {
            "message": "created",
            "dispatcher_plan_id": new_item.DISPATCHER_PLAN_ID
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.get("", response_model=TestDispatcherListResponse)
def get_test_dispatcher_list(
    dispatcher_plan_id: int = None,
    que_name: str = None,
    exe_machine: str = None,
    plan_id: int = None,
    batch_name: str = None,
    explanation: str = None,
    update_jira: str = None,
    create_bug: str = None,
    uipath_exe_machone: str = None,

    page: int = 1,
    page_size: int = 10,

    sort_field: str = "dispatcher_plan_id",
    sort_order: str = "desc"
):
    db = SessionLocal()
    try:
        query = db.query(TestDispatcherData)

        # ===== 查询条件 =====
        if dispatcher_plan_id:
            query = query.filter(
                TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
            )

        if que_name:
            query = query.filter(
                TestDispatcherData.QUE_NAME.like(f"%{que_name}%")
            )

        if exe_machine:
            query = query.filter(
                TestDispatcherData.EXE_MACHINE.like(f"%{exe_machine}%")
            )

        if plan_id is not None:
            query = query.filter(
                TestDispatcherData.PLAN_ID == plan_id
            )

        if batch_name:
            query = query.filter(
                TestDispatcherData.BATCH_NAME.like(f"%{batch_name}%")
            )

        if explanation:
            query = query.filter(
                TestDispatcherData.EXPLANATION.like(f"%{explanation}%")
            )

        if update_jira:
            query = query.filter(
                TestDispatcherData.UPDATE_JIRA.like(f"%{update_jira}%")
            )

        if create_bug:
            query = query.filter(
                TestDispatcherData.CREATE_BUG.like(f"%{create_bug}%")
            )

        if uipath_exe_machone:
            query = query.filter(
                TestDispatcherData.UIPATH_EXE_MACHONE.like(f"%{uipath_exe_machone}%")
            )

        # ===== 排序 =====
        sort_column = {
            "dispatcher_plan_id": TestDispatcherData.DISPATCHER_PLAN_ID,
            "que_name": TestDispatcherData.QUE_NAME,
            "exe_machine": TestDispatcherData.EXE_MACHINE,
            "plan_id": TestDispatcherData.PLAN_ID,
            "batch_name": TestDispatcherData.BATCH_NAME,
            "explanation": TestDispatcherData.EXPLANATION,
            "create_date": TestDispatcherData.CREATE_DATE,
            "update_jira": TestDispatcherData.UPDATE_JIRA,
            "create_bug": TestDispatcherData.CREATE_BUG,
            "uipath_exe_machone": TestDispatcherData.UIPATH_EXE_MACHONE,
        }.get(sort_field.lower(), TestDispatcherData.DISPATCHER_PLAN_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestDispatcherData.DISPATCHER_PLAN_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestDispatcherData.DISPATCHER_PLAN_ID))

        total = query.count()

        rows = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "data": [
                {
                    "dispatcher_plan_id": x.DISPATCHER_PLAN_ID,
                    "que_name": x.QUE_NAME,
                    "exe_machine": x.EXE_MACHINE,
                    "plan_id": x.PLAN_ID if x.PLAN_ID is not None else 0,
                    "batch_name": x.BATCH_NAME,

                    "send_email": x.SEND_EMAIL if x.SEND_EMAIL is not None else 0,
                    "pass_rate_switch": x.PASS_RATE_SWITCH if x.PASS_RATE_SWITCH is not None else 0,
                    "pass_rate": x.PASS_RATE,

                    "default_msg_to_list": x.DEFAULT_MSG_TO_LIST,
                    "msg_cc_list": x.MSG_CC_LIST,
                    "msg_to_list": x.MSG_TO_LIST,

                    "case_list": x.CASE_LIST,
                    "actual_case_list": x.ACTUAL_CASE_LIST,

                    "explanation": x.EXPLANATION,

                    "update_jira": x.UPDATE_JIRA,
                    "create_bug": x.CREATE_BUG,

                    "uipath_exe_machone": x.UIPATH_EXE_MACHONE,

                    "create_date": x.CREATE_DATE,
                    "expire_date": x.EXPIRE_DATE
                }
                for x in rows
            ]
        }

    finally:
        db.close()


@router.get("/{dispatcher_plan_id}", response_model=TestDispatcherDetailResponse)
def get_test_dispatcher_detail(dispatcher_plan_id: int):
    db = SessionLocal()
    try:
        item = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Test dispatcher not found")

        return {
            "dispatcher_plan_id": item.DISPATCHER_PLAN_ID,
            "que_name": item.QUE_NAME,
            "exe_machine": item.EXE_MACHINE,
            "plan_id": item.PLAN_ID if item.PLAN_ID is not None else 0,
            "batch_name": item.BATCH_NAME,

            "send_email": item.SEND_EMAIL if item.SEND_EMAIL is not None else 0,
            "pass_rate_switch": item.PASS_RATE_SWITCH if item.PASS_RATE_SWITCH is not None else 0,
            "pass_rate": item.PASS_RATE,

            "default_msg_to_list": item.DEFAULT_MSG_TO_LIST,
            "msg_cc_list": item.MSG_CC_LIST,
            "msg_to_list": item.MSG_TO_LIST,

            "case_list": item.CASE_LIST,
            "actual_case_list": item.ACTUAL_CASE_LIST,

            "explanation": item.EXPLANATION,

            "update_jira": item.UPDATE_JIRA,
            "create_bug": item.CREATE_BUG,

            "uipath_exe_machone": item.UIPATH_EXE_MACHONE,

            "create_date": item.CREATE_DATE,
            "expire_date": item.EXPIRE_DATE
        }

    finally:
        db.close()


@router.put("/{dispatcher_plan_id}")
def update_test_dispatcher(dispatcher_plan_id: int, req: TestDispatcherUpdateRequest):
    db = SessionLocal()
    try:
        item = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Test dispatcher not found")

        item.QUE_NAME = req.que_name
        item.EXE_MACHINE = req.exe_machine
        item.PLAN_ID = req.plan_id if req.plan_id is not None else 0
        item.BATCH_NAME = req.batch_name

        item.SEND_EMAIL = req.send_email if req.send_email is not None else 0
        item.PASS_RATE_SWITCH = req.pass_rate_switch if req.pass_rate_switch is not None else 0
        item.PASS_RATE = req.pass_rate

        item.DEFAULT_MSG_TO_LIST = req.default_msg_to_list
        item.MSG_CC_LIST = req.msg_cc_list
        item.MSG_TO_LIST = req.msg_to_list

        item.CASE_LIST = req.case_list
        item.ACTUAL_CASE_LIST = req.actual_case_list

        item.EXPLANATION = req.explanation

        item.UPDATE_JIRA = req.update_jira
        item.CREATE_BUG = req.create_bug

        item.UIPATH_EXE_MACHONE = req.uipath_exe_machone

        db.commit()

        return {
            "message": "updated",
            "dispatcher_plan_id": dispatcher_plan_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.delete("/{dispatcher_plan_id}")
def delete_test_dispatcher(dispatcher_plan_id: int):
    db = SessionLocal()
    try:
        item = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Test dispatcher not found")

        db.delete(item)
        db.commit()

        return {
            "message": "deleted",
            "dispatcher_plan_id": dispatcher_plan_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()