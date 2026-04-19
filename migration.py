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

BATCH_SIZE = 50
LIMIT_ROWS = 5000

# ===============================
# 连接
# ===============================
source_conn = pymysql.connect(**SOURCE_DB)
target_conn = pymysql.connect(**TARGET_DB)

source_cursor = source_conn.cursor(pymysql.cursors.SSCursor)
target_cursor = target_conn.cursor()

# ===============================
# 获取所有表
# ===============================
source_cursor.execute("SHOW TABLES")
source_tables = [row[0] for row in source_cursor.fetchall()]

target_cursor.execute("SHOW TABLES")
target_tables = [row[0] for row in target_cursor.fetchall()]

print(f"源表数量: {len(source_tables)}")
print(f"已存在表: {len(target_tables)}")

# ===============================
# 关闭外键
# ===============================
target_cursor.execute("SET FOREIGN_KEY_CHECKS=0")

# ===============================
# 开始同步
# ===============================
for table in source_tables:

    # ✅ 跳过已经同步过的表
    if table in target_tables:
        print(f"⏭️ 已存在，跳过: {table}")
        continue

    print(f"\n🚀 开始同步表: {table}")

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

        # ---------- 限制数据量（关键🔥） ----------
        source_cursor.execute(
            f"SELECT {column_str} FROM `{table}` LIMIT {LIMIT_ROWS}"
        )

        total = 0

        # ---------- 分批 ----------
        while True:
            rows = source_cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break

            insert_sql = f"""
            INSERT INTO `{table}` ({column_str})
            VALUES ({placeholders})
            """

            target_cursor.executemany(insert_sql, rows)
            target_conn.commit()

            total += len(rows)

        print(f"✅ {table} 完成，共 {total} 条")

    except Exception as e:
        print(f"❌ {table} 失败: {e}")
        continue

# ===============================
# 恢复外键
# ===============================
target_cursor.execute("SET FOREIGN_KEY_CHECKS=1")

# ===============================
# 关闭连接
# ===============================
source_cursor.close()
target_cursor.close()
source_conn.close()
target_conn.close()

print("\n🎉 剩余表同步完成！")