import json
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ERROR_KB_XLSX = DATA_DIR / "error_knowledge_base.xlsx"
CAUSE_MAPPING_XLSX = DATA_DIR / "error_cause_mapping.xlsx"

RULES_OUTPUT = DATA_DIR / "cleaned_error_rules.json"
KNOWLEDGE_OUTPUT = DATA_DIR / "error_cause_mapping_cleaned.json"
CANDIDATE_OUTPUT = DATA_DIR / "candidate_rules.json"


def safe_str(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def compact_space(text):
    return re.sub(r"\s+", " ", safe_str(text)).strip()


def normalize_quotes(text):
    return (
        safe_str(text)
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def extract_json_messages(text):
    text = normalize_quotes(text)
    if not text:
        return []

    try:
        obj = json.loads(text)
    except Exception:
        return [text]

    messages = []

    def walk(value):
        if isinstance(value, dict):
            for key in ["message", "errorData", "error", "msg", "sql"]:
                if key in value:
                    walk(value[key])
            for v in value.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            if value.strip():
                messages.append(value.strip())

    walk(obj)
    return messages or [text]


def normalize_error_text(text):
    parts = extract_json_messages(text)
    text = " ".join(parts)
    text = normalize_quotes(text)
    text = text.replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    text = compact_space(text)
    return text


def normalize_for_match(text):
    text = normalize_error_text(text).lower()

    replacements = {
        "data can\"t found": "data can't found",
        "data can not found": "data not found",
        "data cannot found": "data not found",
        "resouce can not found": "resource not found",
        "order process is wrong": "order process wrong",
        "order process is stuck": "order process stuck",
        "current case excute over time": "case execute over time",
        "current case execute over time": "case execute over time",
        "index was out of range": "index out of range",
        "找不到对应此选取器的用户界面元素": "ui element not found 找不到对应此选取器的用户界面元素",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    return compact_space(text)


def regex_escape(text):
    return re.escape(safe_str(text))


def shorten_pattern(pattern, limit=240):
    pattern = compact_space(pattern)
    if len(pattern) <= limit:
        return pattern
    return pattern[:limit].rstrip()


def normalize_error_type(value, root_cause=""):
    text = (safe_str(value) + " " + safe_str(root_cause)).lower()

    if any(k in text for k in ["selector", "ui element", "uipath", "自动化", "脚本", "找不到对应"]):
        return "Automation bug"

    if any(k in text for k in ["data", "数据", "资源", "iccid", "bill id", "号码", "not found"]):
        return "Data issue"

    if any(k in text for k in ["crm bug", "veris bug", "system bug", "arrayindexoutofbound", "nullpointer"]):
        return "System bug"

    if any(k in text for k in ["环境", "communication", "server exception", "timeout"]):
        return "Environment issue"

    if any(k in text for k in ["sap", "sff", "stub", "tdc", "external"]):
        return "External system issue"

    if safe_str(value):
        return safe_str(value)

    return "Unknown"


def normalize_root_cause(error_text, raw_root_cause):
    text = normalize_for_match(error_text + " " + raw_root_cause)

    if "soasapinterface" in text and "createdoc" in text:
        return "SAP createDoc returned data not found"

    if "uservertifycode" in text:
        return "Login verification code element not found"

    if "headtable_agrtable" in text or "agreement number" in text:
        return "Agreement page table element not found"

    if "uielement is no longer valid" in text or "ui element is no longer valid" in text or "element is no longer valid" in text:
        return "UI element handle expired or page refreshed"

    if "ui element not found" in text or "selector" in text or "找不到对应此选取器" in text:
        return "UI element location failed"

    if "index out of bounds" in text or "arrayindexoutofboundsexception" in text or "index out of range" in text:
        return "Array index out of bounds"

    if "i_data_index" in text:
        return "Billing i-table not started, or MDB upload failed, or offer data missing"

    if "database validation error" in text and "mem_shortnum" in text:
        return "MEM_SHORTNUM table not created"

    if "database validation error" in text and "insurance" in text:
        return "Insurance order not generated"

    if "order process wrong" in text:
        return "CRM environment abnormal"

    if "order process stuck" in text:
        return "Order workflow delay"

    if "case execute over time" in text or "over time" in text or "timeout" in text:
        return "Case execution timeout"

    if "object reference not set" in text or "nullpointer" in text:
        return "Null pointer exception"

    if "communication with server" in text or "server exception" in text:
        return "Deployment or network exception"

    if "resource not found" in text or "data not found" in text or "data can't found" in text:
        return "Resource does not exist or was not generated"

    if "test data" in text or "data by sql" in text:
        return "Test data not prepared or SQL did not generate data"

    if "bill id" in text:
        return "Insufficient number resources or not generated"

    cleaned = compact_space(raw_root_cause)
    if cleaned:
        return cleaned[:255]

    return "Unknown"


def build_solution(root_cause):
    mapping = {
        "SAP createDoc returned data not found": "Check whether upstream SAP data exists, verify createDoc request parameters, and confirm the SAP stub or service response.",
        "UI element handle expired or page refreshed": "Re-locate the UI element before operating it. Check whether the page refreshed, dialog changed, or the element reference became stale.",
        "Login verification code element not found": "Check whether the login page changed, update the UserVertifyCode selector, and add waiting logic if the element loads slowly.",
        "Agreement page table element not found": "Check whether the Agreement page structure changed, update the HeadTable_agrTable or Agreement Number selector, and confirm the page loaded successfully.",
        "UI element location failed": "Check whether the page structure changed, update automation selectors, and add wait logic if the page loads slowly.",
        "Array index out of bounds": "Check whether the returned list is empty before accessing elements. Add boundary validation and handle empty result scenarios.",
        "Billing i-table not started, or MDB upload failed, or offer data missing": "Check Billing i-table startup, MDB upload status, and whether offer data exists.",
        "MEM_SHORTNUM table not created": "Check whether MEM_SHORTNUM data was generated and whether VPN order data has landed in the table.",
        "Insurance order not generated": "Check whether the insurance order was generated and whether the insurance processing flow completed.",
        "CRM environment abnormal": "Check CRM environment status, database connection, and related service availability.",
        "Order workflow delay": "Check order workflow status and rerun or investigate delayed workflow nodes.",
        "Case execution timeout": "Check execution performance, service response time, and timeout configuration.",
        "Null pointer exception": "Check object initialization and add null checks before accessing object fields.",
        "Deployment or network exception": "Check deployment status, service availability, and network connectivity.",
        "Resource does not exist or was not generated": "Check whether the required resource exists and whether upstream data generation completed.",
        "Test data not prepared or SQL did not generate data": "Prepare test data or check SQL-based data generation.",
        "Insufficient number resources or not generated": "Replenish number resources or check number generation logic.",
    }

    return mapping.get(root_cause, "Further analyze logs or contact the relevant system owner.")


def classify_category(root_cause):
    text = root_cause.lower()

    if any(k in text for k in ["ui element", "uielement", "selector", "verification code", "agreement page"]):
        return "Automation"

    if any(k in text for k in ["data", "resource", "table", "bill", "iccid", "insurance", "mem_shortnum"]):
        return "Data"

    if any(k in text for k in ["sap", "sff", "stub", "external"]):
        return "External System"

    if any(k in text for k in ["network", "deployment", "environment", "timeout", "workflow"]):
        return "Environment"

    if any(k in text for k in ["array", "null pointer", "bug"]):
        return "Code"

    return "Other"


def assign_priority(error_type, root_cause):
    text = (error_type + " " + root_cause).lower()

    if any(k in text for k in ["sap", "network", "deployment", "environment", "i-table"]):
        return 10

    if any(k in text for k in ["timeout", "workflow", "order process"]):
        return 9

    if any(k in text for k in ["ui element", "selector", "array", "null pointer"]):
        return 8

    if any(k in text for k in ["data", "resource", "bill", "insurance", "mem_shortnum"]):
        return 7

    return 5


def extract_match_text(text):
    raw = normalize_error_text(text)

    selectors = []

    for pattern in [
        r"id=['\"]([^'\"]+)['\"]",
        r"aaname=['\"]([^'\"]+)['\"]",
        r"parentid=['\"]([^'\"]+)['\"]",
        r"SoaSapInterFace\(([^)]+)\)",
    ]:
        for match in re.findall(pattern, raw, flags=re.IGNORECASE):
            value = compact_space(match)
            if value and len(value) <= 80:
                selectors.append(value)

    if selectors:
        return selectors[0]

    return ""


def build_pattern_from_text(error_text, root_cause):
    text = normalize_for_match(error_text + " " + root_cause)
    raw = normalize_error_text(error_text + " " + root_cause)

    if "soasapinterface" in text and "createdoc" in text:
        return r"soasapinterface\s*\(\s*createdoc\s*\)|data can'?t found|code['\"]?\s*:\s*404"

    if "uservertifycode" in text:
        return r"uservertifycode|找不到对应此选取器的用户界面元素|ui element not found"

    if "headtable_agrtable" in text or "agreement number" in text:
        return r"headtable_agrtable|agreement number|找不到对应此选取器的用户界面元素|ui element not found"

    if "uielement is no longer valid" in text or "ui element is no longer valid" in text or "element is no longer valid" in text:
        return r"uielement is no longer valid|ui element is no longer valid|element is no longer valid"

    if "ui element not found" in text or "selector" in text or "找不到对应此选取器" in text:
        return r"找不到对应此选取器的用户界面元素|ui element not found|selector"

    if "index out of bounds" in text or "arrayindexoutofboundsexception" in text or "index out of range" in text:
        return r"arrayindexoutofboundsexception|index \d+ out of bounds|index out of bounds|index out of range|array out of bounds"

    if "i_data_index" in text:
        return r"i_data_index"

    if "database validation error" in text:
        return r"database validation error"

    if "order process wrong" in text:
        return r"order process wrong|order process is wrong"

    if "order process stuck" in text:
        return r"order process stuck|order process is stuck"

    if "case execute over time" in text or "over time" in text:
        return r"case execute over time|current case execute over time|current case excute over time|over time"

    if "object reference not set" in text:
        return r"object reference not set"

    if "communication with server" in text:
        return r"communication with server exception|communication with server"

    if "resource not found" in text or "data not found" in text or "data can't found" in text:
        return r"resource not found|data not found|data can'?t found"

    if "bill id" in text:
        return r"bill id"

    if "test data" in text:
        return r"test data|get test data|data by sql"

    message_candidates = extract_json_messages(raw)
    for message in message_candidates:
        message = compact_space(message)
        if 6 <= len(message) <= 120:
            message = re.sub(r"\b\d+\b", r"\\d+", message)
            return shorten_pattern(regex_escape(message).replace(r"\\d\+", r"\d+"))

    return ""


def build_rule_record(error_text, error_type, root_cause):
    pattern = build_pattern_from_text(error_text, root_cause)
    if not pattern:
        return None

    match_text = extract_match_text(error_text)

    return {
        "pattern": shorten_pattern(pattern),
        "match": match_text,
        "match_text": match_text,
        "error_type": error_type,
        "root_cause": root_cause,
        "priority": assign_priority(error_type, root_cause),
        "is_active": True,
        "source": "excel_cleaned",
    }


def build_knowledge_record(error_type, root_cause, confidence="high"):
    return {
        "error_type": error_type,
        "root_cause": root_cause,
        "solution": build_solution(root_cause),
        "category": classify_category(root_cause),
        "confidence": confidence,
        "source": "excel_cleaned",
    }


def add_unique_rule(rules, record):
    if not record:
        return

    key = (
        record["pattern"].lower(),
        safe_str(record.get("match_text") or record.get("match")).lower(),
    )

    existing = rules.get(key)
    if not existing or record["priority"] > existing["priority"]:
        rules[key] = record


def add_unique_knowledge(knowledge, record):
    key = (record["error_type"].lower(), record["root_cause"].lower())
    if key not in knowledge:
        knowledge[key] = record


def load_error_knowledge_base(rules, knowledge):
    df = pd.read_excel(ERROR_KB_XLSX, sheet_name="error_knowledge_base")

    for _, row in df.iterrows():
        error_text = safe_str(row.get("报错信息"))
        raw_type = safe_str(row.get("问题类型"))
        raw_root = safe_str(row.get("失败原因"))

        if not error_text and not raw_root:
            continue

        root_cause = normalize_root_cause(error_text, raw_root)
        error_type = normalize_error_type(raw_type, root_cause)

        rule = build_rule_record(error_text, error_type, root_cause)
        add_unique_rule(rules, rule)

        item = build_knowledge_record(error_type, root_cause, "high")
        add_unique_knowledge(knowledge, item)


def load_cause_mapping(rules, knowledge):
    df = pd.read_excel(CAUSE_MAPPING_XLSX, sheet_name="error_cause_mapping")

    for _, row in df.iterrows():
        raw_root = safe_str(row.get("失败原因"))
        raw_type = safe_str(row.get("报错类型"))

        if not raw_root:
            continue

        root_cause = normalize_root_cause(raw_root, raw_root)
        error_type = normalize_error_type(raw_type, root_cause)

        item = build_knowledge_record(error_type, root_cause, "medium")
        add_unique_knowledge(knowledge, item)

        # error_cause_mapping 没有标准“报错信息”列，但如果失败原因里含技术信号，也可以反向生成规则。
        technical_signals = [
            "SoaSapInterFace",
            "Index 0 out of bounds",
            "ArrayIndexOutOfBoundsException",
            "selector",
            "找不到对应此选取器",
            "database validation error",
            "i_data_index",
            "object reference not set",
        ]

        if any(signal.lower() in raw_root.lower() for signal in technical_signals):
            rule = build_rule_record(raw_root, error_type, root_cause)
            add_unique_rule(rules, rule)


def build_candidate_rules(rules):
    candidates = []

    for record in rules.values():
        candidates.append({
            "pattern": record["pattern"],
            "match_text": record.get("match_text", ""),
            "error_type": record["error_type"],
            "root_cause": record["root_cause"],
            "priority": record["priority"],
        })

    return sorted(candidates, key=lambda x: x["priority"], reverse=True)


def main():
    rules = {}
    knowledge = {}

    load_error_knowledge_base(rules, knowledge)
    load_cause_mapping(rules, knowledge)

    rule_list = sorted(
        rules.values(),
        key=lambda r: (r["priority"], len(r["pattern"])),
        reverse=True,
    )

    knowledge_list = sorted(
        knowledge.values(),
        key=lambda r: (r["error_type"], r["root_cause"]),
    )

    RULES_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(RULES_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(rule_list, f, ensure_ascii=False, indent=2)

    with open(KNOWLEDGE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(knowledge_list, f, ensure_ascii=False, indent=2)

    with open(CANDIDATE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(build_candidate_rules(rules), f, ensure_ascii=False, indent=2)

    print(f"Generated rules: {len(rule_list)} -> {RULES_OUTPUT}")
    print(f"Generated knowledge: {len(knowledge_list)} -> {KNOWLEDGE_OUTPUT}")
    print(f"Generated candidate rules: {len(rule_list)} -> {CANDIDATE_OUTPUT}")


if __name__ == "__main__":
    main()
