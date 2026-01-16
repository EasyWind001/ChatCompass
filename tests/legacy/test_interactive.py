"""
自动化测试主程序
"""
import subprocess
import time

print("=" * 60)
print("测试 ChatCompass 主程序")
print("=" * 60)

# 测试1: 查看帮助
print("\n[测试1] 运行主程序并查看统计...")
result = subprocess.run(
    ["python", "main.py", "stats"],
    cwd="d:\\Workspace\\ChatCompass",
    capture_output=True,
    text=True,
    encoding='utf-8'
)

print(result.stdout)
if result.stderr:
    print("错误:", result.stderr)

# 测试2: 搜索（英文）
print("\n[测试2] 搜索 'Python'...")
result = subprocess.run(
    ["python", "main.py", "search", "Python"],
    cwd="d:\\Workspace\\ChatCompass",
    capture_output=True,
    text=True,
    encoding='utf-8'
)

print(result.stdout)
if result.stderr:
    print("错误:", result.stderr)

# 测试3: 列出所有对话
print("\n[测试3] 使用演示数据库测试搜索...")
result = subprocess.run(
    ["python", "-c", """
import sys
sys.path.insert(0, 'd:/Workspace/ChatCompass')
from database.db_manager import DatabaseManager
db = DatabaseManager('demo.db')
conversations = db.get_all_conversations(limit=5)
print(f'\\n找到 {len(conversations)} 条对话:')
for conv in conversations:
    print(f"  - {conv['title']} ({conv['platform']})")
"""],
    cwd="d:\\Workspace\\ChatCompass",
    capture_output=True,
    text=True,
    encoding='utf-8'
)

print(result.stdout)
if result.stderr and "error" in result.stderr.lower():
    print("错误:", result.stderr)

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
