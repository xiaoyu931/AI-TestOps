import os
import shutil
import argparse
import time


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--env", default="dev")
    parser.add_argument("--module", default="all")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    os.environ["TEST_ENV"] = args.env
    print(f"🚀 开始执行测试 | browser={args.browser} | env={args.env}")

    start = time.time()
    print("🚀 开始执行测试...")

    # 清理旧数据
    if os.path.exists("reports/allure-results"):
        shutil.rmtree("reports/allure-results")
        print("🧹 清理旧报告")

    os.makedirs("reports/allure-results", exist_ok=True)

    # 🧠 拼接 pytest 命令
    import sys

    cmd = f"pytest --browser=chromium --alluredir=reports/allure-results"

    # 模块控制（先简单版）
    if args.module == "smoke":
        cmd += " -k smoke"

    print(f"👉 执行命令: {cmd}")

    exit_code = os.system(cmd)


    print("📊 生成 Allure 报告...")

    # 自动打开报告
    os.system("allure serve reports/allure-results")

    print("✅ 完成")

    end = time.time()
    print(f"⏱ 总耗时: {end - start:.2f}s")

    if exit_code != 0:
        print("❌ 有用例失败")
    else:
        print("✅ 全部通过")