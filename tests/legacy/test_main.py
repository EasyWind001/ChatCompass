"""测试主程序功能"""
import sys
sys.path.insert(0, '.')

from database.db_manager import DatabaseManager

print("测试主程序功能\n")

# 创建数据库
db = DatabaseManager("test_main.db")

# 添加测试数据
print("添加测试数据...")
conv_id = db.add_conversation(
    source_url="https://chatgpt.com/share/test",
    platform="chatgpt",
    title="Python编程入门",
    raw_content={'messages': [
        {'role': 'user', 'content': 'Python如何入门？'},
        {'role': 'assistant', 'content': '学习Python可以从基础语法开始，推荐使用官方教程...'}
    ]},
    summary="讨论Python学习方法",
    category="编程",
    tags=["Python", "编程", "入门"]
)

print(f"添加成功 ID: {conv_id}")

# 搜索测试
print("\n搜索测试...")
results = db.search_conversations("Python", limit=10)
print(f"搜索'Python': 找到 {len(results)} 条结果")

if results:
    for r in results:
        print(f"  - {r['title']}")
        if 'snippet' in r:
            print(f"    {r['snippet'][:100]}...")

# 统计
print("\n统计信息...")
stats = db.get_statistics()
print(f"总对话数: {stats['total_conversations']}")
print(f"按平台: {stats['by_platform']}")

db.close()
print("\n测试完成!")
