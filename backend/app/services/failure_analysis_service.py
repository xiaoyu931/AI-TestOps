import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.analyzer.analyzer_core import analyze_error
from app.models.batch_detail_model import BatchDetail
from app.models.cfg_test_case_task_model import TestCaseTask
from app.models.test_case_execution_model import TestCaseExecution
from app.models.test_component_execution_model import TestComponentExecution
from app.services.aggregation_service import (
    build_empty_failure_analysis_response,
    build_failure_analysis_response,
    build_summary,
)


FAIL_STATES = [3, 6, 11]
SUCCESS_STATES = [5, 13, 14]

MAX_BATCH_ROWS = 500
MAX_COMPONENT_ROWS = 2000


def get_state_text(value: int) -> str:
    mapping = {
        1: "Running",
        2: "Success",
        3: "UiPath Failed",
        4: "Verifying",
        5: "Verify Success",
        6: "Verify Failed",
        7: "Triggered Verify",
        8: "UiPath Success",
        9: "Order Processing",
        10: "Order Success",
        11: "Order Failed",
        12: "Triggered Order",
        13: "No Order Needed",
        14: "No Verify Needed",
    }
    return mapping.get(value, str(value))


def get_stage(state: int) -> str:
    if state == 3:
        return "UIPATH"
    if state == 11:
        return "ORDER"
    if state == 6:
        return "VERIFY"
    return "UNKNOWN"


def parse_json_text(text: Optional[str]):
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return None


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""

    return str(text).replace("\r", " ").replace("\n", " ").strip()


def extract_error_from_result_data(test_result_data: Optional[str]) -> str:
    if not test_result_data:
        return ""

    obj = parse_json_text(test_result_data)
    if obj is None:
        return clean_text(test_result_data)

    if isinstance(obj, dict):
        error_data = obj.get("errorData")
        if isinstance(error_data, list):
            return clean_text(" | ".join([str(x) for x in error_data if x]))

        if isinstance(error_data, str):
            return clean_text(error_data)

        if obj.get("message"):
            return clean_text(obj.get("message"))

    return clean_text(test_result_data)


def shorten_text(text: str, limit: int = 220) -> str:
    text = clean_text(text)

    if len(text) <= limit:
        return text

    return text[:limit] + "..."


def extract_error_pattern(error_text: str) -> str:
    text = error_text or ""

    match = re.search(r"Index \d+ out of bounds", text)
    if match:
        return "Index Out Of Bounds"

    match = re.search(r"id='([^']+)'", text)
    if match:
        return f"Selector ID: {match.group(1)}"

    match = re.search(r"aaname='([^']+)'", text)
    if match:
        return f"Selector Name: {match.group(1)}"

    match = re.search(r"SoaSapInterFace\(([^)]+)\)", text, flags=re.IGNORECASE)
    if match:
        return f"SAP API: {match.group(1)}"

    match = re.search(r"code[:=]\s*(\d+)", text, flags=re.IGNORECASE)
    if match:
        return f"Error Code: {match.group(1)}"

    return "Other"


def build_pattern_display(pattern: str):
    if pattern == "Index Out Of Bounds":
        return {
            "title": "Array index out of bounds",
            "suggestion": "Check list/array size before accessing elements; add boundary validation",
        }

    if pattern.startswith("SAP API"):
        api = pattern.split(":")[-1].strip()
        return {
            "title": f"SAP API failure ({api})",
            "suggestion": "Check SAP API status, confirm whether data exists, and verify whether the request timed out",
        }

    if "UserVertifyCode" in pattern:
        return {
            "title": "Login page verification-code element missing",
            "suggestion": "Check whether the login page changed, whether the selector is invalid, and whether additional wait time is needed",
        }

    if "HeadTable_agrTable" in pattern:
        return {
            "title": "Agreement page table element missing",
            "suggestion": "Check the Agreement page structure and verify the selector path",
        }

    if pattern.startswith("Selector ID"):
        selector_id = pattern.split(":")[-1].strip()
        return {
            "title": f"UI element missing ({selector_id})",
            "suggestion": "Check whether the selector is stable and whether the related page changed",
        }

    if pattern.startswith("Selector Name"):
        selector_name = pattern.split(":")[-1].strip()
        return {
            "title": f"UI element missing ({selector_name})",
            "suggestion": "Check whether the selector is stable and whether the related page changed",
        }

    if pattern.startswith("Error Code: 404"):
        return {
            "title": "Requested data not found",
            "suggestion": "Check whether upstream data exists and whether the query condition is correct",
        }

    if pattern.startswith("Error Code: 410"):
        return {
            "title": "Data indexing or boundary issue",
            "suggestion": "Check whether the returned list is empty and verify boundary handling in the script",
        }

    return {
        "title": "Unknown issue",
        "suggestion": "Review the detailed log and classify this issue into a reusable rule if it happens repeatedly",
    }


class FailureAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def get_failure_analysis(
        self,
        batch_id: int = None,
        cfg_id: int = None,
        uipath_case_name: str = None,
        create_date_from: str = None,
        create_date_to: str = None,
    ):
        batch_rows = self._query_batch_rows(
            batch_id=batch_id,
            cfg_id=cfg_id,
            create_date_from=create_date_from,
            create_date_to=create_date_to,
        )

        if not batch_rows:
            return build_empty_failure_analysis_response()

        cfg_map = self._load_cfg_map(batch_rows)
        batch_rows = self._filter_by_uipath_case_name(
            batch_rows=batch_rows,
            cfg_map=cfg_map,
            uipath_case_name=uipath_case_name,
        )

        if not batch_rows:
            return build_empty_failure_analysis_response()

        cfg_map = self._load_cfg_map(batch_rows)

        total = len(batch_rows)
        failed_batch_rows = [row for row in batch_rows if row[3] in FAIL_STATES]
        success_batch_rows = [row for row in batch_rows if row[3] in SUCCESS_STATES]

        summary = build_summary(
            total=total,
            failed=len(failed_batch_rows),
            success=len(success_batch_rows),
        )

        if not failed_batch_rows:
            return build_failure_analysis_response(summary=summary, failure_details=[])

        failed_case_exe_ids = self._collect_failed_case_exe_ids(failed_batch_rows)

        if not failed_case_exe_ids:
            return build_failure_analysis_response(summary=summary, failure_details=[])

        case_map = self._load_case_map(failed_case_exe_ids)
        component_preferred_map = self._load_preferred_component_map(failed_case_exe_ids)

        failure_details = self._build_failure_details(
            failed_batch_rows=failed_batch_rows,
            case_map=case_map,
            component_preferred_map=component_preferred_map,
            cfg_map=cfg_map,
        )

        return build_failure_analysis_response(
            summary=summary,
            failure_details=failure_details,
        )

    def _query_batch_rows(
        self,
        batch_id: int = None,
        cfg_id: int = None,
        create_date_from: str = None,
        create_date_to: str = None,
    ) -> List[Tuple]:
        batch_query = self.db.query(BatchDetail).with_entities(
            BatchDetail.BATCH_ID,
            BatchDetail.BATCH_DETAIL_ID,
            BatchDetail.CFG_ID,
            BatchDetail.STATUS,
            BatchDetail.UIPATH_CASE_EXE_ID,
            BatchDetail.ORDER_CASE_EXE_ID,
            BatchDetail.VERIFY_CASE_EXE_ID,
            BatchDetail.CREATE_DATE,
            BatchDetail.FINISH_DATE,
        )

        if batch_id:
            batch_query = batch_query.filter(BatchDetail.BATCH_ID == batch_id)

        if cfg_id:
            batch_query = batch_query.filter(BatchDetail.CFG_ID == cfg_id)

        if create_date_from:
            try:
                dt_from = datetime.fromisoformat(create_date_from)
                batch_query = batch_query.filter(BatchDetail.CREATE_DATE >= dt_from)
            except ValueError:
                pass

        if create_date_to:
            try:
                dt_to = datetime.fromisoformat(create_date_to)
                batch_query = batch_query.filter(BatchDetail.CREATE_DATE <= dt_to)
            except ValueError:
                pass

        return batch_query.order_by(
            BatchDetail.BATCH_DETAIL_ID.desc()
        ).limit(MAX_BATCH_ROWS).all()

    def _load_cfg_map(self, batch_rows: List[Tuple]) -> Dict[int, TestCaseTask]:
        cfg_ids = {row[2] for row in batch_rows if row[2] is not None}

        if not cfg_ids:
            return {}

        cfg_list = self.db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID.in_(list(cfg_ids))
        ).all()

        return {x.CFG_ID: x for x in cfg_list}

    def _filter_by_uipath_case_name(
        self,
        batch_rows: List[Tuple],
        cfg_map: Dict[int, TestCaseTask],
        uipath_case_name: str = None,
    ) -> List[Tuple]:
        if not uipath_case_name:
            return batch_rows

        keyword = uipath_case_name.strip().lower()

        return [
            row for row in batch_rows
            if row[2] in cfg_map
            and cfg_map[row[2]].UIPATH_CASE_NAME
            and keyword in cfg_map[row[2]].UIPATH_CASE_NAME.lower()
        ]

    def _collect_failed_case_exe_ids(self, failed_batch_rows: List[Tuple]) -> set:
        failed_case_exe_ids = set()

        for row in failed_batch_rows:
            status = row[3]

            if status == 3 and row[4] and row[4] > 0:
                failed_case_exe_ids.add(row[4])
            elif status == 11 and row[5] and row[5] > 0:
                failed_case_exe_ids.add(row[5])
            elif status == 6 and row[6] and row[6] > 0:
                failed_case_exe_ids.add(row[6])

        return failed_case_exe_ids

    def _load_case_map(self, failed_case_exe_ids: set) -> Dict[int, TestCaseExecution]:
        case_rows = self.db.query(TestCaseExecution).filter(
            TestCaseExecution.TEST_CASE_EXE_ID.in_(list(failed_case_exe_ids))
        ).all()

        return {x.TEST_CASE_EXE_ID: x for x in case_rows}

    def _load_preferred_component_map(
        self,
        failed_case_exe_ids: set,
    ) -> Dict[int, TestComponentExecution]:
        component_rows = self.db.query(TestComponentExecution).filter(
            TestComponentExecution.TEST_CASE_EXE_ID.in_(list(failed_case_exe_ids))
        ).order_by(
            TestComponentExecution.TEST_CASE_EXE_ID.asc(),
            TestComponentExecution.TEST_COMPONENT_EXE_ID.desc(),
        ).limit(MAX_COMPONENT_ROWS).all()

        component_preferred_map: Dict[int, TestComponentExecution] = {}
        component_latest_map: Dict[int, TestComponentExecution] = {}

        for row in component_rows:
            case_exe_id = row.TEST_CASE_EXE_ID

            if case_exe_id not in component_latest_map:
                component_latest_map[case_exe_id] = row

            if row.STATE == 3 and case_exe_id not in component_preferred_map:
                component_preferred_map[case_exe_id] = row

        for case_exe_id, latest_row in component_latest_map.items():
            if case_exe_id not in component_preferred_map:
                component_preferred_map[case_exe_id] = latest_row

        return component_preferred_map

    def _build_failure_details(
        self,
        failed_batch_rows: List[Tuple],
        case_map: Dict[int, TestCaseExecution],
        component_preferred_map: Dict[int, TestComponentExecution],
        cfg_map: Dict[int, TestCaseTask],
    ) -> List[dict]:
        failure_details = []

        for batch_row in failed_batch_rows:
            detail = self._build_failure_detail(
                batch_row=batch_row,
                case_map=case_map,
                component_preferred_map=component_preferred_map,
                cfg_map=cfg_map,
            )

            if detail:
                failure_details.append(detail)

        return failure_details

    def _build_failure_detail(
        self,
        batch_row: Tuple,
        case_map: Dict[int, TestCaseExecution],
        component_preferred_map: Dict[int, TestComponentExecution],
        cfg_map: Dict[int, TestCaseTask],
    ):
        batch_id_value = batch_row[0]
        cfg_value = batch_row[2]
        status_value = batch_row[3]
        uipath_case_exe_id = batch_row[4]
        order_case_exe_id = batch_row[5]
        verify_case_exe_id = batch_row[6]
        create_date_value = batch_row[7]
        finish_date_value = batch_row[8]

        current_case_exe_id = None
        if status_value == 3:
            current_case_exe_id = uipath_case_exe_id
        elif status_value == 11:
            current_case_exe_id = order_case_exe_id
        elif status_value == 6:
            current_case_exe_id = verify_case_exe_id

        if not current_case_exe_id or current_case_exe_id <= 0:
            return None

        case_row = case_map.get(current_case_exe_id)
        component_row = component_preferred_map.get(current_case_exe_id)

        stage = get_stage(status_value)
        base_error = ""
        component_name = None
        state = status_value
        state_text = get_state_text(status_value)

        if case_row:
            state = case_row.STATE if case_row.STATE is not None else status_value
            state_text = get_state_text(state)
            cfg_value = case_row.CFG_ID if case_row.CFG_ID is not None else cfg_value

            base_error = extract_error_from_result_data(case_row.TEST_RESULT_DATA)
            if not base_error:
                base_error = clean_text(case_row.ERROR_MESSAGE)

        if component_row:
            component_name = component_row.TEST_COMPONENT_NAME

            if not base_error:
                component_result = clean_text(component_row.COMPONENT_RESULT_DATA)
                python_error = clean_text(component_row.PYTHON_ERROR_MESSAGE)
                system_error = clean_text(component_row.SYSTEM_ERROR_MESSAGE)

                if component_result:
                    base_error = component_result
                elif python_error:
                    base_error = python_error
                elif system_error:
                    base_error = system_error

        analysis = analyze_error(self.db, base_error)

        error_type = analysis["error_type"]
        error_reason = analysis["root_cause"]
        suggestion = analysis["solution"]

        if analysis.get("matched"):
            pattern = analysis["root_cause"]
            pattern_title = analysis["root_cause"]
            pattern_suggestion = analysis["solution"]
        else:
            pattern = extract_error_pattern(base_error)
            display = build_pattern_display(pattern)
            pattern_title = display["title"]
            pattern_suggestion = display["suggestion"]

        cfg_info = cfg_map.get(cfg_value)

        return {
            "test_case_exe_id": current_case_exe_id,
            "batch_id": batch_id_value,
            "cfg_id": cfg_value,
            "uipath_case_name": cfg_info.UIPATH_CASE_NAME if cfg_info else None,
            "stage": stage,
            "state": state,
            "state_text": state_text,
            "error_type": error_type,
            "error_reason": error_reason,
            "suggestion": suggestion,
            "error_pattern": pattern,
            "error_pattern_title": pattern_title,
            "error_pattern_suggestion": pattern_suggestion,
            "error_summary": shorten_text(base_error, 220) if base_error else "-",
            "component_name": component_name if component_name else "Not Triggered",
            "create_date": create_date_value.isoformat(sep=" ") if create_date_value else None,
            "finish_date": finish_date_value.isoformat(sep=" ") if finish_date_value else None,
        }
