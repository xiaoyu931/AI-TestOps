import json
import pymysql
from pathlib import Path

# ======================
# 文件路径
# ======================
RULES_FILE = Path("../data/cleaned_error_rules.json")
KNOWLEDGE_FILE = Path("../data/error_cause_mapping_cleaned.json")

# ======================
# 数据库配置（自己改）
# ======================
DB_CONFIG =  {
    "host": "localhost",
    "user": "root",
    "password": "Yuhongyi850623!",
    "database": "autotest_data",
    "charset": "utf8mb4"
}


# ======================
# 连接数据库
# ======================
def get_conn():
    return pymysql.connect(**DB_CONFIG)


# ======================
# 插入 rules 表
# ======================
def insert_rules(conn):
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()

    sql = """
    INSERT INTO error_rules 
    (pattern, match_text, error_type, root_cause, priority, is_active, source)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    error_type = VALUES(error_type),
    root_cause = VALUES(root_cause),
    priority = VALUES(priority),
    is_active = VALUES(is_active),
    source = VALUES(source)
    """

    for r in data:
        cursor.execute(sql, (
            r.get("pattern"),
            r.get("match") or "",
            r.get("error_type"),
            r.get("root_cause"),
            r.get("priority"),
            r.get("is_active"),
            "rules_json"
        ))

    conn.commit()
    print(f"✅ 插入 rules: {len(data)} 条")


# ======================
# 插入 knowledge 表
# ======================
def insert_knowledge(conn):
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()

    sql = """
    INSERT INTO error_knowledge 
    (error_type, root_cause, solution, category, confidence, source)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    solution = VALUES(solution),
    category = VALUES(category),
    confidence = VALUES(confidence),
    source = VALUES(source)
    """

    for r in data:
        cursor.execute(sql, (
            r.get("error_type"),
            r.get("root_cause"),
            r.get("solution"),
            r.get("category"),
            r.get("confidence"),
            "mapping_json"
        ))

    conn.commit()
    print(f"✅ 插入 knowledge: {len(data)} 条")


# ======================
# 主函数
# ======================
def main():
    conn = get_conn()

    try:
        insert_rules(conn)
        insert_knowledge(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()