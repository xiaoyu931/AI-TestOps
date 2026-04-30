import allure
import os
import time
import re


class AssertUtils:

    @staticmethod
    def get_test_name():
        current_test = os.getenv("PYTEST_CURRENT_TEST", "unknown_test")

        # test_open_testops_home[chromium]
        name_part = current_test.split("::")[-1].split(" ")[0]

        # 拆分参数
        if "[" in name_part:
            base, param = name_part.split("[")
            param = param.rstrip("]")
            return f"{base}_{param}"

        return name_part

    @staticmethod
    def format_message_for_filename(message: str) -> str:
        # 1️⃣ 转小写
        msg = message.lower()

        # 2️⃣ 中文 → 英文（简单映射，可扩展）
        replace_map = {
            "首页": "home",
            "加载": "load",
            "失败": "failed",
            "成功": "success",
            "未出现": "not_found",
            "logo": "logo"
        }

        for k, v in replace_map.items():
            msg = msg.replace(k, v)

        # 3️⃣ 去掉特殊符号
        msg = re.sub(r'[^\w\s]', '', msg)

        # 4️⃣ 空格 → 下划线
        msg = msg.replace(" ", "_")

        # 5️⃣ 压缩多余下划线
        msg = re.sub(r'_+', '_', msg)

        return msg.strip("_")

    @staticmethod
    def assert_true(result, page=None):
        if result.success:
            print(f"[ASSERT PASS] {result.message}")
        else:
            print(f"[ASSERT FAIL] {result.message}")

            if page:
                test_name = AssertUtils.get_test_name()
                timestamp = int(time.time())

                msg_part = AssertUtils.format_message_for_filename(result.message)
                screenshot_path = f"reports/screenshots/{test_name}/fail_{msg_part}_{timestamp}.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

                print(f"开始截图: {screenshot_path}")
                page.screenshot(path=screenshot_path)

                allure.attach.file(
                    screenshot_path,
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )

        assert result.success, result.message