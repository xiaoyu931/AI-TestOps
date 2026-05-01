from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.test_dispatcher_model import TestDispatcherData
from app.models.cfg_test_case_task_model import TestCaseTask
from app.models.cfg_test_case_data_model import TestCaseData

import json
import re
from typing import Optional
from datetime import datetime
from app.models.test_plan_model import TestPlan
from app.models.batch_detail_model import BatchDetail

router = APIRouter(prefix="/dispatcher-ext", tags=["Test Dispatcher"])


def _has_value(value) -> bool:
    return value is not None and value != "" and value != 0


def _parse_case_list(raw: Optional[str]) -> list[int]:
    if not raw:
        return []

    text = raw.strip()
    if not text:
        return []

    try:
        loaded = json.loads(text)

        if isinstance(loaded, list):
            result = []
            for item in loaded:
                if str(item).strip():
                    result.append(int(item))
            return result

        if isinstance(loaded, (int, str)):
            return [int(loaded)]

    except Exception:
        pass

    values = re.split(r"[\s,;]+", text.strip("[](){} "))
    result = []

    for value in values:
        if not value:
            continue

        try:
            result.append(int(value))
        except ValueError:
            continue

    return result


def _safe_json_loads(text: Optional[str]):
    if not text:
        return {}

    try:
        return json.loads(text)
    except Exception:
        return text


def _is_playwright_case(case: TestCaseTask) -> bool:
    entry = case.UIPATH_ENTRY or ""
    case_name = case.UIPATH_CASE_NAME or ""
    case_id = case.CASE_ID or ""
    machine = case.EXECUTION_MACHINE or ""

    text = " ".join([
        entry.lower(),
        case_name.lower(),
        case_id.lower(),
        machine.lower(),
    ])

    return (
        "::test_" in entry
        or "playwright" in text
        or "pytest" in text
        or case_id.upper().startswith("PW_")
        or bool(entry and entry.startswith("tests/"))
    )


def _success_status_after_playwright(case: TestCaseTask) -> int:
    need_order_process = _has_value(case.TEST_CASE_TEMPLATE_ID)
    need_data_verify = _has_value(case.VERIFY_TEST_CASE_TEMPLATE_ID)

    if need_order_process:
        return 8

    if need_data_verify:
        return 10

    return 13


@router.put("/{plan_id}")
def update_dispatcher(plan_id: int, data: dict):

    db = SessionLocal()

    try:
        item = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == plan_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        for k, v in data.items():
            if hasattr(item, k):
                setattr(item, k, v)

        db.commit()

        return {"message": "updated"}

    finally:
        db.close()


@router.get("/{dispatcher_plan_id}/execution-config")
def get_execution_config(dispatcher_plan_id: int):
    db = SessionLocal()

    try:
        dispatcher = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
        ).first()

        if not dispatcher:
            raise HTTPException(status_code=404, detail="Dispatcher plan not found")

        case_ids = _parse_case_list(dispatcher.CASE_LIST)

        cases = []
        missing_cfg_ids = []

        for cfg_id in case_ids:
            case = db.query(TestCaseTask).filter(
                TestCaseTask.CFG_ID == cfg_id
            ).first()

            if not case:
                missing_cfg_ids.append(cfg_id)
                continue

            case_data_rows = db.query(TestCaseData).filter(
                TestCaseData.CFG_ID == cfg_id,
                TestCaseData.STATE == 1
            ).all()

            playwright_input = {}
            order_input = {}
            verify_input = {}

            for row in case_data_rows:
                data = _safe_json_loads(row.TEST_DATA)

                if row.UIPATH_FLAG == 1:
                    playwright_input = data
                elif (
                    _has_value(case.TEST_CASE_TEMPLATE_ID)
                    and row.TEST_CASE_TEMPLATE_ID == case.TEST_CASE_TEMPLATE_ID
                ):
                    order_input = data
                elif (
                    _has_value(case.VERIFY_TEST_CASE_TEMPLATE_ID)
                    and row.TEST_CASE_TEMPLATE_ID == case.VERIFY_TEST_CASE_TEMPLATE_ID
                ):
                    verify_input = data

            need_order_process = _has_value(case.TEST_CASE_TEMPLATE_ID)
            need_data_verify = _has_value(case.VERIFY_TEST_CASE_TEMPLATE_ID)

            cases.append({
                "cfg_id": case.CFG_ID,
                "is_playwright": _is_playwright_case(case),

                "pytest_nodeid": case.UIPATH_ENTRY,
                "playwright_case_name": case.UIPATH_CASE_NAME,
                "case_id": case.CASE_ID,

                "execution_environment": case.EXECUTION_ENVIRONMENT,
                "execution_machine": case.EXECUTION_MACHINE,
                "tenant_id": case.TENANT_ID,
                "state": case.STATE,
                "task_status": case.TASK_STATUS,

                "need_order_process": need_order_process,
                "need_data_verify": need_data_verify,
                "success_status_after_playwright": _success_status_after_playwright(case),

                "order_template_id": case.TEST_CASE_TEMPLATE_ID,
                "order_case_name": case.TEST_CASE_NAME,
                "verify_template_id": case.VERIFY_TEST_CASE_TEMPLATE_ID,
                "verify_case_name": case.VERIFY_TEST_CASE_NAME,

                "playwright_input": playwright_input,
                "order_input": order_input,
                "verify_input": verify_input,
            })

        return {
            "dispatcher_plan_id": dispatcher.DISPATCHER_PLAN_ID,
            "batch_name": dispatcher.BATCH_NAME,
            "plan_id": dispatcher.PLAN_ID,
            "case_list": case_ids,
            "case_count": len(cases),
            "missing_cfg_ids": missing_cfg_ids,
            "is_playwright_plan": any(item["is_playwright"] for item in cases),
            "cases": cases,
        }

    finally:
        db.close()


@router.post("/{dispatcher_plan_id}/create-run")
def create_run(dispatcher_plan_id: int):
    db = SessionLocal()

    try:
        dispatcher = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == dispatcher_plan_id
        ).first()

        if not dispatcher:
            raise HTTPException(status_code=404, detail="Dispatcher plan not found")

        case_ids = _parse_case_list(dispatcher.CASE_LIST)

        if not case_ids:
            raise HTTPException(status_code=400, detail="CASE_LIST is empty")

        now = datetime.now()

        test_plan = TestPlan(
            BATCH_NAME=dispatcher.BATCH_NAME,
            TASK_STATUS=0,
            STATUS=1,
            SEND_EMAIL=dispatcher.SEND_EMAIL if dispatcher.SEND_EMAIL is not None else 0,
            PLAN_ID=dispatcher.PLAN_ID if dispatcher.PLAN_ID is not None else 0,
            OMP_BATCH_ID=0,
            PASS_RATE_SWITCH=dispatcher.PASS_RATE_SWITCH if dispatcher.PASS_RATE_SWITCH is not None else 0,
            PASS_RATE=dispatcher.PASS_RATE,
            RE_RUN=0,
            DEFAULT_MSG_TO_LIST=dispatcher.DEFAULT_MSG_TO_LIST,
            MSG_CC_LIST=dispatcher.MSG_CC_LIST,
            MSG_TO_LIST=dispatcher.MSG_TO_LIST,
            EXECUTION_MACHINE=dispatcher.EXE_MACHINE,
            CREATE_DATE=now,
            FINISH_DATE=None,
            update_jira=dispatcher.UPDATE_JIRA,
            billing_issue=0,
            CREATE_BUG=dispatcher.CREATE_BUG
        )

        db.add(test_plan)
        db.flush()

        batch_id = test_plan.BATCH_ID

        batch_details = []

        for cfg_id in case_ids:
            batch_detail = BatchDetail(
                BATCH_ID=batch_id,
                CFG_ID=cfg_id,
                UIPATH_CASE_EXE_ID=None,
                ORDER_CASE_EXE_ID=None,
                VERIFY_CASE_EXE_ID=None,
                STATUS=0,
                TASK_STATUS=0,
                CREATE_DATE=now,
                FINISH_DATE=None
            )

            db.add(batch_detail)
            batch_details.append(batch_detail)

        db.commit()

        return {
            "message": "created",
            "dispatcher_plan_id": dispatcher_plan_id,
            "batch_id": batch_id,
            "batch_name": dispatcher.BATCH_NAME,
            "case_count": len(case_ids),
            "case_list": case_ids
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

