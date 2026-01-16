"""
完整功能测试脚本
"""
import sys
import os
sys.path.insert(0, 'd:/Workspace/ChatCompass')

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

from database.db_manager import DatabaseManager
from scrapers.scraper_factory import ScraperFactory

print("=" * 60)
print("ChatCompass 完整功能测试")
print("=" * 60)

# 使用演示数据库
db = DatabaseManager('demo.db')
factory = ScraperFactory()

# 测试1: 列出对话
print("\n[测试1] 列出所有对话")
print("-" * 60)
conversations = db.get_all_conversations(limit=10)
print(f"找到 {len(conversations)} 条对话:\n")
for i, conv in enumerate(conversations, 1):
    print(f"{i}. {conv['title']}")
    print(f"   平台: {conv['platform']} | 分类: {conv.get('category', '无')}")
    if conv.get('tags'):
        print(f"   标签: {', '.join(conv['tags'])}")
    print()

# 测试2: 搜索功能
print("\n[测试2] 搜索功能测试")
print("-" * 60)
test_keywords = ['Python', 'JavaScript', '数据分析', 'async', '技术博客']
for keyword in test_keywords:
    results = db.search_conversations(keyword, limit=3)
    print(f"搜索 '{keyword}': {len(results)} 条结果")
    for r in results[:1]:  # 只显示第一条
        print(f"  -> {r['title']}")

# 测试3: 统计信息
print("\n[测试3] 统计信息")
print("-" * 60)
stats = db.get_statistics()
print(f"总对话数: {stats['total_conversations']}")
print(f"总标签数: {stats['total_tags']}")
print("\n按平台统计:")
for platform, count in stats['by_platform'].items():
    print(f"  {platform}: {count} 条")
print("\n按分类统计:")
for category, count in stats['by_category'].items():
    print(f"  {category}: {count} 条")

# 测试4: 标签系统
print("\n[测试4] 标签系统")
print("-" * 60)
tags = db.get_all_tags()
hot_tags = sorted(tags, key=lambda x: x['usage_count'], reverse=True)[:10]
print("热门标签:")
for tag in hot_tags:
    if tag['usage_count'] > 0:
        print(f"  {tag['name']} (使用 {tag['usage_count']} 次)")

# 测试5: 爬虫工厂
print("\n[测试5] 爬虫工厂 URL识别")
print("-" * 60)
test_urls = [
    'https://chatgpt.com/share/abc123',
    'https://claude.ai/share/xyz789',
    'https://chat.openai.com/share/test',
    'https://gemini.google.com/share/456'
]
print(f"支持的平台: {', '.join(factory.get_supported_platforms())}\n")
for url in test_urls:
    scraper = factory.get_scraper(url)
    if scraper:
        print(f"[OK] {url}")
        print(f"     -> 平台: {scraper.platform_name}")
    else:
        print(f"[NO] {url}")
        print(f"     -> 不支持")

# 测试6: 详细查询
print("\n[测试6] 查询对话详情")
print("-" * 60)
conv = db.get_conversation_by_id(1)
if conv:
    print(f"标题: {conv['title']}")
    print(f"平台: {conv['platform']}")
    print(f"分类: {conv.get('category', '无')}")
    print(f"摘要: {conv.get('summary', '无')[:100]}...")
    print(f"标签: {', '.join(conv.get('tags', []))}")
    print(f"创建时间: {conv['created_at']}")

db.close()

print("\n" + "=" * 60)
print("所有测试完成！✓")
print("=" * 60)
print("\n提示: 使用以下命令体验交互模式:")
print("  python main.py")
print("\n或使用命令行模式:")
print("  python main.py stats")
print("  python main.py search Python")
print("  python main.py search 数据分析")
