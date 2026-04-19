import os

def export_backend_files():
    # 👉 当前项目根目录（export_files.py 所在位置）
    project_path = os.path.dirname(os.path.abspath(__file__))

    # 👉 backend 路径
    backend_path = os.path.join(project_path, "backend")

    output_file = os.path.join(project_path, "backend_output.txt")

    if not os.path.exists(backend_path):
        print("❌ backend 文件夹不存在！")
        return

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(backend_path):

            # ❗忽略不需要的目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv']]

            for file in files:
                file_path = os.path.join(root, file)

                # ❗避免读到输出文件
                if os.path.abspath(file_path) == os.path.abspath(output_file):
                    continue

                # 👉 相对路径（重点）
                relative_path = os.path.relpath(file_path, project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                except:
                    continue

                outfile.write(f"===== 文件路径: {relative_path} =====\n")
                outfile.write(content)
                outfile.write("\n\n")

    print("✅ backend 导出完成！")


# 直接运行
export_backend_files()