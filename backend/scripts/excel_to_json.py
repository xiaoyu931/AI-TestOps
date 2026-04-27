import json
import re
from pathlib import Path
import pandas as pd
from collections import defaultdict

EXCEL_PATH = Path("../data/error_knowledge_base.xlsx")
RULES_PATH = Path("../data/rules.json")
OUTPUT_PATH = Path("../data/cleaned_error_rules.json")
UNMATCHED_PATH = Path("../data/unmatched.json")
CANDIDATE_PATH = Path("../data/candidate_rules.json")


# ======================
# 工具
# ======================

def safe_str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()


# ======================
# ⭐ 轻清洗（匹配用）
# ======================

def normalize_for_match(text):
    text = safe_str(text).lower()

    # 提取 message
    try:
        obj = json.loads(text)

        # ⭐ 支持 dict + list 混合结构
        if isinstance(obj, dict):
            values = []
            for v in obj.values():
                if isinstance(v, list):
                    values.extend(v)
                elif isinstance(v, str):
                    values.append(v)
            text = " ".join(values)

        elif isinstance(obj, list):
            msgs = []
            for i in obj:
                if isinstance(i, dict):
                    msgs.append(i.get("message", ""))
                elif isinstance(i, str):
                    msgs.append(i)
            text = " ".join(msgs)

    except:
        pass

    text = re.sub(r"\s+", " ", text)

    # ⭐ 关键：轻量语义归一（只做核心）
    replacements = {
        "order process is wrong": "order process wrong",
        "order process is stuck": "order process stuck",
        "current case excute over time": "case execute over time",
        "current case execute over time": "case execute over time",
        "index was out of range": "index out of range",
        "resouce can not found": "resource not found",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()

def extract_core_error(text):
    text = safe_str(text).lower()

    # 提取 message
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            msgs = [i.get("message", "") for i in obj if "message" in i]
            if msgs:
                text = " ".join(msgs)
    except:
        pass

    # 去HTML
    text = re.sub(r"<.*?>", " ", text)

    # 去UI垃圾
    text = re.sub(r"webctrl.*", "", text)
    text = re.sub(r"aaname.*", "", text)
    text = re.sub(r"parentclass.*", "", text)

    # 去多余字段
    text = re.sub(r"errordata", "", text)

    # 保留核心句
    text = re.sub(r"\s+", " ", text)

    return text[:120].strip()

def pre_match_fix(text):
    replacements = {
        "order process is wrong": "order process wrong",
        "order process is stuck": "order process stuck",

        "current case excute over time": "case execute over time",
        "current case execute over time": "case execute over time",

        "resouce can not found": "resource not found",
        "can not found": "not found",

        "index was out of range": "index out of range",

        "errordata case execute over": "case execute over time",

        # ⭐ UI统一
        "找不到对应此选取器的用户界面元素": "ui element not found"
    }

    for k, v in replacements.items():
        if k in text:
            return v

    return text

def clean_candidate_pattern(p):
    p = p.strip()

    # ❌ 去掉这种垃圾
    if p.endswith("can") or p.endswith("get"):
        return None

    if len(p) < 4:
        return None

    return p

def extract_business_signal(text):
    text = text.lower()

    # ⭐ 数据问题
    if "test data" in text or "data by sql" in text:
        return "test data missing"

    # ⭐ 号码资源
    if "bill id" in text:
        return "bill id missing"

    # ⭐ UI
    if "找不到对应此选取器" in text:
        return "ui element not found"

    return None

# ======================
# ⭐ 重清洗（核心优化）
# ======================

def normalize_for_cluster(text):
    text = text.replace("errordata", "")
    text = normalize_for_match(text)

    # 去SQL
    text = re.sub(r"select .*? from .*?", "", text, flags=re.IGNORECASE)

    # 去数字
    text = re.sub(r"\b\d+\b", "", text)

    # 去符号
    text = re.sub(r"[^a-zA-Z\u4e00-\u9fff\s_]", " ", text)

    text = text.lower()

    # ⭐ 强力语义替换（先做）
    replacements = {
        "order process is wrong": "order process wrong",
        "order process is stuck": "order process stuck",
        "current case excute over time": "case execute over time",
        "current case execute over time": "case execute over time",
        "resouce can not found": "resource not found",
        "can not found": "not found",
        "index was out of range": "index out of range",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # ⭐ 强力停用词（关键）
    stopwords = {
        "code", "message", "sql", "from", "where",
        "and", "or", "is", "the", "please", "must",
        "check", "error", "failed", "more", "then", "minutes", "it"
    }

    words = [w for w in text.split() if w not in stopwords]

    text = " ".join(words)

    # ⭐ 统一结构
    text = text.replace("i data index", "i_data_index")

    # # ⭐ 截断（更短更稳定）
    # words = text.split()
    # if len(words) > 4:
    #     text = " ".join(words[:4])

    # ⭐ 不随便截断，而是优先保留关键短语
    priority_phrases = [
        "test data missing",
        "bill id missing",
        "resource not found",
        "data not found",
        "case execute over time",
        "ui element not found"
    ]

    for p in priority_phrases:
        if p in text:
            return p

    # fallback 再截断
    words = text.split()
    if len(words) > 6:
        text = " ".join(words[:6])

    return text.strip()


# ======================
# ⭐ pattern归一
# ======================

def simplify_pattern(text):
    rules = [
        ("insurance user not generated", "insurance user not generated"),
        ("order process wrong", "order process wrong"),
        ("order process stuck", "order process stuck"),
        ("database validation error", "database validation error"),
        ("mem_shortnum", "mem_shortnum"),
        ("ui element", "ui element not found"),
        ("selector", "ui element not found"),
        ("index out of range", "index error"),
        ("send confirm to och", "send confirm to och"),
        ("case execute over time", "case execute over time"),
        ("resource not found", "resource not found"),
        # ===== 新增：数据类 =====
        ("test data", "test data missing"),
        ("get test data", "test data missing"),
        ("data by sql", "test data missing"),

        # ===== 新增：资源类 =====
        ("bill id", "bill id missing"),
        ("enough bill id", "bill id missing"),
        ("找不到对应此选取器的用户界面元素", "ui element not found"),
    ]

    for k, v in rules:
        if k in text:
            return v

    return text


# ======================
# 加载规则
# ======================

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)

    return sorted(
        rules,
        key=lambda r: (1 if r.get("match") else 0, len(r.get("pattern", ""))),
        reverse=True
    )


# ======================
# priority
# ======================

def assign_priority(error_type: str) -> int:
    text = error_type.lower()

    if any(x in text for x in ["系统", "环境", "i表"]):
        return 10
    if any(x in text for x in ["执行", "流程", "超时"]):
        return 9
    if any(x in text for x in ["vpn", "数据库", "校验"]):
        return 8
    if any(x in text for x in ["bug"]):
        return 8
    if any(x in text for x in ["ui", "selector"]):
        return 7
    if "数据准备" in text:
        return 6

    return 5


# ======================
# ⭐ 匹配规则（更稳）
# ======================

def match_rule(text: str, rules: list):
    best_match = None

    for r in rules:
        pattern = safe_str(r.get("pattern")).lower()
        match = safe_str(r.get("match")).lower()

        # ⭐ 优先 match（更精准）
        if match and match in text:
            return r

        if not pattern:
            continue

        if pattern in text:
            if match:
                if match in text:
                    return r
            else:
                if not best_match:
                    best_match = r

    return best_match


# ======================
# 工具函数
# ======================

def is_existing_rule(pattern, rules):
    for r in rules:
        p = safe_str(r.get("pattern")).lower()
        if pattern in p or p in pattern:
            return True
    return False


def is_noise(text):
    noise_keywords = [
        "html", "webctrl", "msedge",
        "aaname", "tag", "parentclass"
    ]

    # ⭐ UI错误直接过滤（因为已经有规则）
    if "ui element not found" in text:
        return True

    return any(k in text for k in noise_keywords)


# ======================
# 主处理
# ======================

def process():
    df = pd.read_excel(EXCEL_PATH, sheet_name="error_knowledge_base")
    rules = load_rules()

    results = []
    unmatched = []

    for _, row in df.iterrows():
        raw_error = safe_str(row.get("报错信息", ""))

        if not raw_error:
            continue

        text = normalize_for_match(raw_error)
        # ⭐ 新增：先提取业务语义（优先级最高）
        signal = extract_business_signal(text)
        if signal:
            text = signal
        text = pre_match_fix(text)
        rule = match_rule(text, rules)

        if rule:
            results.append({
                "pattern": rule.get("pattern"),
                "match": rule.get("match"),
                "error_type": safe_str(rule.get("error_type")),
                "root_cause": safe_str(rule.get("root_cause")),
                "priority": assign_priority(safe_str(rule.get("error_type"))),
                "is_active": True
            })
        else:
            cleaned = normalize_for_cluster(raw_error)

            if cleaned:
                unmatched.append({
                    "raw_error": extract_core_error(raw_error),  # ⭐ 核心改动
                    "cleaned": normalize_for_cluster(raw_error)
                })

    return results, unmatched


# ======================
# 去重
# ======================

def deduplicate(records):
    seen = set()
    result = []

    for r in records:
        key = (r["pattern"], r.get("match"))
        if key not in seen:
            seen.add(key)
            result.append(r)

    return result


def deduplicate_unmatched(records):
    seen = set()
    result = []

    for r in records:
        key = r["cleaned"]
        if key and key not in seen:
            seen.add(key)
            result.append(r)

    return result


# ======================
# 聚类
# ======================

def group_unmatched(records):
    groups = defaultdict(list)

    for r in records:
        clean = r["cleaned"]

        if not clean or len(clean) < 3:
            continue

        if is_noise(clean):
            continue

        pattern = simplify_pattern(clean)

        groups[pattern].append(r["raw_error"])

    return groups


# ======================
# main
# ======================

def main():
    results, unmatched = process()

    results = deduplicate(results)
    unmatched = deduplicate_unmatched(unmatched)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(UNMATCHED_PATH, "w", encoding="utf-8") as f:
        json.dump(unmatched, f, ensure_ascii=False, indent=2)

    print(f"✅ 匹配成功: {len(results)}")
    print(f"⚠️ 未匹配: {len(unmatched)}")

    # 候选规则
    groups = group_unmatched(unmatched)
    rules = load_rules()

    candidate_rules = []

    for k, v in groups.items():
        k = clean_candidate_pattern(k)
        if not k:
            continue
        if is_existing_rule(k, rules):
            continue

        candidate_rules.append({
            "pattern": k,
            "count": len(v),
            "examples": v[:3]
        })

    candidate_rules = sorted(candidate_rules, key=lambda x: x["count"], reverse=True)

    with open(CANDIDATE_PATH, "w", encoding="utf-8") as f:
        json.dump(candidate_rules, f, ensure_ascii=False, indent=2)

    print(f"🧠 候选规则: {len(candidate_rules)}")


if __name__ == "__main__":
    main()