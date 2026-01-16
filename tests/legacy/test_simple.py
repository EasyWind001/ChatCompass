"""
简单直接测试
"""
import sys
sys.path.insert(0, 'd:/Workspace/ChatCompass')

print("=" * 60)
print("直接测试 ChatCompass")
print("=" * 60)

from database.db_manager import DatabaseManager

# 使用演示数据库
db = DatabaseManager('demo.db')

print("\n[测试1] 列出所有对话")
conversations = db.get_all_conversations(limit=10)
print(f"找到 {len(conversations)} 条对话:\n")
for i, conv in enumerate(conversations, 1):
    print(f"  [{i}] {conv['title']}")
    print(f"      平台: {conv['platform']} | 分类: {conv.get('category', '无')}")
    if conv.get('tags'):
        print(f"      标签: {', '.join(conv['tags'])}")
    print()

print("\n[测试2] 统计信息")
stats = db.get_statistics()
print(f"总对话数: {stats['total_conversations']}")
print(f"总标签数: {stats['total_tags']}")
print("\n按平台:")
for platform, count in stats['by_platform'].items():
    print(f"  {platform}: {count} 条")

print("\n[测试3] 搜索测试（英文）")
results = db.search_conversations('Python', limit=5)
print(f"搜索 'Python': {len(results)} 条结果")
for r in results:
    print(f"  - {r['title']}")

print("\n[测试4] 搜索测试（中文）")
results = db.search_conversations('数据分析', limit=5)
print(f"搜索 '数据分析': {len(results)} 条结果")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)

db.close()
