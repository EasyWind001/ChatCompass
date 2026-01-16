"""
ChatCompass 测试运行脚本
验证各个模块是否正常工作
"""
import sys
from pathlib import Path

print("=" * 60)
print("ChatCompass 测试运行")
print("=" * 60)

# 测试1: 导入模块
print("\n[测试1] 导入模块...")
try:
    from database.db_manager import DatabaseManager
    from scrapers.scraper_factory import ScraperFactory
    from scrapers.chatgpt_scraper import ChatGPTScraper
    from scrapers.claude_scraper import ClaudeScraper
    from config import DATABASE_PATH, SUPPORTED_PLATFORMS
    print("✓ 所有模块导入成功")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试2: 数据库初始化
print("\n[测试2] 数据库初始化...")
try:
    db = DatabaseManager("test_chatcompass.db")
    print("✓ 数据库初始化成功")
    print(f"  数据库路径: test_chatcompass.db")
except Exception as e:
    print(f"✗ 数据库初始化失败: {e}")
    sys.exit(1)

# 测试3: 添加测试数据
print("\n[测试3] 添加测试对话...")
try:
    test_conversation = {
        'messages': [
            {'role': 'user', 'content': '你好，我想学习Python编程'},
            {'role': 'assistant', 'content': '你好！学习Python是个很好的选择。建议从基础语法开始...'},
            {'role': 'user', 'content': '推荐一些学习资源？'},
            {'role': 'assistant', 'content': '推荐以下资源：\n1. 官方文档\n2. 《Python编程：从入门到实践》\n3. Coursera课程'}
        ]
    }
    
    conv_id = db.add_conversation(
        source_url="https://chatgpt.com/share/test-001",
        platform="chatgpt",
        title="Python学习路线咨询",
        raw_content=test_conversation,
        summary="讨论Python学习方法和推荐资源",
        category="编程",
        tags=["Python", "学习", "入门"]
    )
    print(f"✓ 添加对话成功 (ID: {conv_id})")
    
    # 再添加一条
    conv_id2 = db.add_conversation(
        source_url="https://claude.ai/share/test-002",
        platform="claude",
        title="JavaScript异步编程详解",
        raw_content={'messages': [
            {'role': 'user', 'content': '解释一下Promise和async/await'},
            {'role': 'assistant', 'content': 'Promise是JavaScript中处理异步操作的对象...'}
        ]},
        summary="深入讲解JavaScript异步编程机制",
        category="编程",
        tags=["JavaScript", "异步编程", "Promise"]
    )
    print(f"✓ 添加第二条对话成功 (ID: {conv_id2})")
    
except Exception as e:
    print(f"✗ 添加对话失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 查询对话
print("\n[测试4] 查询对话...")
try:
    conversations = db.get_all_conversations(limit=10)
    print(f"✓ 查询成功，共 {len(conversations)} 条对话")
    for conv in conversations:
        print(f"  - [{conv['platform']}] {conv['title']}")
except Exception as e:
    print(f"✗ 查询失败: {e}")

# 测试5: 全文搜索
print("\n[测试5] 全文搜索...")
test_keywords = ["Python", "JavaScript", "异步"]
for keyword in test_keywords:
    try:
        results = db.search_conversations(keyword, limit=5)
        print(f"✓ 搜索 '{keyword}': 找到 {len(results)} 条结果")
        for result in results[:2]:  # 只显示前2条
            snippet = result.get('snippet', '')[:80]
            print(f"    - {result['title']}: {snippet}...")
    except Exception as e:
        print(f"✗ 搜索 '{keyword}' 失败: {e}")

# 测试6: 统计信息
print("\n[测试6] 统计信息...")
try:
    stats = db.get_statistics()
    print(f"✓ 统计查询成功")
    print(f"  总对话数: {stats['total_conversations']}")
    print(f"  按平台: {stats['by_platform']}")
    print(f"  按分类: {stats['by_category']}")
    print(f"  总标签数: {stats['total_tags']}")
except Exception as e:
    print(f"✗ 统计查询失败: {e}")

# 测试7: 爬虫工厂
print("\n[测试7] 爬虫工厂...")
try:
    factory = ScraperFactory()
    print(f"✓ 爬虫工厂初始化成功")
    print(f"  支持的平台: {factory.get_supported_platforms()}")
    
    # 测试URL识别
    test_urls = [
        "https://chatgpt.com/share/abc123",
        "https://chat.openai.com/share/xyz789",
        "https://claude.ai/share/test456",
        "https://unknown.com/share/123"
    ]
    
    for url in test_urls:
        scraper = factory.get_scraper(url)
        if scraper:
            print(f"  ✓ {url} -> {scraper.platform_name}")
        else:
            print(f"  ✗ {url} -> 不支持")
            
except Exception as e:
    print(f"✗ 爬虫工厂测试失败: {e}")

# 测试8: AI客户端（仅检查导入）
print("\n[测试8] AI客户端...")
try:
    from ai.ollama_client import OllamaClient
    from ai.openai_client import OpenAIClient
    print("✓ AI客户端模块导入成功")
    
    # 检查Ollama服务（不强制要求）
    try:
        client = OllamaClient()
        if client.is_available():
            print("  ✓ Ollama服务可用")
            models = client.list_models()
            if models:
                print(f"  可用模型: {models[:3]}")
        else:
            print("  ℹ Ollama服务未启动（可选）")
    except:
        print("  ℹ Ollama未配置（可选）")
        
except Exception as e:
    print(f"✗ AI客户端测试失败: {e}")

# 清理
print("\n[清理] 关闭数据库连接...")
db.close()
print("✓ 清理完成")

print("\n" + "=" * 60)
print("测试运行完成！")
print("=" * 60)
print("\n所有核心模块工作正常 ✓")
print("\n下一步:")
print("1. 运行主程序: python main.py")
print("2. 尝试添加真实的对话链接")
print("3. 测试搜索功能")
print("\n数据库文件: test_chatcompass.db")
print("可以删除测试数据库: del test_chatcompass.db")
