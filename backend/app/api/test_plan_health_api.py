from fastapi import APIRouter, Query
from collections import defaultdict, Counter
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re

from app.database import SessionLocal
from app.analyzer.analyzer_core import analyze_error
from app.models.test_plan_model import TestPlan
from app.models.batch_detail_model import BatchDetail
from app.models.test_case_execution_model import TestCaseExecution
from app.models.test_component_execution_model import TestComponentExecution


router = APIRouter(prefix="/test-plan-health", tags=["Test Plan Health"])

FAIL_STATES = [3, 6, 11]
LOOKBACK_DAYS = 30
TREND_RUNS = 3
ATTENTION_LIMIT = 5
ROOT_CAUSE_LIMIT = 10

# 你当前重点关注的固定核心计划
CORE_PLAN_NAMES = {
    "Regression 1 Mobile Automation",
    "Regression 2 OpennetNewOM Automation",
    "Regression 3 WS Automation",
    "Regression 4 NewOmMobile Automation",
}


# ===============================
# 基础工具
# ===============================
def calculate_success_rate(total: int, failed: int) -> float:
    if total == 0:
        return 0
    return round((total - failed) / total * 100, 2)


def get_trend(values: List[float]) -> str:
    """
    values 按时间从旧到新
    """
    if len(values) < 2:
        return "STABLE"

    prev = values[-2]
    last = values[-1]

    if last > prev:
        return "UP"
    if last < prev:
        return "DOWN"
    return "STABLE"


def get_risk_level(success_rate: float, trend: str, failed_count: int) -> str:
    """
    简单风险分级：
    - 成功率 < 60 或趋势下降 或失败数 > 10 => HIGH
    - 成功率 < 80 或失败数 > 3 => MEDIUM
    - 其余 LOW
    """
    if success_rate < 60 or trend == "DOWN" or failed_count > 10:
        return "HIGH"
    if success_rate < 80 or failed_count > 3:
        return "MEDIUM"
    return "LOW"


def is_data_prep_plan(plan_name: str) -> bool:
    if not plan_name:
        return False

    text = plan_name.lower()
    keywords = [
        "pre",
        "prepare",
        "fixedpre",
        "mobilepre",
        "newommobilepre",
        "wspre",
        "smokepre",
        "pbx pre",
        "ose pre",
    ]
    return any(k in text for k in keywords)


def is_roadmap_plan(plan_name: str) -> bool:
    if not plan_name:
        return False
    return "roadmap" in plan_name.lower()


def is_core_plan(plan_name: str, plan_runs: Optional[List[TestPlan]] = None) -> bool:
    """
    当前先按固定白名单识别。
    后续如果你想改成“最近30天执行次数 >= N”也可以在这里扩展。
    """
    if not plan_name:
        return False
    return plan_name in CORE_PLAN_NAMES


def get_plan_category(plan_name: str, plan_runs: Optional[List[TestPlan]] = None) -> str:
    if is_core_plan(plan_name, plan_runs):
        return "CORE_REGRESSION"
    if is_data_prep_plan(plan_name):
        return "DATA_PREP"
    if is_roadmap_plan(plan_name):
        return "ROADMAP"
    return "OTHER"


def should_collapse_plan(item: Dict) -> bool:
    """
    默认收起：
    - 数据准备计划
    - 最近一次 total = 0（没真正跑起来）
    """
    if item.get("plan_category") == "DATA_PREP":
        return True
    if item.get("latest_total", 0) == 0:
        return True
    return False


def calc_attention_score(item: Dict) -> int:
    """
    Attention 排序打分
    """
    score = 0

    success_rate = item.get("latest_success_rate", 0)
    failed = item.get("latest_failed", 0)
    trend = item.get("trend", "STABLE")
    risk = item.get("risk_level", "LOW")

    if success_rate < 50:
        score += 50
    elif success_rate < 80:
        score += 20

    score += failed * 2

    if trend == "DOWN":
        score += 20

    if risk == "HIGH":
        score += 20
    elif risk == "MEDIUM":
        score += 10

    return score


# ===============================
# JSON / error text 提取
# ===============================
def safe_json_loads(text: Optional[str]):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def normalize_error_data(value) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return " | ".join([str(x) for x in value if x])
    if isinstance(value, str):
        return value
    return str(value)


def extract_error_text_from_case(case_row: Optional[TestCaseExecution]) -> str:
    if not case_row:
        return ""

    if case_row.TEST_RESULT_DATA:
        obj = safe_json_loads(case_row.TEST_RESULT_DATA)
        if isinstance(obj, dict):
            error_data = obj.get("errorData")
            if error_data:
                return normalize_error_data(error_data)
            if obj.get("message"):
                return str(obj.get("message"))
        return str(case_row.TEST_RESULT_DATA)

    if case_row.ERROR_MESSAGE:
        obj = safe_json_loads(case_row.ERROR_MESSAGE)
        if isinstance(obj, dict):
            error_data = obj.get("errorData")
            if error_data:
                return normalize_error_data(error_data)
            if obj.get("message"):
                return str(obj.get("message"))
        return str(case_row.ERROR_MESSAGE)

    return ""


def extract_error_text_from_component(component_row: Optional[TestComponentExecution]) -> str:
    if not component_row:
        return ""

    if component_row.COMPONENT_RESULT_DATA:
        obj = safe_json_loads(component_row.COMPONENT_RESULT_DATA)
        if isinstance(obj, dict):
            data_obj = obj.get("data")
            if isinstance(data_obj, dict):
                error_data = data_obj.get("errorData")
                if error_data:
                    return normalize_error_data(error_data)

            error_data = obj.get("errorData")
            if error_data:
                return normalize_error_data(error_data)

            if obj.get("message"):
                return str(obj.get("message"))
        return str(component_row.COMPONENT_RESULT_DATA)

    if component_row.PYTHON_ERROR_MESSAGE:
        obj = safe_json_loads(component_row.PYTHON_ERROR_MESSAGE)
        if isinstance(obj, dict):
            error_data = obj.get("errorData")
            if error_data:
                return normalize_error_data(error_data)
            if obj.get("message"):
                return str(obj.get("message"))
        return str(component_row.PYTHON_ERROR_MESSAGE)

    if component_row.SYSTEM_ERROR_MESSAGE:
        obj = safe_json_loads(component_row.SYSTEM_ERROR_MESSAGE)
        if isinstance(obj, dict):
            error_data = obj.get("errorData")
            if error_data:
                return normalize_error_data(error_data)
            if obj.get("message"):
                return str(obj.get("message"))
        return str(component_row.SYSTEM_ERROR_MESSAGE)

    return ""


def extract_error_text(case_row: Optional[TestCaseExecution], component_row: Optional[TestComponentExecution]) -> str:
    """
    优先 component，再 fallback case
    """
    text = extract_error_text_from_component(component_row)
    if text:
        return text
    return extract_error_text_from_case(case_row)


# ===============================
# Top Issue 分类（规则版）
# ===============================
def classify_top_issue(error_text: str, plan_name: str) -> str:
    if not error_text:
        return "Unknown"

    text = error_text.lower()

    # 1. timeout
    if "timeout" in text or "timed out" in text or "超时" in text:
        return "Timeout"

    # 2. selector / ui
    if "selector" in text or "选取器" in text or "ui element" in text or "uielement" in text:
        match = re.search(r"id='([^']+)'", error_text)
        if match:
            return f"Selector: {match.group(1)}"

        match = re.search(r"aaname='([^']+)'", error_text)
        if match:
            return f"Selector: {match.group(1)}"

        return "UI Selector Issue"

    # 3. SAP / API
    match = re.search(r"SoaSapInterFace\(([^)]+)\)", error_text)
    if match:
        return f"SAP API: {match.group(1)}"

    if "api" in text or "interface" in text:
        return "API Failure"

    # 4. code error
    if "index out of bounds" in text:
        return "Code Error: Index Out Of Bounds"

    if "nullpointer" in text or ("null" in text and "exception" in text):
        return "Code Error: Null Pointer"

    # 5. data / not found
    if "not found" in text or "no data" in text or "data can" in text:
        if is_data_prep_plan(plan_name):
            return "Data Creation Failed"
        return "Data Missing"

    # 6. login
    if "login" in text or "登录" in text:
        return "Login Failed"

    return "Other"

def analyze_top_issue(db, error_text: str, plan_name: str) -> str:
    analysis = analyze_error(db, error_text)

    if analysis.get("matched"):
        return analysis.get("root_cause") or "Unknown"

    return classify_top_issue(error_text, plan_name)



# ===============================
# 辅助：最近一个月失败趋势
# ===============================
def build_monthly_failure_trend(plan_runs: List[TestPlan], batch_rows_map: Dict[int, List[BatchDetail]]) -> List[Dict]:
    runs = sorted(plan_runs, key=lambda x: x.CREATE_DATE or datetime.min)

    trend_list = []
    for run in runs:
        rows = batch_rows_map.get(run.BATCH_ID, [])
        total = len(rows)
        failed = len([x for x in rows if x.STATUS in FAIL_STATES])
        success_rate = calculate_success_rate(total, failed)

        trend_list.append({
            "batch_id": run.BATCH_ID,
            "create_date": run.CREATE_DATE.isoformat(sep=" ") if run.CREATE_DATE else None,
            "total": total,
            "failed": failed,
            "success_rate": success_rate,
        })

    return trend_list


def get_case_exe_id_from_batch_row(row: BatchDetail) -> Optional[int]:
    """
    根据失败状态正确取当前失败对应的 case_exe_id
    """
    if row.STATUS == 3 and row.UIPATH_CASE_EXE_ID:
        return row.UIPATH_CASE_EXE_ID
    if row.STATUS == 6 and row.VERIFY_CASE_EXE_ID:
        return row.VERIFY_CASE_EXE_ID
    if row.STATUS == 11 and row.ORDER_CASE_EXE_ID:
        return row.ORDER_CASE_EXE_ID
    return None


# ===============================
# 主接口
# ===============================
@router.get("")
def get_test_plan_health():
    db = SessionLocal()

    try:
        # 1. 只查最近30天的 test_plan
        cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)

        plans = db.query(TestPlan).filter(
            TestPlan.CREATE_DATE >= cutoff
        ).order_by(TestPlan.CREATE_DATE.desc()).all()

        if not plans:
            return {
                "attention_plans": [],
                "core_plans": [],
                "non_core_plans": [],
                "collapsed_plans": [],
                "plans": [],
                "root_cause_ranking": []
            }

        # 2. 按 plan_name 分组
        grouped_plans: Dict[str, List[TestPlan]] = defaultdict(list)
        for p in plans:
            if p.BATCH_NAME:
                grouped_plans[p.BATCH_NAME].append(p)

        # 3. 预取所有 batch_detail
        all_batch_ids = [p.BATCH_ID for p in plans if p.BATCH_ID is not None]

        batch_rows = db.query(BatchDetail).filter(
            BatchDetail.BATCH_ID.in_(all_batch_ids)
        ).all()

        batch_rows_map: Dict[int, List[BatchDetail]] = defaultdict(list)
        for row in batch_rows:
            batch_rows_map[row.BATCH_ID].append(row)

        results = []

        # ===============================
        # 第一阶段：轻计算（所有计划）
        # trend 保留最近3次，但只查 BatchDetail
        # ===============================
        for plan_name, plan_runs in grouped_plans.items():
            sorted_runs = sorted(
                plan_runs,
                key=lambda x: x.CREATE_DATE or datetime.min,
                reverse=True
            )[:TREND_RUNS]

            trend_values: List[float] = []

            latest_total = 0
            latest_failed = 0
            latest_success_rate = 0
            latest_batch_id = None
            latest_create_date = None

            for idx, run in enumerate(sorted_runs):
                rows = batch_rows_map.get(run.BATCH_ID, [])
                total = len(rows)
                failed = len([x for x in rows if x.STATUS in FAIL_STATES])
                success_rate = calculate_success_rate(total, failed)

                trend_values.append(success_rate)

                if idx == 0:
                    latest_total = total
                    latest_failed = failed
                    latest_success_rate = success_rate
                    latest_batch_id = run.BATCH_ID
                    latest_create_date = run.CREATE_DATE.isoformat(sep=" ") if run.CREATE_DATE else None

            trend_values = list(reversed(trend_values))
            trend = get_trend(trend_values)
            risk_level = get_risk_level(latest_success_rate, trend, latest_failed)

            monthly_failure_trend = build_monthly_failure_trend(plan_runs, batch_rows_map)

            item = {
                "plan_name": plan_name,
                "latest_batch_id": latest_batch_id,
                "latest_create_date": latest_create_date,
                "latest_success_rate": latest_success_rate,
                "latest_total": latest_total,
                "latest_failed": latest_failed,
                "trend": trend,
                "trend_values": trend_values,
                "top_issue": None,  # 第二阶段再填
                "risk_level": risk_level,
                "is_core": is_core_plan(plan_name, plan_runs),
                "is_core_plan": is_core_plan(plan_name, plan_runs),
                "plan_category": get_plan_category(plan_name, plan_runs),
                "is_data_prep": is_data_prep_plan(plan_name),
                "is_data_prep_plan": is_data_prep_plan(plan_name),
                "is_roadmap_plan": is_roadmap_plan(plan_name),
                "monthly_failure_trend": monthly_failure_trend,
            }

            results.append(item)

        # 4. 风险排序
        risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        results = sorted(
            results,
            key=lambda x: (
                risk_order.get(x["risk_level"], 99),
                -x["latest_failed"],
                x["latest_success_rate"]
            )
        )

        # 5. 分类
        core_plans = [x for x in results if x["is_core"]]
        collapsed_plans = [x for x in results if not x["is_core"] and should_collapse_plan(x)]
        non_core_plans = [x for x in results if not x["is_core"] and not should_collapse_plan(x)]

        # Attention 只从 Core Plans 中挑
        attention_candidates = [
            x for x in core_plans
            if (
                x["latest_success_rate"] < 80
                or x["trend"] == "DOWN"
                or x["latest_failed"] > 3
            )
        ]

        attention_plans = sorted(
            attention_candidates,
            key=lambda x: calc_attention_score(x),
            reverse=True
        )[:ATTENTION_LIMIT]

        # ===============================
        # 第二阶段：只对 attention + core 做重分析
        # root cause 只分析最新一次执行
        # ===============================
        deep_plan_names = {
            x["plan_name"] for x in (attention_plans + core_plans)
        }

        deep_items = [
            x for x in results
            if x["plan_name"] in deep_plan_names and x.get("latest_batch_id")
        ]

        deep_batch_ids = [x["latest_batch_id"] for x in deep_items if x.get("latest_batch_id")]

        deep_batch_fail_rows = []
        if deep_batch_ids:
            deep_batch_fail_rows = db.query(BatchDetail).filter(
                BatchDetail.BATCH_ID.in_(deep_batch_ids),
                BatchDetail.STATUS.in_(FAIL_STATES)
            ).all()

        deep_batch_fail_rows_map: Dict[int, List[BatchDetail]] = defaultdict(list)
        for row in deep_batch_fail_rows:
            deep_batch_fail_rows_map[row.BATCH_ID].append(row)

        # 收集全部 case_exe_ids
        all_case_exe_ids = []
        for item in deep_items:
            batch_id = item["latest_batch_id"]
            for row in deep_batch_fail_rows_map.get(batch_id, []):
                cid = get_case_exe_id_from_batch_row(row)
                if cid:
                    all_case_exe_ids.append(cid)

        all_case_exe_ids = list(set(all_case_exe_ids))

        # 批量查 case_rows
        case_map = {}
        if all_case_exe_ids:
            case_rows = db.query(TestCaseExecution).filter(
                TestCaseExecution.TEST_CASE_EXE_ID.in_(all_case_exe_ids)
            ).all()
            case_map = {x.TEST_CASE_EXE_ID: x for x in case_rows}

        # 批量查 component_rows
        component_map = {}
        if all_case_exe_ids:
            component_rows = db.query(TestComponentExecution).filter(
                TestComponentExecution.TEST_CASE_EXE_ID.in_(all_case_exe_ids)
            ).order_by(
                TestComponentExecution.TEST_CASE_EXE_ID.asc(),
                TestComponentExecution.TEST_COMPONENT_EXE_ID.desc()
            ).all()

            # 优先失败组件；否则最新组件
            component_latest_map = {}
            component_failed_map = {}

            for c in component_rows:
                cid = c.TEST_CASE_EXE_ID

                if cid not in component_latest_map:
                    component_latest_map[cid] = c

                if c.STATE == 3 and cid not in component_failed_map:
                    component_failed_map[cid] = c

            for cid, latest_row in component_latest_map.items():
                component_map[cid] = component_failed_map.get(cid, latest_row)

        global_root_counter = Counter()
        INVALID_ISSUES = {"Other", "Unknown", "", None}

        for item in deep_items:
            batch_id = item["latest_batch_id"]
            issue_counter = Counter()

            for row in deep_batch_fail_rows_map.get(batch_id, []):
                cid = get_case_exe_id_from_batch_row(row)
                if not cid:
                    continue

                case_row = case_map.get(cid)
                component_row = component_map.get(cid)

                error_text = extract_error_text(case_row, component_row)
                issue = analyze_top_issue(db, error_text, item["plan_name"])

                issue_counter[issue] += 1
                global_root_counter[issue] += 1

            valid_issue_items = [
                (k, v) for k, v in issue_counter.items()
                if k not in INVALID_ISSUES
            ]

            if valid_issue_items:
                item["top_issue"] = sorted(valid_issue_items, key=lambda x: x[1], reverse=True)[0][0]
            elif issue_counter:
                item["top_issue"] = issue_counter.most_common(1)[0][0]
            else:
                item["top_issue"] = None

        root_cause_ranking = [
            {"pattern": k, "count": v}
            for k, v in global_root_counter.most_common()
            if k not in INVALID_ISSUES
        ][:ROOT_CAUSE_LIMIT]

        return {
            "attention_plans": attention_plans,
            "core_plans": core_plans,
            "non_core_plans": non_core_plans,
            "collapsed_plans": collapsed_plans,
            "plans": results,
            "root_cause_ranking": root_cause_ranking
        }

    finally:
        db.close()


# ===============================
# 某个计划最近一个月失败趋势
# ===============================
@router.get("/monthly-trend")
def get_plan_monthly_trend(
    plan_name: str = Query(..., description="Plan name")
):
    db = SessionLocal()

    try:
        cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)

        plan_runs = db.query(TestPlan).filter(
            TestPlan.BATCH_NAME == plan_name,
            TestPlan.CREATE_DATE >= cutoff
        ).order_by(TestPlan.CREATE_DATE.asc()).all()

        if not plan_runs:
            return {
                "plan_name": plan_name,
                "monthly_failure_trend": []
            }

        batch_ids = [x.BATCH_ID for x in plan_runs if x.BATCH_ID is not None]

        batch_rows = []
        if batch_ids:
            batch_rows = db.query(BatchDetail).filter(
                BatchDetail.BATCH_ID.in_(batch_ids)
            ).all()

        batch_rows_map: Dict[int, List[BatchDetail]] = defaultdict(list)
        for row in batch_rows:
            batch_rows_map[row.BATCH_ID].append(row)

        trend_list = build_monthly_failure_trend(plan_runs, batch_rows_map)

        return {
            "plan_name": plan_name,
            "monthly_failure_trend": trend_list
        }

    finally:
        db.close()