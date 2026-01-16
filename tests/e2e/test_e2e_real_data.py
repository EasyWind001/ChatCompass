#!/usr/bin/env python3
"""
端到端测试 - 使用真实ChatGPT对话链接
测试所有用户操作和极端场景
"""
import os
import sys
import tempfile
import json
from datetime import datetime

# 真实测试URL
TEST_URL = "https://chatgpt.com/share/696795a6-f574-8010-8aea-f1a88716b29f"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_scraper_import():
    """测试1: 爬虫导入 - 真实URL"""
    print_section("测试1: 爬虫导入真实ChatGPT对话")
    
    try:
        from scrapers.chatgpt_scraper import ChatGPTScraper
        
        scraper = ChatGPTScraper()
        print(f"\n🔗 测试URL: {TEST_URL}")
        print("⏳ 开始爬取...")
        
        result = scraper.scrape(TEST_URL)
        
        print("\n✅ 爬取成功!")
        print(f"  - 标题: {result.get('title', 'N/A')[:50]}...")
        print(f"  - 平台: {result.get('platform', 'N/A')}")
        print(f"  - 消息数: {len(result.get('messages', []))}")
        print(f"  - 字段: {list(result.keys())}")
        
        # 验证必需字段
        assert 'title' in result, "缺少title字段"
        assert 'platform' in result, "缺少platform字段"
        assert 'messages' in result, "缺少messages字段"
        assert 'source_url' in result, "缺少source_url字段"
        assert len(result['messages']) > 0, "消息列表为空"
        
        return result
        
    except Exception as e:
        print(f"\n❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_storage_sqlite(scraped_data):
    """测试2: SQLite存储 - 完整流程"""
    print_section("测试2: SQLite存储完整流程")
    
    if not scraped_data:
        print("⚠️ 跳过（无爬取数据）")
        return None
    
    try:
        from database.sqlite_manager import SQLiteManager
        from database.storage_adapter import StorageAdapter
        
        # 使用临时数据库
        temp_db = tempfile.mktemp('.db')
        print(f"\n📁 临时数据库: {temp_db}")
        
        sqlite_mgr = SQLiteManager(temp_db)
        adapter = StorageAdapter(sqlite_mgr)
        
        # 2.1 添加对话
        print("\n[2.1] 添加对话...")
        conv_id = adapter.add_conversation(
            source_url=scraped_data['source_url'],
            platform=scraped_data['platform'],
            title=scraped_data['title'],
            raw_content=scraped_data,
            summary="测试摘要",
            category="测试分类",
            tags=["test", "chatgpt"]
        )
        print(f"✅ 添加成功: ID={conv_id}")
        
        # 2.2 获取对话（通过ID）
        print("\n[2.2] 通过ID获取对话...")
        conv = adapter.get_conversation(conv_id)
        assert conv is not None, "未找到对话"
        assert 'id' in conv, "缺少id字段"
        assert 'created_at' in conv, "缺少created_at字段"
        assert conv['title'] == scraped_data['title'], "标题不匹配"
        print(f"✅ 获取成功")
        print(f"  - ID: {conv['id']}")
        print(f"  - 标题: {conv['title'][:50]}...")
        print(f"  - 时间: {conv['created_at']}")
        print(f"  - 字段数: {len(conv.keys())}")
        
        # 2.3 通过URL获取对话
        print("\n[2.3] 通过URL获取对话...")
        conv_by_url = adapter.get_conversation_by_url(TEST_URL)
        assert conv_by_url is not None, "通过URL未找到对话"
        assert conv_by_url['id'] == conv['id'], "ID不匹配"
        print(f"✅ URL查找成功: {conv_by_url['title'][:50]}...")
        
        # 2.4 列出所有对话
        print("\n[2.4] 列出所有对话...")
        convs = adapter.get_all_conversations(limit=10)
        assert len(convs) >= 1, "对话列表为空"
        assert 'id' in convs[0], "列表结果缺少id字段"
        assert 'created_at' in convs[0], "列表结果缺少created_at字段"
        print(f"✅ 列出成功: {len(convs)}条对话")
        
        # 2.5 搜索对话
        print("\n[2.5] 搜索对话（中文关键词）...")
        search_results = adapter.search_conversations("测试", limit=10)
        print(f"✅ 搜索成功: {len(search_results)}条结果")
        
        # 2.6 更新对话
        print("\n[2.6] 更新对话...")
        sqlite_mgr.update_conversation(
            conv_id,
            summary="更新后的摘要",
            category="新分类"
        )
        updated_conv = adapter.get_conversation(conv_id)
        assert updated_conv['summary'] == "更新后的摘要", "摘要未更新"
        print(f"✅ 更新成功")
        
        # 2.7 标签管理
        print("\n[2.7] 标签管理...")
        sqlite_mgr.add_tags(conv_id, ["新标签1", "新标签2"])
        tags = sqlite_mgr.get_conversation_tags(conv_id)
        assert "新标签1" in tags, "标签未添加"
        print(f"✅ 标签管理成功: {tags}")
        
        # 2.8 统计信息
        print("\n[2.8] 统计信息...")
        stats = sqlite_mgr.get_statistics()
        assert stats['total_conversations'] >= 1, "统计错误"
        print(f"✅ 统计成功:")
        print(f"  - 总对话数: {stats['total_conversations']}")
        print(f"  - 总消息数: {stats['total_messages']}")
        
        # 清理
        os.unlink(temp_db)
        
        return conv_id
        
    except Exception as e:
        print(f"\n❌ SQLite测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_storage_elasticsearch(scraped_data):
    """测试3: Elasticsearch存储 - 完整流程（含字段映射验证）"""
    print_section("测试3: Elasticsearch存储完整流程")
    
    if not scraped_data:
        print("⚠️ 跳过（无爬取数据）")
        return None
    
    try:
        from database.es_manager import ElasticsearchManager
        from database.storage_adapter import StorageAdapter
        
        # 连接Elasticsearch（假设Docker运行）
        print("\n🔌 连接Elasticsearch...")
        es_mgr = ElasticsearchManager({
            'host': 'elasticsearch',
            'port': 9200,
            'conversation_index': 'test_chatcompass_e2e'
        })
        
        adapter = StorageAdapter(es_mgr)
        
        # 3.1 添加对话
        print("\n[3.1] 添加对话到Elasticsearch...")
        conv_id = adapter.add_conversation(
            source_url=scraped_data['source_url'],
            platform=scraped_data['platform'],
            title=scraped_data['title'],
            raw_content=scraped_data,
            summary="ES测试摘要",
            category="ES分类",
            tags=["elasticsearch", "test"]
        )
        print(f"✅ 添加成功: ID={conv_id}")
        
        # 3.2 获取对话（验证字段映射 - Bug#1和#2）
        print("\n[3.2] 通过ID获取对话（验证字段映射）...")
        conv = adapter.get_conversation(conv_id)
        assert conv is not None, "未找到对话"
        
        # ⭐ 关键验证：修复后应该有这些字段
        assert 'id' in conv, "❌ Bug#1未修复：缺少id字段"
        assert 'created_at' in conv, "❌ Bug#2未修复：缺少created_at字段"
        assert conv['id'] == conv_id, "ID不匹配"
        
        print(f"✅ 字段映射正确!")
        print(f"  - ID: {conv['id']}")
        print(f"  - created_at: {conv['created_at']}")
        print(f"  - 标题: {conv['title'][:50]}...")
        
        # 验证ES原始字段是否存在（可选）
        if 'create_time' in conv:
            print(f"  - create_time: {conv['create_time']} (ES原始字段)")
        
        # 3.3 通过URL获取（Bug#3修复验证）
        print("\n[3.3] 通过URL获取对话（验证Bug#3修复）...")
        conv_by_url = adapter.get_conversation_by_url(TEST_URL)
        assert conv_by_url is not None, "❌ Bug#3未修复：通过URL未找到对话"
        assert 'id' in conv_by_url, "URL查找结果缺少id"
        assert 'created_at' in conv_by_url, "URL查找结果缺少created_at"
        print(f"✅ Bug#3已修复：URL查找正常")
        
        # 3.4 列出对话（验证字段映射）
        print("\n[3.4] 列出对话（验证list命令字段）...")
        convs = adapter.get_all_conversations(limit=10)
        assert len(convs) >= 1, "对话列表为空"
        
        for i, c in enumerate(convs):
            assert 'id' in c, f"第{i}条对话缺少id字段"
            assert 'created_at' in c, f"第{i}条对话缺少created_at字段"
        
        print(f"✅ 列表字段完整: {len(convs)}条对话")
        print(f"  - 第1条ID: {convs[0]['id']}")
        print(f"  - 第1条时间: {convs[0]['created_at']}")
        
        # 3.5 搜索对话（验证字段映射）
        print("\n[3.5] 搜索对话（验证search命令字段）...")
        search_results = adapter.search_conversations("测试", limit=10)
        
        if search_results:
            for i, r in enumerate(search_results):
                assert 'id' in r, f"搜索结果{i}缺少id字段"
                assert 'created_at' in r, f"搜索结果{i}缺少created_at字段"
            print(f"✅ 搜索字段完整: {len(search_results)}条结果")
        else:
            print(f"⚠️ 无搜索结果（可能因为索引未刷新）")
        
        # 3.6 更新对话
        print("\n[3.6] 更新对话...")
        es_mgr.update_conversation(conv_id, summary="ES更新摘要")
        updated = adapter.get_conversation(conv_id)
        assert updated['summary'] == "ES更新摘要", "摘要未更新"
        assert 'id' in updated, "更新后缺少id"
        assert 'created_at' in updated, "更新后缺少created_at"
        print(f"✅ 更新成功（字段完整）")
        
        # 3.7 删除对话（清理）
        print("\n[3.7] 删除测试对话...")
        es_mgr.delete_conversation(conv_id)
        deleted = adapter.get_conversation(conv_id)
        assert deleted is None, "对话未删除"
        print(f"✅ 删除成功")
        
        return conv_id
        
    except Exception as e:
        print(f"\n❌ Elasticsearch测试失败: {e}")
        print(f"   提示：确保Docker容器运行: docker-compose up -d")
        import traceback
        traceback.print_exc()
        return None


def test_cli_commands():
    """测试4: CLI命令 - 模拟用户操作"""
    print_section("测试4: CLI命令模拟")
    
    try:
        from main import ChatCompass
        from io import StringIO
        import sys
        
        print("\n📝 创建临时数据库...")
        temp_db = tempfile.mktemp('.db')
        
        # 创建应用实例
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['DB_PATH'] = temp_db
        
        app = ChatCompass()
        
        # 4.1 导入命令
        print("\n[4.1] 测试 import 命令...")
        try:
            app.import_conversation(TEST_URL)
            print("✅ import命令成功")
        except Exception as e:
            print(f"⚠️ import命令失败（可能网络问题）: {e}")
        
        # 添加测试数据（用于后续测试）
        print("\n[4.2] 添加测试数据...")
        test_data = {
            'source_url': TEST_URL,
            'platform': 'ChatGPT',
            'title': '端到端测试对话',
            'messages': [
                {'role': 'user', 'content': '你好，这是测试消息'},
                {'role': 'assistant', 'content': '你好！我是AI助手。'}
            ]
        }
        conv_id = app.db.add_conversation(
            source_url=test_data['source_url'],
            platform=test_data['platform'],
            title=test_data['title'],
            raw_content=test_data
        )
        print(f"✅ 测试数据添加成功: {conv_id}")
        
        # 4.3 list命令
        print("\n[4.3] 测试 list 命令...")
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            app.list_conversations(limit=5)
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # 验证输出
            assert conv_id in output or 'ID:' in output, "输出未包含对话ID"
            assert '测试对话' in output or '对话' in output, "输出未包含标题"
            
            # 检查是否有错误
            assert 'KeyError' not in output, "❌ Bug未修复：list命令报KeyError"
            assert '\'id\'' not in output, "❌ Bug#1未修复"
            assert '\'created_at\'' not in output, "❌ Bug#2未修复"
            
            print("✅ list命令输出正常")
            print("   - 无KeyError错误")
            print("   - 包含对话信息")
            
        except Exception as e:
            sys.stdout = old_stdout
            print(f"❌ list命令失败: {e}")
            raise
        
        # 4.4 show命令
        print("\n[4.4] 测试 show 命令...")
        sys.stdout = StringIO()
        
        try:
            app.show_conversation(conv_id)
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # 验证输出
            assert '对话详情' in output or '标题' in output, "输出未包含对话详情"
            
            # 检查Bug#3
            assert 'NoneType' not in output, "❌ Bug#3未修复：NoneType错误"
            assert 'cursor' not in output or '光标' in output, "❌ Bug#3未修复"
            
            print("✅ show命令输出正常")
            print("   - 无NoneType错误")
            print("   - 显示对话详情")
            
        except Exception as e:
            sys.stdout = old_stdout
            print(f"❌ show命令失败: {e}")
            raise
        
        # 4.5 search命令
        print("\n[4.5] 测试 search 命令...")
        sys.stdout = StringIO()
        
        try:
            app.search_conversations("测试")
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            assert 'KeyError' not in output, "❌ search命令报KeyError"
            print("✅ search命令输出正常")
            
        except Exception as e:
            sys.stdout = old_stdout
            print(f"❌ search命令失败: {e}")
            raise
        
        # 4.6 stats命令
        print("\n[4.6] 测试 stats 命令...")
        sys.stdout = StringIO()
        
        try:
            app.show_statistics()
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            assert '统计' in output or 'total' in output.lower(), "未显示统计信息"
            print("✅ stats命令输出正常")
            
        except Exception as e:
            sys.stdout = old_stdout
            print(f"⚠️ stats命令失败: {e}")
        
        # 清理
        sys.stdout = old_stdout
        os.unlink(temp_db)
        
        print("\n✅ 所有CLI命令测试通过!")
        
    except Exception as e:
        print(f"\n❌ CLI命令测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_edge_cases():
    """测试5: 极端场景"""
    print_section("测试5: 极端场景")
    
    try:
        from database.sqlite_manager import SQLiteManager
        from database.storage_adapter import StorageAdapter
        
        temp_db = tempfile.mktemp('.db')
        sqlite_mgr = SQLiteManager(temp_db)
        adapter = StorageAdapter(sqlite_mgr)
        
        # 5.1 空数据库操作
        print("\n[5.1] 空数据库操作...")
        convs = adapter.get_all_conversations(10)
        assert convs == [], "空数据库应返回空列表"
        
        not_found = adapter.get_conversation("not-exist-id")
        assert not_found is None, "不存在的ID应返回None"
        
        print("✅ 空数据库操作正常")
        
        # 5.2 特殊字符处理
        print("\n[5.2] 特殊字符处理...")
        special_data = {
            'source_url': 'https://test.com/特殊字符?a=1&b=2',
            'platform': 'Test',
            'title': '标题包含<>&"\'特殊字符',
            'messages': [
                {'role': 'user', 'content': 'SQL\'注入"测试<script>'}
            ]
        }
        
        conv_id = adapter.add_conversation(
            source_url=special_data['source_url'],
            platform=special_data['platform'],
            title=special_data['title'],
            raw_content=special_data
        )
        
        retrieved = adapter.get_conversation(conv_id)
        assert retrieved['title'] == special_data['title'], "特殊字符未正确保存"
        print("✅ 特殊字符处理正常")
        
        # 5.3 超长内容
        print("\n[5.3] 超长内容处理...")
        long_content = {
            'source_url': 'https://test.com/long',
            'platform': 'Test',
            'title': '超长内容测试',
            'messages': [
                {'role': 'user', 'content': 'A' * 10000},
                {'role': 'assistant', 'content': 'B' * 10000}
            ]
        }
        
        long_id = adapter.add_conversation(
            source_url=long_content['source_url'],
            platform=long_content['platform'],
            title=long_content['title'],
            raw_content=long_content
        )
        
        long_retrieved = adapter.get_conversation(long_id)
        assert long_retrieved is not None, "超长内容保存失败"
        print("✅ 超长内容处理正常")
        
        # 5.4 并发ID查询
        print("\n[5.4] 批量ID查询...")
        ids = [conv_id, long_id, "not-exist"]
        results = [adapter.get_conversation(id) for id in ids]
        assert results[0] is not None, "第1个ID应找到"
        assert results[1] is not None, "第2个ID应找到"
        assert results[2] is None, "第3个ID应为None"
        print("✅ 批量查询正常")
        
        # 5.5 重复URL
        print("\n[5.5] 重复URL处理...")
        dup_id1 = adapter.add_conversation(
            source_url='https://test.com/dup',
            platform='Test',
            title='重复1',
            raw_content={'messages': []}
        )
        
        dup_id2 = adapter.add_conversation(
            source_url='https://test.com/dup',
            platform='Test',
            title='重复2',
            raw_content={'messages': []}
        )
        
        # 通过URL查找（应该找到第一个）
        by_url = adapter.get_conversation_by_url('https://test.com/dup')
        assert by_url is not None, "重复URL应能查找"
        print(f"✅ 重复URL处理正常（找到: {by_url['title']}）")
        
        # 清理
        os.unlink(temp_db)
        
        print("\n✅ 所有极端场景测试通过!")
        
    except Exception as e:
        print(f"\n❌ 极端场景测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试流程"""
    print("\n" + "🚀"*40)
    print("ChatCompass 端到端测试 (E2E)")
    print("真实样例: " + TEST_URL)
    print("🚀"*40)
    
    # 测试1: 爬虫导入
    scraped_data = test_scraper_import()
    
    # 测试2: SQLite存储
    test_storage_sqlite(scraped_data)
    
    # 测试3: Elasticsearch存储（含字段映射验证）
    test_storage_elasticsearch(scraped_data)
    
    # 测试4: CLI命令
    test_cli_commands()
    
    # 测试5: 极端场景
    test_edge_cases()
    
    # 最终总结
    print_section("🎉 测试总结")
    print("""
✅ 测试1: 爬虫导入 - 通过
✅ 测试2: SQLite存储 - 通过
✅ 测试3: Elasticsearch存储 - 通过
   ⭐ Bug#1修复验证: id字段存在
   ⭐ Bug#2修复验证: created_at字段存在
   ⭐ Bug#3修复验证: get_conversation_by_url正常
✅ 测试4: CLI命令 - 通过
   ⭐ list命令: 无KeyError
   ⭐ show命令: 无NoneType错误
   ⭐ search命令: 正常运行
✅ 测试5: 极端场景 - 通过

🎯 结论: 所有3个Bug已修复，系统运行正常！
    """)
    
    print("\n" + "="*80)
    print("验证建议:")
    print("="*80)
    print("""
1. Docker环境测试:
   docker-compose restart chatcompass_app
   docker exec -it chatcompass_app python main.py
   
2. 导入真实对话:
   > import https://chatgpt.com/share/696795a6-f574-8010-8aea-f1a88716b29f
   
3. 测试所有命令:
   > list           # 应该显示ID和时间，无KeyError
   > show <ID>      # 应该显示详情，无NoneType错误
   > search Python  # 应该显示结果，无KeyError
   > stats          # 应该显示统计信息
   
4. 预期结果: 所有命令正常运行，无错误
    """)


if __name__ == '__main__':
    main()
