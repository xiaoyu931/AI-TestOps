import pymysql

# ===============================
# 配置
# ===============================
SOURCE_DB = {
    "host": "10.1.248.187",
    "user": "autotest_data",
    "password": "auto1234",
    "database": "autotest_data",
    "charset": "utf8mb4"
}

TARGET_DB = {
    "host": "localhost",
    "user": "root",
    "password": "Yuhongyi850623!",
    "database": "autotest_data",
    "charset": "utf8mb4"
}

FETCH_SIZE = 200   # 每次从源库拉取
MAX_STR_LEN = 20000  # 🔥 超长字段截断（防炸）

TABLE_CONFIG = {
    "test_plan": 6000,
    "batch_detail": 10000,
    "test_case_execution": 20000,
    "test_component_execution": 40000
}

# ===============================
# 工具函数
# ===============================

def safe_row(row):
    """截断超长字段"""
    new_row = []
    for v in row:
        if isinstance(v, str) and len(v) > MAX_STR_LEN:
            new_row.append(v[:MAX_STR_LEN])
        else:
            new_row.append(v)
    return tuple(new_row)


# ===============================
# 连接
# ===============================
source_conn = pymysql.connect(**SOURCE_DB)
target_conn = pymysql.connect(**TARGET_DB)

source_cursor = source_conn.cursor()
target_cursor = target_conn.cursor()

target_cursor.execute("SET FOREIGN_KEY_CHECKS=0")

print("🚀 开始数据迁移...")

# ===============================
# 主逻辑
# ===============================
for table, limit_rows in TABLE_CONFIG.items():

    print(f"\n📦 处理表: {table}")

    try:
        # ---------- 创建表 ----------
        source_cursor.execute(f"SHOW CREATE TABLE `{table}`")
        create_sql = source_cursor.fetchone()[1]

        target_cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        target_cursor.execute(create_sql)
        target_conn.commit()

        # ---------- 获取字段 ----------
        source_cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        columns = [col[0] for col in source_cursor.fetchall()]

        column_str = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))

        insert_sql = f"""
        INSERT INTO `{table}` ({column_str})
        VALUES ({placeholders})
        """

        # ---------- 查询 ----------
        select_sql = f"""
        SELECT {column_str}
        FROM `{table}`
        ORDER BY `create_date` DESC
        LIMIT {limit_rows}
        """

        source_cursor.execute(select_sql)

        total = 0
        fail_count = 0

        while True:
            rows = source_cursor.fetchmany(FETCH_SIZE)
            if not rows:
                break

            for row in rows:
                try:
                    target_conn.ping(reconnect=True)

                    row = safe_row(row)  # 🔥 防止超长字段

                    target_cursor.execute(insert_sql, row)

                    total += 1

                    # 每500条提交一次
                    if total % 500 == 0:
                        target_conn.commit()
                        print(f"➡️ 已写入 {total} 条")

                except Exception as e:
                    fail_count += 1
                    print(f"❌ 跳过异常数据: {e}")
                    continue

        target_conn.commit()

        print(f"✅ 完成: {table} 成功 {total} 条 | 失败 {fail_count} 条")

    except Exception as e:
        print(f"❌ 表失败: {table} -> {e}")
        continue

# ===============================
# 收尾
# ===============================
try:
    target_conn.ping(reconnect=True)
    target_cursor.execute("SET FOREIGN_KEY_CHECKS=1")
except:
    pass

source_cursor.close()
target_cursor.close()
source_conn.close()
target_conn.close()

print("\n🎉 数据迁移完成！")