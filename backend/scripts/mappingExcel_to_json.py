import pandas as pd
import json
import re
from pathlib import Path

INPUT = Path("../data/error_cause_mapping.xlsx")
OUTPUT = Path("../data/error_cause_mapping_cleaned.json")


# ======================
# 工具
# ======================
def safe_str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()


# ======================
# 1️⃣ error_type标准化
# ======================
def normalize_error_type(text):
    t = safe_str(text).lower()

    mapping = {
        "自动化脚本": "自动化BUG",
        "自动化bug": "自动化BUG",
        "脚本问题": "自动化BUG",

        "数据准备": "数据问题",
        "数据问题": "数据问题",

        "veris bug": "系统BUG",
        "vers bug": "系统BUG",

        "crm环境": "环境问题",
        "billing环境": "环境问题",
        "环境": "环境问题",

        "tdc": "外部系统问题",
        "桩": "外部系统问题"
    }

    for k, v in mapping.items():
        if k in t:
            return v

    return safe_str(text)


# ======================
# 2️⃣ 去噪音（强化版）
# ======================
def remove_noise_phrases(text):
    noise_patterns = [
        r"已优化.*",
        r"已修复.*",
        r"问题定位中.*",
        r"未能复现.*",
        r"已换客户.*",
        r"再跑前置.*",
        r"待优化.*",
        r"待修改.*",
        r"已提bug.*",
        r"已解决.*",
        r"优化代码.*",
        r"修改代码.*",
        r"处理中.*",
        r"建议优化.*"
    ]

    for p in noise_patterns:
        text = re.sub(p, "", text)

    return text.strip()


# ======================
# 3️⃣ 基础清洗（加强版）
# ======================
def clean_text(text):
    text = safe_str(text)

    # 去编号
    text = re.sub(r"^\d+[、\.]", "", text)

    # 去括号
    text = re.sub(r"\（.*?\）|\(.*?\)", "", text)

    # 去备注
    text = re.sub(r"--.*", "", text)

    # 去URL
    text = re.sub(r"http[s]?://\S+", "", text)

    # 去SQL
    text = re.sub(r"select .*? from .*?", "", text, flags=re.IGNORECASE)

    # 去大段数字（但保留短数字）
    text = re.sub(r"\b\d{3,}\b", "", text)

    # 清符号
    text = text.replace("\n", " ")
    text = re.sub(r"[\"'{}\[\]]", "", text)

    # 多空格
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ======================
# 4️⃣ root_cause标准化（核心升级）
# ======================
def normalize_root_cause(text):
    text = clean_text(text)
    text = remove_noise_phrases(text)

    t = text.lower()

    rules = [
        # ===== 数据 =====
        (["没有可用", "找不到数据"], "没有可用数据"),
        (["iccid"], "ICCID资源不足"),
        (["bill id", "号码"], "号码资源不足"),
        (["未落表"], "数据未落表"),
        (["未生成"], "数据未生成"),
        (["offer被修改", "offer修改"], "offer配置变更"),

        # ===== 流程 =====
        (["over time", "超时"], "执行超时"),
        (["stuck", "卡住"], "流程卡住"),
        (["延迟", "慢"], "流程执行延迟"),

        # ===== UI =====
        (["ui element", "selector", "找不到对应"], "UI元素定位失败"),

        # ===== SQL =====
        (["database validation error"], "数据库校验失败"),
        (["sql"], "SQL执行异常"),

        # ===== 资源 =====
        (["not found", "can not found"], "资源不存在"),
        (["out of stock"], "库存不足"),

        # ===== 脚本 =====
        (["未初始化", "inparam"], "脚本参数未初始化"),
        (["out of range"], "数组越界"),
        (["object reference"], "空指针异常"),

        # ===== 环境 =====
        (["communication", "server exception"], "服务通信异常"),

        # ===== 地址 =====
        (["validate address"], "地址校验失败"),

        # ===== i表 =====
        (["i_data_index"], "i表处理异常"),

        # ===== 未执行 =====
        (["未执行"], "任务未执行"),
    ]

    for keys, result in rules:
        for k in keys:
            if k in t:
                return result

    # ⭐ fallback（不截断句子，只清理尾巴）
    text = re.sub(r"[，,]\s*$", "", text)

    # 去掉无意义尾巴
    text = re.sub(r"(报错|异常|失败)$", "", text)

    return text.strip()


# ======================
# 5️⃣ solution 自动生成
# ======================
def generate_solution(root_cause):
    mapping = {
        "没有可用数据": "补充测试数据或检查数据准备流程",
        "ICCID资源不足": "补充ICCID资源或检查资源池",
        "号码资源不足": "补充号码资源或检查号码分配",
        "数据未落表": "检查数据入库流程或数据库状态",
        "数据未生成": "检查数据生成逻辑或前置流程",

        "执行超时": "检查流程性能或优化执行时间",
        "流程卡住": "检查流程节点或重跑流程",
        "流程执行延迟": "优化流程执行效率",

        "UI元素定位失败": "检查页面元素或更新自动化定位规则",

        "SQL执行异常": "检查SQL语句或数据库状态",
        "数据库校验失败": "检查数据一致性或校验逻辑",

        "资源不存在": "检查资源是否生成或路径是否正确",
        "库存不足": "补充库存或调整库存配置",

        "脚本参数未初始化": "初始化脚本参数或修复脚本逻辑",
        "数组越界": "检查数组边界或数据长度",
        "空指针异常": "检查对象初始化",

        "服务通信异常": "检查服务接口或网络状态",

        "地址校验失败": "检查地址数据或校验规则",

        "i表处理异常": "检查i表同步或数据处理流程",

        "任务未执行": "检查任务调度或执行状态",
    }

    return mapping.get(root_cause, "需要人工分析具体原因")


# ======================
# 6️⃣ 分类（统一体系）
# ======================
def classify(root_cause):
    if any(k in root_cause for k in ["数据", "资源", "库存"]):
        return "数据类"
    if any(k in root_cause for k in ["流程", "超时"]):
        return "流程类"
    if "UI" in root_cause:
        return "自动化类"
    if any(k in root_cause for k in ["SQL", "数据库"]):
        return "数据库类"
    if any(k in root_cause for k in ["通信", "环境"]):
        return "环境类"
    if "外部" in root_cause:
        return "外部系统类"

    return "其他"


# ======================
# 主流程
# ======================
def main():
    df = pd.read_excel(INPUT)

    result = []
    seen = set()

    for _, row in df.iterrows():
        error_type = normalize_error_type(row.get("报错类型"))
        root_cause = normalize_root_cause(row.get("失败原因"))

        if not error_type or not root_cause:
            continue

        # ⭐只按 root_cause 去重（关键优化）
        key = root_cause.lower()
        if key in seen:
            continue
        seen.add(key)

        solution = generate_solution(root_cause)
        category = classify(root_cause)

        result.append({
            "error_type": error_type,
            "root_cause": root_cause,
            "solution": solution,
            "category": category
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成: {len(result)} 条")
    print(f"📄 输出文件: {OUTPUT}")


if __name__ == "__main__":
    main()