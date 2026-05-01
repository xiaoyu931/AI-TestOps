import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote

import pytest
import pymysql


def pytest_addoption(parser):
    parser.addoption(
        "--testops-batch-id",
        action="store",
        default=os.getenv("TESTOPS_BATCH_ID", ""),
        help="AI-TestOps batch_id for this Playwright run",
    )


def _load_local_database_url():
    try:
        project_root = Path(__file__).resolve().parent

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from database import DATABASE_URL

        return DATABASE_URL
    except Exception:
        return ""


def _parse_database_url(db_url):
    if not db_url:
        return None

    parsed = urlparse(db_url)

    return {
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or "root"),
        "password": unquote(parsed.password or ""),
        "database": parsed.path.lstrip("/") or "autotest_data",
    }


def _get_db_config():
    db_url = os.getenv("TESTOPS_DB_URL", "")

    if db_url:
        parsed_config = _parse_database_url(db_url)
        if parsed_config:
            return parsed_config

    local_db_url = _load_local_database_url()

    if local_db_url:
        parsed_config = _parse_database_url(local_db_url)
        if parsed_config:
            return parsed_config

    return {
        "host": os.getenv("TESTOPS_DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("TESTOPS_DB_PORT", "3306")),
        "user": os.getenv("TESTOPS_DB_USER", "root"),
        "password": os.getenv("TESTOPS_DB_PASSWORD", ""),
        "database": os.getenv("TESTOPS_DB_NAME", "autotest_data"),
    }

def _normalize_nodeid(nodeid):
    parts = nodeid.split("::")
    if not parts:
        return nodeid

    last = parts[-1]
    if "[" in last and last.endswith("]"):
        last = last.split("[", 1)[0]
        parts[-1] = last

    return "::".join(parts)

def _connect():
    cfg = _get_db_config()

    if not cfg["password"]:
        print("[TestOps] DB password is empty, skip DB reporting.")
        return None

    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def _has_value(value):
    return value is not None and value != "" and value != 0 and value != "0"


def _safe_json_loads(text):
    if not text:
        return {}

    try:
        return json.loads(text)
    except Exception:
        return {}


def _to_int_or_zero(value):
    try:
        return int(value)
    except Exception:
        return 0


def _short(value, limit):
    if value is None:
        return None
    return str(value)[:limit]

def _extract_error_summary(report):
    if not report or not report.failed:
        return None

    longrepr = getattr(report, "longrepr", None)

    if not longrepr:
        return None

    text = str(longrepr)

    if not text:
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in reversed(lines):
        if line.startswith("E       AssertionError:"):
            return line.replace("E       AssertionError:", "AssertionError:").strip()

    for line in reversed(lines):
        if line.startswith("AssertionError:"):
            return line.strip()

    for line in reversed(lines):
        if line.startswith("E       "):
            return line.replace("E       ", "").strip()

    for line in reversed(lines):
        if "TimeoutError:" in line:
            return line[line.find("TimeoutError:"):].strip()

    for line in reversed(lines):
        if "Error:" in line:
            return line[line.find("Error:"):].strip()

    for line in lines:
        if line.startswith(">"):
            continue
        if len(line) > 20:
            return line[:1000]

    return text[:1000]



def _load_case_config(conn, nodeid):
    normalized_nodeid = _normalize_nodeid(nodeid)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM cfg_test_case_task
            WHERE UIPATH_ENTRY = %s
              AND STATE = 1
            ORDER BY CFG_ID DESC
            LIMIT 1
            """,
            (normalized_nodeid,),
        )
        return cursor.fetchone()



def _load_playwright_input(conn, cfg_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT TEST_DATA
            FROM cfg_test_case_data
            WHERE CFG_ID = %s
              AND STATE = 1
              AND UIPATH_FLAG = 1
            ORDER BY CFG_DATA_ID DESC
            LIMIT 1
            """,
            (cfg_id,),
        )
        row = cursor.fetchone()

    if not row:
        return {}

    return _safe_json_loads(row.get("TEST_DATA"))


def _success_state_after_playwright(case_config):
    if _has_value(case_config.get("TEST_CASE_TEMPLATE_ID")):
        return 8

    if _has_value(case_config.get("VERIFY_TEST_CASE_TEMPLATE_ID")):
        return 10

    return 13


def _batch_task_status_after_case_state(state):
    if state in (3, 13, 14):
        return 2

    if state == 10:
        return 1

    return 0


def _create_case_execution(conn, case_config, nodeid, batch_id):
    now = datetime.now()
    playwright_input = _load_playwright_input(conn, case_config["CFG_ID"])

    result_data = {
        "framework": "playwright",
        "phase": "running",
        "batch_id": batch_id,
        "nodeid": nodeid,
        "playwright_input": playwright_input,
    }

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO test_case_execution (
                REL_CASE_EXE_ID,
                CFG_ID,
                TEST_CASE_TEMPLATE_ID,
                TEST_CASE_NAME,
                TEST_INST_ID,
                EXECUTION_ENVIRONMENT,
                EXECUTION_MACHINE,
                IS_PRE_TASK,
                STATE,
                OMP_BATCH_ID,
                SOURCE_DATA,
                TEST_RESULT_DATA,
                ERROR_MESSAGE,
                TENANT_ID,
                CREATE_DATE,
                FINISH_DATE,
                CASE_ID,
                PLAN_ID,
                TASK_STATUS
            ) VALUES (
                NULL,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                0,
                1,
                0,
                %s,
                %s,
                NULL,
                %s,
                %s,
                NULL,
                %s,
                0,
                0
            )
            """,
            (
                case_config.get("CFG_ID"),
                case_config.get("TEST_CASE_TEMPLATE_ID"),
                _short(case_config.get("UIPATH_CASE_NAME") or nodeid.split("::")[-1], 100),
                _short(case_config.get("TEST_INST_ID"), 50),
                _short(case_config.get("EXECUTION_ENVIRONMENT"), 10),
                _short(case_config.get("EXECUTION_MACHINE"), 20),
                json.dumps(playwright_input, ensure_ascii=False),
                json.dumps(result_data, ensure_ascii=False),
                _short(case_config.get("TENANT_ID"), 6),
                now,
                _to_int_or_zero(case_config.get("CASE_ID")),
            ),
        )

        case_exe_id = cursor.lastrowid

    conn.commit()
    return case_exe_id


def _update_case_execution(conn, case_exe_id, state, report, batch_id):
    now = datetime.now()

    error_message = None
    if report.failed:
        error_message = _extract_error_summary(report)

    result_data = {
        "framework": "playwright",
        "phase": "finished",
        "batch_id": batch_id,
        "nodeid": report.nodeid,
        "outcome": report.outcome,
        "duration": getattr(report, "duration", None),
        "state": state,
    }

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE test_case_execution
            SET STATE = %s,
                TEST_RESULT_DATA = %s,
                ERROR_MESSAGE = %s,
                FINISH_DATE = %s
            WHERE TEST_CASE_EXE_ID = %s
            """,
            (
                state,
                json.dumps(result_data, ensure_ascii=False),
                error_message,
                now,
                case_exe_id,
            ),
        )

    conn.commit()


def _sync_batch_detail(conn, batch_id, cfg_id, case_exe_id, state):
    if not batch_id or not cfg_id or not case_exe_id:
        return

    task_status = _batch_task_status_after_case_state(state)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE batch_detail
            SET UIPATH_CASE_EXE_ID = %s,
                STATUS = %s,
                TASK_STATUS = %s,
                FINISH_DATE = %s
            WHERE BATCH_ID = %s
              AND CFG_ID = %s
            """,
            (
                case_exe_id,
                state,
                task_status,
                datetime.now(),
                batch_id,
                cfg_id,
            ),
        )

    conn.commit()

def _calculate_pass_rate(conn, batch_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT STATUS
            FROM batch_detail
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )
        rows = cursor.fetchall()

    total = len(rows)

    if total == 0:
        return "0%"

    success_count = 0

    for row in rows:
        if row.get("STATUS") in (5, 13, 14):
            success_count += 1

    return f"{round(success_count / total * 100)}%"

def _sync_test_plan_if_batch_finished(conn, batch_id):
    if not batch_id:
        return

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) AS total_count
            FROM batch_detail
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )
        total_row = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*) AS finished_count
            FROM batch_detail
            WHERE BATCH_ID = %s
              AND TASK_STATUS = 2
            """,
            (batch_id,),
        )
        finished_row = cursor.fetchone()

    total_count = total_row.get("total_count", 0) if total_row else 0
    finished_count = finished_row.get("finished_count", 0) if finished_row else 0

    if total_count == 0 or total_count != finished_count:
        return

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT SEND_EMAIL
            FROM test_plan
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )
        plan_row = cursor.fetchone()

    if not plan_row:
        return

    send_email = plan_row.get("SEND_EMAIL")
    pass_rate = _calculate_pass_rate(conn, batch_id)

    if send_email == 0:
        task_status = 5
    else:
        return

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE test_plan
            SET TASK_STATUS = %s,
                PASS_RATE = %s,
                FINISH_DATE = %s
            WHERE BATCH_ID = %s
            """,
            (
                task_status,
                pass_rate,
                datetime.now(),
                batch_id,
            ),
        )

    conn.commit()

def _create_component_execution(conn, case_exe_id, case_config, batch_id, state, report):
    now = datetime.now()

    component_state = 2 if state in (5, 8, 10, 13, 14) else 3

    playwright_input = _load_playwright_input(conn, case_config["CFG_ID"])

    result_data = {
        "framework": "playwright",
        "component": "Playwright Execution",
        "batch_id": batch_id,
        "cfg_id": case_config.get("CFG_ID"),
        "nodeid": getattr(report, "nodeid", ""),
        "outcome": getattr(report, "outcome", ""),
        "duration": getattr(report, "duration", None),
        "case_state": state,
    }

    error_summary = _extract_error_summary(report)

    python_error_message = None
    system_error_message = None

    if report.failed:
        python_error_message = error_summary
        system_error_message = error_summary

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO test_component_execution (
                TEST_CASE_EXE_ID,
                TEST_CASE_TEMPLATE_ID,
                TEST_COMPONENT_ID,
                TEST_COMPONENT_NAME,
                STATE,
                COMPONENT_IN_PARAM,
                COMPONENT_RESULT_DATA,
                PYTHON_ERROR_MESSAGE,
                SYSTEM_ERROR_MESSAGE,
                TENANT_ID,
                CREATE_DATE,
                FINISH_DATE
            ) VALUES (
                %s,
                %s,
                NULL,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                case_exe_id,
                case_config.get("TEST_CASE_TEMPLATE_ID"),
                "Playwright Execution",
                component_state,
                json.dumps(playwright_input, ensure_ascii=False),
                json.dumps(result_data, ensure_ascii=False),
                python_error_message,
                system_error_message,
                _short(case_config.get("TENANT_ID"), 6),
                now,
                now,
            ),
        )

    conn.commit()



@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    batch_id = _to_int_or_zero(item.config.getoption("--testops-batch-id"))

    if not batch_id:
        print("[TestOps] Missing --testops-batch-id, skip DB reporting.")
        return

    conn = _connect()
    if not conn:
        return

    try:
        normalized_nodeid = _normalize_nodeid(item.nodeid)
        case_config = _load_case_config(conn, normalized_nodeid)

        if not case_config:
            print(f"[TestOps] No cfg_test_case_task found for nodeid: {item.nodeid}")
            conn.close()
            return

        case_exe_id = _create_case_execution(
            conn=conn,
            case_config=case_config,
            nodeid=normalized_nodeid,
            batch_id=batch_id,
        )

        item._testops_conn = conn
        item._testops_batch_id = batch_id
        item._testops_case_config = case_config
        item._testops_case_exe_id = case_exe_id
        item._testops_finalized = False

        print(
            "[TestOps] Created test_case_execution: "
            f"TEST_CASE_EXE_ID={case_exe_id}, CFG_ID={case_config.get('CFG_ID')}, BATCH_ID={batch_id}"
        )

    except Exception as exc:
        conn.rollback()
        conn.close()
        print(f"[TestOps] Create test_case_execution failed: {exc}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    case_exe_id = getattr(item, "_testops_case_exe_id", None)
    case_config = getattr(item, "_testops_case_config", None)
    conn = getattr(item, "_testops_conn", None)
    batch_id = getattr(item, "_testops_batch_id", 0)

    if not case_exe_id or not case_config or not conn or not batch_id:
        return

    should_finalize = False
    final_state = None

    if report.failed:
        should_finalize = True
        final_state = 3
    elif report.when == "call" and report.passed:
        should_finalize = True
        final_state = _success_state_after_playwright(case_config)

    if not should_finalize:
        return

    if getattr(item, "_testops_finalized", False) and final_state != 3:
        return

    try:
        _update_case_execution(
            conn=conn,
            case_exe_id=case_exe_id,
            state=final_state,
            report=report,
            batch_id=batch_id,
        )

        _create_component_execution(
            conn=conn,
            case_exe_id=case_exe_id,
            case_config=case_config,
            batch_id=batch_id,
            state=final_state,
            report=report,
        )

        _sync_batch_detail(
            conn=conn,
            batch_id=batch_id,
            cfg_id=case_config.get("CFG_ID"),
            case_exe_id=case_exe_id,
            state=final_state,
        )

        _sync_test_plan_if_batch_finished(
            conn=conn,
            batch_id=batch_id,
        )

        item._testops_finalized = True

        print(
            "[TestOps] Finalized test_case_execution and batch_detail: "
            f"TEST_CASE_EXE_ID={case_exe_id}, STATE={final_state}, BATCH_ID={batch_id}"
        )

    except Exception as exc:
        conn.rollback()
        print(f"[TestOps] Finalize test_case_execution failed: {exc}")


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    conn = getattr(item, "_testops_conn", None)

    if conn:
        conn.close()
