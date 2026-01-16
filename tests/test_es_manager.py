"""
Elasticsearch管理器测试

测试Elasticsearch数据存储和搜索功能。

作者: ChatCompass Team
版本: v1.2.2
"""

import pytest
import os
from datetime import datetime
from database.es_manager import ElasticsearchManager
from elasticsearch.exceptions import ConnectionError as ESConnectionError


# 检查ES是否可用
def is_elasticsearch_available():
    """检查Elasticsearch是否可用"""
    try:
        es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
        
        mgr = ElasticsearchManager(
            host=es_host,
            port=es_port,
            index_prefix='test_chatcompass'
        )
        health = mgr.health_check()
        mgr.close()
        return health['status'] in ['green', 'yellow']
    except:
        return False


# 跳过条件
skip_if_no_es = pytest.mark.skipif(
    not is_elasticsearch_available(),
    reason="Elasticsearch不可用"
)


@pytest.fixture
def es_manager():
    """创建测试用的ES管理器"""
    mgr = ElasticsearchManager(
        host=os.getenv('ELASTICSEARCH_HOST', 'localhost'),
        port=int(os.getenv('ELASTICSEARCH_PORT', '9200')),
        index_prefix='test_chatcompass'
    )
    
    yield mgr
    
    # 清理测试数据
    try:
        mgr.es.indices.delete(index=f"test_chatcompass_*", ignore=[404])
    except:
        pass
    
    mgr.close()


@skip_if_no_es
class TestElasticsearchManager:
    """Elasticsearch管理器测试类"""
    
    def test_connection(self, es_manager):
        """测试连接"""
        health = es_manager.health_check()
        assert health['status'] in ['green', 'yellow', 'red']
        assert 'indices' in health
    
    def test_save_and_get_conversation(self, es_manager):
        """测试保存和获取对话"""
        # 保存对话
        conv_id = "test_conv_001"
        assert es_manager.save_conversation(
            conversation_id=conv_id,
            title="测试对话",
            platform="chatgpt",
            summary="这是一个测试对话"
        )
        
        # 获取对话
        conv = es_manager.get_conversation(conv_id)
        assert conv is not None
        assert conv['conversation_id'] == conv_id
        assert conv['title'] == "测试对话"
        assert conv['platform'] == "chatgpt"
    
    def test_list_conversations(self, es_manager):
        """测试列出对话"""
        # 保存多个对话
        for i in range(5):
            es_manager.save_conversation(
                conversation_id=f"test_conv_{i:03d}",
                title=f"测试对话 {i}",
                platform="chatgpt" if i % 2 == 0 else "claude"
            )
        
        # 列出所有对话
        convs = es_manager.list_conversations(limit=10)
        assert len(convs) >= 5
        
        # 按平台筛选
        chatgpt_convs = es_manager.list_conversations(platform="chatgpt")
        assert all(c['platform'] == 'chatgpt' for c in chatgpt_convs)
    
    def test_update_conversation(self, es_manager):
        """测试更新对话"""
        conv_id = "test_conv_update"
        
        # 创建对话
        es_manager.save_conversation(
            conversation_id=conv_id,
            title="原标题",
            platform="chatgpt"
        )
        
        # 更新对话
        assert es_manager.update_conversation(
            conv_id,
            title="新标题",
            summary="新摘要"
        )
        
        # 验证更新
        conv = es_manager.get_conversation(conv_id)
        assert conv['title'] == "新标题"
        assert conv['summary'] == "新摘要"
    
    def test_delete_conversation(self, es_manager):
        """测试删除对话"""
        conv_id = "test_conv_delete"
        
        # 创建对话
        es_manager.save_conversation(
            conversation_id=conv_id,
            title="待删除对话",
            platform="chatgpt"
        )
        
        # 删除对话
        assert es_manager.delete_conversation(conv_id)
        
        # 验证删除
        conv = es_manager.get_conversation(conv_id)
        assert conv is None
    
    def test_save_and_get_messages(self, es_manager):
        """测试保存和获取消息"""
        conv_id = "test_conv_msg"
        
        # 保存对话
        es_manager.save_conversation(
            conversation_id=conv_id,
            title="消息测试对话",
            platform="chatgpt"
        )
        
        # 保存消息
        messages = [
            {
                'message_id': 'msg_001',
                'conversation_id': conv_id,
                'role': 'user',
                'content': '你好',
                'order_index': 0
            },
            {
                'message_id': 'msg_002',
                'conversation_id': conv_id,
                'role': 'assistant',
                'content': '你好！有什么可以帮你的吗？',
                'order_index': 1
            }
        ]
        
        for msg in messages:
            assert es_manager.save_message(**msg)
        
        # 获取消息
        retrieved_msgs = es_manager.get_messages(conv_id)
        assert len(retrieved_msgs) == 2
        assert retrieved_msgs[0]['role'] == 'user'
        assert retrieved_msgs[1]['role'] == 'assistant'
    
    def test_search_conversations(self, es_manager):
        """测试搜索对话标题"""
        # 创建测试数据
        es_manager.save_conversation(
            conversation_id="search_conv_001",
            title="Python编程入门指南",
            platform="chatgpt",
            summary="这是一个关于Python基础的对话"
        )
        
        es_manager.save_conversation(
            conversation_id="search_conv_002",
            title="JavaScript高级特性",
            platform="chatgpt",
            summary="讨论JavaScript的高级用法"
        )
        
        # 等待索引刷新
        es_manager.es.indices.refresh(index=es_manager.conversation_index)
        
        # 搜索
        results = es_manager.search("Python", search_type="title")
        assert len(results) > 0
        assert any('Python' in r.get('title', '') for r in results)
    
    def test_search_messages(self, es_manager):
        """测试搜索消息内容"""
        conv_id = "search_msg_conv"
        
        # 创建对话和消息
        es_manager.save_conversation(
            conversation_id=conv_id,
            title="技术讨论",
            platform="chatgpt"
        )
        
        es_manager.save_message(
            message_id="msg_search_001",
            conversation_id=conv_id,
            role="user",
            content="如何使用Elasticsearch进行全文搜索？",
            order_index=0
        )
        
        # 等待索引刷新
        es_manager.es.indices.refresh(index=es_manager.message_index)
        
        # 搜索
        results = es_manager.search("Elasticsearch", search_type="content")
        assert len(results) > 0
    
    def test_tags(self, es_manager):
        """测试标签管理"""
        # 保存标签
        assert es_manager.save_tag(
            tag_id="tag_001",
            name="Python",
            color="#3776ab",
            description="Python相关"
        )
        
        # 获取所有标签
        tags = es_manager.get_all_tags()
        assert len(tags) > 0
        assert any(t['name'] == 'Python' for t in tags)
        
        # 删除标签
        assert es_manager.delete_tag("tag_001")
    
    def test_statistics(self, es_manager):
        """测试统计功能"""
        # 创建测试数据
        for i in range(3):
            es_manager.save_conversation(
                conversation_id=f"stat_conv_{i}",
                title=f"对话 {i}",
                platform="chatgpt" if i < 2 else "claude"
            )
        
        # 等待索引刷新
        es_manager.es.indices.refresh(index=es_manager.conversation_index)
        
        # 获取统计
        stats = es_manager.get_statistics()
        assert 'total_conversations' in stats
        assert stats['total_conversations'] >= 3
        assert 'by_platform' in stats
    
    def test_bulk_save_messages(self, es_manager):
        """测试批量保存消息"""
        conv_id = "bulk_msg_conv"
        
        # 创建对话
        es_manager.save_conversation(
            conversation_id=conv_id,
            title="批量消息测试",
            platform="chatgpt"
        )
        
        # 准备批量消息
        messages = [
            {
                'message_id': f'bulk_msg_{i:03d}',
                'conversation_id': conv_id,
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': f'消息内容 {i}',
                'create_time': datetime.now().isoformat(),
                'order_index': i
            }
            for i in range(100)
        ]
        
        # 批量保存
        count = es_manager.bulk_save_messages(messages)
        assert count == 100
        
        # 验证
        retrieved = es_manager.get_messages(conv_id, limit=200)
        assert len(retrieved) == 100


@skip_if_no_es
def test_storage_factory():
    """测试存储工厂"""
    from database.base_storage import StorageFactory
    
    # 测试自动注册
    available_types = StorageFactory.get_available_types()
    assert 'elasticsearch' in available_types
    
    # 测试创建ES实例
    es_mgr = StorageFactory.create('elasticsearch', index_prefix='test_factory')
    assert es_mgr is not None
    assert isinstance(es_mgr, ElasticsearchManager)
    
    es_mgr.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
