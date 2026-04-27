import os

# 你的 src 路径（根据实际修改）
SRC_DIR = "src"

# 输出文件
OUTPUT_FILE = "output.txt"

# 想要读取的文件类型（可以自己加）
TARGET_EXT = (".js", ".ts", ".tsx", ".jsx", ".css", ".html")

with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(TARGET_EXT):
                file_path = os.path.join(root, file)
                
                outfile.write(f"\n===== {file_path} =====\n")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                        outfile.write("\n")
                except Exception as e:
                    outfile.write(f"[读取失败: {e}]\n")

print("✅ 已导出到 output.txt")