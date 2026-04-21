import json
import re
from collections import Counter
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from fastapi import APIRouter

from app.database import SessionLocal
from app.models.batch_detail_model import BatchDetail
from app.models.cfg_test_case_task_model import TestCaseTask
from app.models.test_component_execution_model import TestComponentExecution
from app.models.test_case_execution_model import TestCaseExecution
from app.schemas.failure_analysis_schema import FailureAnalysisResponse

router = APIRouter(prefix="/failure-analysis", tags=["Failure Analysis"])


FAIL_STATES = [3, 6, 11]
SUCCESS_STATES = [5, 13, 14]

MAX_BATCH_ROWS = 500
MAX_COMPONENT_ROWS = 2000


def build_empty_response():
    return {
        "summary": {
            "total": 0,
            "failed": 0,
            "success": 0,
            "success_rate": 0,
        },
        "stage_distribution": [],
        "error_type_distribution": [],
        "error_pattern_distribution": [],
        "top_issue": None,
        "failure_details": [],
    }


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


ERROR_RULES = [
    ("UI_SELECTOR", [
        "找不到对应此选取器的用户界面元素",
        "选取器",
        "selector",
        "uielement",
        "element not found"
    ]),
    ("TIMEOUT", ["timeout", "超时", "timed out"]),
    ("LOGIN", ["login", "登录", "not successfully"]),
    ("DATA_ERROR", [
        "校验",
        "validate",
        "validation",
        "mismatch",
        "不一致",
        "data can\"t found",
        "data can't found",
        "data not found"
    ]),
    ("NETWORK", ["connection", "network", "socket", "connect", "communication with server"]),
    ("CODE_ERROR", [
        "index out of bounds",
        "nullpointer",
        "undefined",
        "cannot read",
        "exception"
    ]),
    ("SCRIPT_CAPTURE_ERROR", ["traceback", "脚本", "script capture exception"]),
]


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


def classify_error(error_text: str) -> str:
    text = (error_text or "").lower()

    for error_type, keywords in ERROR_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return error_type

    return "OTHER"


def shorten_text(text: str, limit: int = 220) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


# def build_error_advice(error_type: str, error_text: str):
#     text = (error_text or "").lower()
#
#     if "selector" in text or "选取器" in text:
#         return {
#             "reason": "UI element locating failed (selector issue or page changed)",
#             "suggestion": "1. Check whether the page structure changed\n2. Check whether the selector is stable\n3. Add more wait time before locating the element"
#         }
#
#     if "timeout" in text or "超时" in text:
#         return {
#             "reason": "Execution timeout (page or service response is too slow)",
#             "suggestion": "1. Check service performance\n2. Increase timeout settings\n3. Check network condition"
#         }
#
#     if "login" in text or "登录" in text:
#         return {
#             "reason": "Login failed",
#             "suggestion": "1. Verify username and password\n2. Verify account permission\n3. Verify environment configuration"
#         }
#
#     if "data" in text or "数据" in text:
#         return {
#             "reason": "Data is missing or invalid",
#             "suggestion": "1. Check whether test data exists\n2. Verify data format\n3. Verify database connectivity"
#         }
#
#     mapping = {
#         "UI_SELECTOR": {
#             "reason": "UI element locating failed",
#             "suggestion": "Check whether the selector is stable and avoid dynamic IDs"
#         },
#         "TIMEOUT": {
#             "reason": "Execution timeout",
#             "suggestion": "Check performance and increase timeout if necessary"
#         },
#         "LOGIN": {
#             "reason": "Login failed",
#             "suggestion": "Check credentials and account permission"
#         },
#         "DATA_ERROR": {
#             "reason": "Data validation failed",
#             "suggestion": "Check test data and business rules"
#         },
#         "NETWORK": {
#             "reason": "Network issue detected",
#             "suggestion": "Check network connectivity and service availability"
#         },
#         "CODE_ERROR": {
#             "reason": "Application code error (logic or boundary issue)",
#             "suggestion": "1. Add boundary checks\n2. Validate array/list before access\n3. Improve error handling"
#         },
#         "SCRIPT_CAPTURE_ERROR": {
#             "reason": "Script execution failed",
#             "suggestion": "Check script logic and exception handling"
#         },
#         "OTHER": {
#             "reason": "Unknown issue",
#             "suggestion": "Review the detailed error log for further analysis"
#         }
#     }
#
#     return mapping.get(error_type, mapping["OTHER"])
def build_error_advice(error_type: str, error_text: str):
    text = (error_text or "").lower()

    # =========================
    # High-priority specific rules
    # =========================

    # 1. Code boundary / array index issue
    if "index out of bounds" in text:
        return {
            "reason": "Application code error: array/list index out of bounds",
            "suggestion": "1. Check list or array size before accessing elements\n2. Add boundary validation\n3. Improve exception handling for empty results"
        }

    # 2. Null / undefined reference
    if "nullpointer" in text or "cannot read" in text or "undefined" in text:
        return {
            "reason": "Application code error: null or undefined reference",
            "suggestion": "1. Add null checks before accessing object fields\n2. Validate returned objects before use\n3. Improve defensive coding and exception handling"
        }

    # 3. UI selector issue
    if "selector" in text or "选取器" in text or "uielement" in text:
        return {
            "reason": "UI element locating failed (selector issue or page changed)",
            "suggestion": "1. Check whether the page structure changed\n2. Check whether the selector is stable\n3. Add more wait time before locating the element"
        }

    # 4. Timeout
    if "timeout" in text or "超时" in text or "timed out" in text:
        return {
            "reason": "Execution timeout (page or service response is too slow)",
            "suggestion": "1. Check service performance\n2. Increase timeout settings\n3. Check network condition"
        }

    # 5. Login issue
    if "login" in text or "登录" in text or "not successfully" in text:
        return {
            "reason": "Login failed",
            "suggestion": "1. Verify username and password\n2. Verify account permission\n3. Verify environment configuration"
        }

    # 6. SAP / API not found
    if "soasapinterface" in text or "data can't found" in text or "data can\"t found" in text or "data not found" in text:
        return {
            "reason": "Required business data was not found in upstream service or database",
            "suggestion": "1. Verify whether the required upstream data exists\n2. Check query conditions and request parameters\n3. Verify service and database connectivity"
        }

    # 7. Generic data issue
    if "validation" in text or "validate" in text or "mismatch" in text or "不一致" in text:
        return {
            "reason": "Data validation failed",
            "suggestion": "1. Verify expected data and actual data\n2. Check business rules\n3. Confirm test data preparation is correct"
        }

    # =========================
    # Fallback by classified type
    # =========================
    mapping = {
        "UI_SELECTOR": {
            "reason": "UI element locating failed",
            "suggestion": "Check whether the selector is stable and avoid dynamic IDs"
        },
        "TIMEOUT": {
            "reason": "Execution timeout",
            "suggestion": "Check performance and increase timeout if necessary"
        },
        "LOGIN": {
            "reason": "Login failed",
            "suggestion": "Check credentials and account permission"
        },
        "DATA_ERROR": {
            "reason": "Data validation failed",
            "suggestion": "Check test data and business rules"
        },
        "NETWORK": {
            "reason": "Network issue detected",
            "suggestion": "Check network connectivity and service availability"
        },
        "SCRIPT_CAPTURE_ERROR": {
            "reason": "Script execution failed",
            "suggestion": "Check script logic and exception handling"
        },
        "CODE_ERROR": {
            "reason": "Application code error",
            "suggestion": "Review code logic, add validation, and improve exception handling"
        },
        "OTHER": {
            "reason": "Unknown issue",
            "suggestion": "Review the detailed error log for further analysis"
        }
    }

    return mapping.get(error_type, mapping["OTHER"])

def extract_error_pattern(error_text: str) -> str:
    text = error_text or ""

    match = re.search(r"Index \d+ out of bounds", text)
    if match:
        return "Index Out Of Bounds"

    # Selector by id
    match = re.search(r"id='([^']+)'", text)
    if match:
        return f"Selector ID: {match.group(1)}"

    # Selector by aaname
    match = re.search(r"aaname='([^']+)'", text)
    if match:
        return f"Selector Name: {match.group(1)}"

    # SAP API
    match = re.search(r"SoaSapInterFace\(([^)]+)\)", text, flags=re.IGNORECASE)
    if match:
        return f"SAP API: {match.group(1)}"

    # Generic error code
    match = re.search(r"code[:=]\s*(\d+)", text, flags=re.IGNORECASE)
    if match:
        return f"Error Code: {match.group(1)}"

    return "Other"


def build_pattern_display(pattern: str):

    if pattern == "Index Out Of Bounds":
        return {
            "title": "Array index out of bounds",
            "suggestion": "Check list/array size before accessing elements; add boundary validation"
        }
    if pattern.startswith("SAP API"):
        api = pattern.split(":")[-1].strip()
        return {
            "title": f"SAP API failure ({api})",
            "suggestion": "Check SAP API status, confirm whether data exists, and verify whether the request timed out"
        }

    if "UserVertifyCode" in pattern:
        return {
            "title": "Login page verification-code element missing",
            "suggestion": "Check whether the login page changed, whether the selector is invalid, and whether additional wait time is needed"
        }

    if "HeadTable_agrTable" in pattern:
        return {
            "title": "Agreement page table element missing",
            "suggestion": "Check the Agreement page structure and verify the selector path"
        }

    if pattern.startswith("Selector ID"):
        selector_id = pattern.split(":")[-1].strip()
        return {
            "title": f"UI element missing ({selector_id})",
            "suggestion": "Check whether the selector is stable and whether the related page changed"
        }

    if pattern.startswith("Selector Name"):
        selector_name = pattern.split(":")[-1].strip()
        return {
            "title": f"UI element missing ({selector_name})",
            "suggestion": "Check whether the selector is stable and whether the related page changed"
        }

    if pattern.startswith("Error Code: 404"):
        return {
            "title": "Requested data not found",
            "suggestion": "Check whether upstream data exists and whether the query condition is correct"
        }

    if pattern.startswith("Error Code: 410"):
        return {
            "title": "Data indexing or boundary issue",
            "suggestion": "Check whether the returned list is empty and verify boundary handling in the script"
        }

    return {
        "title": "Unknown issue",
        "suggestion": "Review the detailed log and classify this issue into a reusable rule if it happens repeatedly"
    }


@router.get("", response_model=FailureAnalysisResponse)
def get_failure_analysis(
    batch_id: int = None,
    cfg_id: int = None,
    uipath_case_name: str = None,
    create_date_from: str = None,
    create_date_to: str = None,
):
    """
    batch_rows tuple order:
    0  BATCH_ID
    1  BATCH_DETAIL_ID
    2  CFG_ID
    3  STATUS
    4  UIPATH_CASE_EXE_ID
    5  ORDER_CASE_EXE_ID
    6  VERIFY_CASE_EXE_ID
    7  CREATE_DATE
    8  FINISH_DATE
    """
    db = SessionLocal()
    try:
        # 1. Query batch_detail first
        batch_query = db.query(BatchDetail).with_entities(
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

        batch_rows: List[Tuple] = batch_query.order_by(
            BatchDetail.BATCH_DETAIL_ID.desc()
        ).limit(MAX_BATCH_ROWS).all()

        if not batch_rows:
            return build_empty_response()

        # 2. Load cfg info and support UiPath case name filtering
        batch_cfg_ids = {row[2] for row in batch_rows if row[2] is not None}

        cfg_map: Dict[int, TestCaseTask] = {}
        if batch_cfg_ids:
            cfg_list = db.query(TestCaseTask).filter(
                TestCaseTask.CFG_ID.in_(list(batch_cfg_ids))
            ).all()
            cfg_map = {x.CFG_ID: x for x in cfg_list}

        if uipath_case_name:
            keyword = uipath_case_name.strip().lower()
            batch_rows = [
                row for row in batch_rows
                if row[2] in cfg_map
                and cfg_map[row[2]].UIPATH_CASE_NAME
                and keyword in cfg_map[row[2]].UIPATH_CASE_NAME.lower()
            ]

        if not batch_rows:
            return build_empty_response()

        filtered_cfg_ids = {row[2] for row in batch_rows if row[2] is not None}
        if filtered_cfg_ids:
            cfg_list = db.query(TestCaseTask).filter(
                TestCaseTask.CFG_ID.in_(list(filtered_cfg_ids))
            ).all()
            cfg_map = {x.CFG_ID: x for x in cfg_list}
        else:
            cfg_map = {}

        # 3. Summary
        total = len(batch_rows)
        failed_batch_rows = [row for row in batch_rows if row[3] in FAIL_STATES]
        success_batch_rows = [row for row in batch_rows if row[3] in SUCCESS_STATES]

        failed = len(failed_batch_rows)
        success = len(success_batch_rows)
        success_rate = round((success / total) * 100, 2) if total > 0 else 0

        if not failed_batch_rows:
            return {
                "summary": {
                    "total": total,
                    "failed": failed,
                    "success": success,
                    "success_rate": success_rate,
                },
                "stage_distribution": [],
                "error_type_distribution": [],
                "error_pattern_distribution": [],
                "top_issue": None,
                "failure_details": [],
            }

        # 4. Collect failed case execution ids only
        failed_case_exe_ids = set()
        for row in failed_batch_rows:
            status = row[3]
            if status == 3 and row[4] and row[4] > 0:
                failed_case_exe_ids.add(row[4])
            elif status == 11 and row[5] and row[5] > 0:
                failed_case_exe_ids.add(row[5])
            elif status == 6 and row[6] and row[6] > 0:
                failed_case_exe_ids.add(row[6])

        if not failed_case_exe_ids:
            return {
                "summary": {
                    "total": total,
                    "failed": failed,
                    "success": success,
                    "success_rate": success_rate,
                },
                "stage_distribution": [],
                "error_type_distribution": [],
                "error_pattern_distribution": [],
                "top_issue": None,
                "failure_details": [],
            }

        # 5. Query case executions
        case_rows = db.query(TestCaseExecution).filter(
            TestCaseExecution.TEST_CASE_EXE_ID.in_(list(failed_case_exe_ids))
        ).all()

        case_map: Dict[int, TestCaseExecution] = {
            x.TEST_CASE_EXE_ID: x for x in case_rows
        }

        # 6. Query related component executions
        component_rows = db.query(TestComponentExecution).filter(
            TestComponentExecution.TEST_CASE_EXE_ID.in_(list(failed_case_exe_ids))
        ).order_by(
            TestComponentExecution.TEST_CASE_EXE_ID.asc(),
            TestComponentExecution.TEST_COMPONENT_EXE_ID.desc()
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

        # 7. Build detail rows and counters
        stage_counter = Counter()
        error_type_counter = Counter()
        pattern_counter = Counter()
        failure_details = []

        for batch_row in failed_batch_rows:
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
                continue

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

            error_type = classify_error(base_error)
            advice = build_error_advice(error_type, base_error)
            pattern = extract_error_pattern(base_error)

            stage_counter[stage] += 1
            error_type_counter[error_type] += 1
            pattern_counter[pattern] += 1

            cfg_info = cfg_map.get(cfg_value)

            failure_details.append({
                "test_case_exe_id": current_case_exe_id,
                "batch_id": batch_id_value,
                "cfg_id": cfg_value,
                "uipath_case_name": cfg_info.UIPATH_CASE_NAME if cfg_info else None,
                "stage": stage,
                "state": state,
                "state_text": state_text,
                "error_type": error_type,
                "error_reason": advice["reason"],
                "suggestion": advice["suggestion"],
                "error_pattern": pattern,
                "error_summary": shorten_text(base_error, 220) if base_error else "-",
                "component_name": component_name if component_name else "Not Triggered",
                "create_date": create_date_value.isoformat(sep=" ") if create_date_value else None,
                "finish_date": finish_date_value.isoformat(sep=" ") if finish_date_value else None,
            })

        stage_distribution = [
            {"stage": k, "count": v}
            for k, v in sorted(stage_counter.items(), key=lambda x: x[1], reverse=True)
        ]

        error_type_distribution = [
            {"error_type": k, "count": v}
            for k, v in sorted(error_type_counter.items(), key=lambda x: x[1], reverse=True)
        ]

        pattern_distribution = []
        for k, v in sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True):
            display = build_pattern_display(k)
            percent = round((v / failed) * 100, 1) if failed > 0 else 0

            pattern_distribution.append({
                "pattern": k,
                "title": display["title"],
                "suggestion": display["suggestion"],
                "count": v,
                "percent": percent,
            })

        top_issue = pattern_distribution[0] if pattern_distribution else None

        return {
            "summary": {
                "total": total,
                "failed": failed,
                "success": success,
                "success_rate": success_rate,
            },
            "stage_distribution": stage_distribution,
            "error_type_distribution": error_type_distribution,
            "error_pattern_distribution": pattern_distribution,
            "top_issue": top_issue,
            "failure_details": failure_details,
        }

    finally:
        db.close()