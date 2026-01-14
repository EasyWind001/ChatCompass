"""
ChatCompass 使用示例
演示核心功能的使用方法
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from scrapers.scraper_factory import ScraperFactory
from ai.ollama_client import OllamaClient
from config import DATABASE_PATH


def example_1_add_conversation():
    """示例1：添加对话"""
    print("\n" + "="*60)
    print("示例1：添加对话")
    print("="*60)
    
    db = DatabaseManager(DATABASE_PATH)
    scraper_factory = ScraperFactory()
    
    # 测试URL（实际使用时替换为真实链接）
    test_url = "https://chatgpt.com/share/example-id"
    
    try:
        # 抓取对话
        print(f"抓取链接: {test_url}")
        conversation_data = scraper_factory.scrape(test_url)
        
        # 保存到数据库
        conv_id = db.add_conversation(
            source_url=test_url,
            platform=conversation_data.platform,
            title=conversation_data.title,
            raw_content=conversation_data.to_dict(),
            summary="这是一个示例对话",
            category="其他",
            tags=["示例", "测试"]
        )
        
        print(f"✓ 对话已保存 (ID: {conv_id})")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    finally:
        db.close()


def example_2_ai_analysis():
    """示例2：AI分析对话"""
    print("\n" + "="*60)
    print("示例2：AI分析对话")
    print("="*60)
    
    # 初始化AI客户端
    ai_client = OllamaClient(model="qwen2.5:7b")
    
    # 检查服务
    if not ai_client.is_available():
        print("✗ Ollama服务不可用")
        print("  请确保已启动: ollama serve")
        return
    
    # 测试对话
    test_conversation = """
用户: 如何学习Python？

助手: 学习Python可以按以下步骤：
1. 掌握基础语法
2. 学习常用库（NumPy、Pandas）
3. 做实际项目
4. 阅读优秀代码

用户: 推荐一些学习资源？

助手: 推荐以下资源：
- 官方文档：python.org
- 在线课程：Coursera、Udemy
- 书籍：《Python编程：从入门到实践》
- 练习平台：LeetCode、HackerRank
"""
    
    try:
        print("分析中...")
        result = ai_client.analyze_conversation(test_conversation)
        
        print(f"\n摘要: {result.summary}")
        print(f"分类: {result.category}")
        print(f"标签: {', '.join(result.tags)}")
        print(f"置信度: {result.confidence}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")


def example_3_search():
    """示例3：搜索对话"""
    print("\n" + "="*60)
    print("示例3：搜索对话")
    print("="*60)
    
    db = DatabaseManager(DATABASE_PATH)
    
    # 先添加一些测试数据
    test_data = [
        {
            'url': 'https://test.com/1',
            'platform': 'chatgpt',
            'title': 'Python数据分析教程',
            'content': {'messages': [
                {'role': 'user', 'content': '如何使用Pandas进行数据分析？'},
                {'role': 'assistant', 'content': 'Pandas是Python中强大的数据分析库...'}
            ]},
            'summary': '介绍Pandas数据分析基础',
            'category': '编程',
            'tags': ['Python', 'Pandas', '数据分析']
        },
        {
            'url': 'https://test.com/2',
            'platform': 'claude',
            'title': 'JavaScript异步编程',
            'content': {'messages': [
                {'role': 'user', 'content': '解释Promise和async/await'},
                {'role': 'assistant', 'content': 'Promise是JavaScript中处理异步操作的对象...'}
            ]},
            'summary': '讲解JavaScript异步编程概念',
            'category': '编程',
            'tags': ['JavaScript', '异步编程', 'Promise']
        }
    ]
    
    # 添加测试数据
    for data in test_data:
        try:
            db.add_conversation(
                source_url=data['url'],
                platform=data['platform'],
                title=data['title'],
                raw_content=data['content'],
                summary=data['summary'],
                category=data['category'],
                tags=data['tags']
            )
        except:
            pass  # 忽略重复
    
    # 执行搜索
    keywords = ['Python', 'JavaScript', '数据分析']
    
    for keyword in keywords:
        print(f"\n搜索: {keyword}")
        results = db.search_conversations(keyword, limit=5)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  [{i}] {result['title']}")
                print(f"      {result['snippet'][:100]}...")
        else:
            print("  未找到结果")
    
    db.close()


def example_4_statistics():
    """示例4：统计信息"""
    print("\n" + "="*60)
    print("示例4：统计信息")
    print("="*60)
    
    db = DatabaseManager(DATABASE_PATH)
    
    stats = db.get_statistics()
    
    print(f"\n总对话数: {stats['total_conversations']}")
    
    if stats['by_platform']:
        print("\n按平台统计:")
        for platform, count in stats['by_platform'].items():
            print(f"  {platform}: {count}")
    
    if stats['by_category']:
        print("\n按分类统计:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
    
    print(f"\n总标签数: {stats['total_tags']}")
    
    # 获取热门标签
    tags = db.get_all_tags()
    if tags:
        print("\n热门标签:")
        for tag in tags[:10]:
            print(f"  {tag['name']} ({tag['usage_count']}次)")
    
    db.close()


def example_5_advanced_search():
    """示例5：高级搜索"""
    print("\n" + "="*60)
    print("示例5：高级搜索语法")
    print("="*60)
    
    db = DatabaseManager(DATABASE_PATH)
    
    # 各种搜索语法示例
    search_examples = [
        ('Python', '简单关键词搜索'),
        ('"数据分析"', '短语搜索（精确匹配）'),
        ('Python AND 数据分析', 'AND操作（同时包含）'),
        ('Python OR JavaScript', 'OR操作（包含任一）'),
        ('Python NOT 入门', 'NOT操作（排除）'),
        ('title:教程', '只搜索标题'),
        ('prog*', '前缀搜索'),
    ]
    
    for query, description in search_examples:
        print(f"\n{description}: {query}")
        try:
            results = db.search_conversations(query, limit=3)
            print(f"  找到 {len(results)} 条结果")
        except Exception as e:
            print(f"  错误: {e}")
    
    db.close()


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("ChatCompass 使用示例")
    print("="*60)
    
    examples = [
        # example_1_add_conversation,  # 需要真实URL，跳过
        example_2_ai_analysis,
        example_3_search,
        example_4_statistics,
        example_5_advanced_search,
    ]
    
    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n\n用户中断")
            break
        except Exception as e:
            print(f"\n示例执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("示例演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
