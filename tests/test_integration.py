"""
集成测试 - 测试存储、AI服务和主程序的集成
"""
import pytest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# 修复Windows控制台重定向导致的IO错误
@pytest.fixture(scope="session", autouse=True)
def fix_stdout():
    """修复stdout以避免IO错误"""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    yield
    sys.stdout = original_stdout
    sys.stderr = original_stderr


class TestStorageAdapter:
    """测试存储适配器"""
    
    @pytest.fixture
    def mock_storage(self):
        """创建mock存储"""
        storage = Mock()
        storage.__class__.__name__ = 'MockStorage'
        return storage
    
    @pytest.fixture
    def adapter(self, mock_storage):
        """创建适配器实例"""
        from database.storage_adapter import StorageAdapter
        return StorageAdapter(mock_storage)
    
    def test_add_conversation(self, adapter, mock_storage):
        """测试添加对话"""
        # 准备测试数据
        raw_content = {
            'messages': [
                {'role': 'user', 'content': '你好'},
                {'role': 'assistant', 'content': '你好！有什么可以帮助你的？'}
            ]
        }
        
        mock_storage.add_conversation.return_value = 'test-id-123'
        
        # 调用
        conv_id = adapter.add_conversation(
            source_url='https://test.com/chat/123',
            platform='chatgpt',
            title='测试对话',
            raw_content=raw_content,
            summary='这是测试摘要',
            category='编程',
            tags=['Python', '测试']
        )
        
        # 验证
        assert conv_id == 'test-id-123'
        assert mock_storage.add_conversation.called
        
        # 检查传递的参数
        call_args = mock_storage.add_conversation.call_args[0][0]
        assert call_args['source_url'] == 'https://test.com/chat/123'
        assert call_args['platform'] == 'chatgpt'
        assert call_args['title'] == '测试对话'
        assert call_args['summary'] == '这是测试摘要'
        assert call_args['category'] == '编程'
        assert call_args['tags'] == ['Python', '测试']
        assert call_args['message_count'] == 2
        assert 'word_count' in call_args
    
    def test_get_conversation(self, adapter, mock_storage):
        """测试获取对话"""
        mock_storage.get_conversation.return_value = {
            'id': 'test-id',
            'title': '测试对话'
        }
        
        result = adapter.get_conversation('test-id')
        
        assert result['id'] == 'test-id'
        assert result['title'] == '测试对话'
        mock_storage.get_conversation.assert_called_once_with('test-id')
    
    def test_search_conversations(self, adapter, mock_storage):
        """测试搜索对话"""
        # Mock返回结果
        mock_storage.search_conversations.return_value = [
            {
                'id': '1',
                'title': '测试对话',
                'raw_content': json.dumps({
                    'messages': [
                        {'role': 'user', 'content': '我想学习Python编程'},
                        {'role': 'assistant', 'content': 'Python是一门很好的语言'}
                    ]
                })
            }
        ]
        
        results = adapter.search_conversations('Python', limit=10)
        
        assert len(results) == 1
        assert results[0]['id'] == '1'
        assert 'matches' in results[0]
        
        # 验证匹配上下文
        matches = results[0]['matches']
        assert len(matches) == 2  # 两条消息都包含Python
        assert matches[0]['role'] == 'user'
        assert 'Python' in matches[0]['match_text']
    
    def test_get_statistics(self, adapter, mock_storage):
        """测试获取统计信息"""
        mock_storage.get_statistics.return_value = {
            'total_conversations': 100,
            'by_platform': {'chatgpt': 60, 'claude': 40},
            'by_category': {'编程': 50, '写作': 30},
            'total_tags': 150
        }
        
        stats = adapter.get_statistics()
        
        assert stats['total_conversations'] == 100
        assert stats['by_platform']['chatgpt'] == 60
        assert stats['by_category']['编程'] == 50
        assert stats['total_tags'] == 150


class TestConfigIntegration:
    """测试配置集成"""
    
    def test_get_storage_sqlite(self):
        """测试获取SQLite存储"""
        from config import get_storage
        
        with patch.dict(os.environ, {'STORAGE_TYPE': 'sqlite'}):
            storage = get_storage()
            assert storage is not None
            assert 'SQLite' in storage.__class__.__name__
            storage.close()
    
    def test_get_storage_from_env(self):
        """测试从环境变量获取存储配置"""
        from database.base_storage import StorageFactory
        
        with patch.dict(os.environ, {
            'STORAGE_TYPE': 'sqlite',
            'DATABASE_PATH': '/tmp/test.db'
        }):
            storage = StorageFactory.create()
            assert storage is not None
            storage.close()
    
    def test_get_ai_service(self):
        """测试获取AI服务"""
        from config import get_ai_service
        
        with patch.dict(os.environ, {'AI_MODE': 'local'}):
            service = get_ai_service()
            assert service is not None
            assert hasattr(service, 'analyze_conversation')
            assert hasattr(service, 'generate_summary')


class TestMainIntegration:
    """测试主程序集成"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @patch('config.get_ai_service')
    @patch('config.get_storage')
    def test_chatcompass_init(self, mock_get_storage, mock_get_ai):
        """测试ChatCompass初始化"""
        from main import ChatCompass
        
        # Mock存储
        mock_storage = Mock()
        mock_storage.__class__.__name__ = 'SQLiteManager'
        mock_get_storage.return_value = mock_storage
        
        # Mock AI服务
        mock_ai = Mock()
        mock_ai.is_available.return_value = True
        mock_ai.get_status.return_value = {
            'backend': 'ollama',
            'model': 'qwen2.5:3b'
        }
        mock_get_ai.return_value = mock_ai
        
        # 创建实例
        app = ChatCompass()
        
        assert app.db is not None
        assert app.scraper_factory is not None
        assert app.ai_service is not None
        
        app.close()
    
    @patch('config.get_ai_service')
    @patch('config.get_storage')
    def test_chatcompass_without_ai(self, mock_get_storage, mock_get_ai):
        """测试没有AI服务的ChatCompass"""
        from main import ChatCompass
        
        # Mock存储
        mock_storage = Mock()
        mock_storage.__class__.__name__ = 'SQLiteManager'
        mock_get_storage.return_value = mock_storage
        
        # Mock AI服务不可用
        mock_ai = Mock()
        mock_ai.is_available.return_value = False
        mock_get_ai.return_value = mock_ai
        
        # 创建实例
        app = ChatCompass()
        
        # AI服务应该被设置为None
        assert app.ai_service is None
        
        app.close()
    
    @patch('scrapers.scraper_factory.ScraperFactory.scrape')
    @patch('config.get_ai_service')
    @patch('config.get_storage')
    def test_add_conversation_flow(self, mock_get_storage, mock_get_ai, mock_scrape):
        """测试完整的添加对话流程"""
        from main import ChatCompass
        
        # Mock存储
        mock_storage = Mock()
        mock_storage.__class__.__name__ = 'SQLiteManager'
        mock_storage.add_conversation.return_value = 'conv-123'
        mock_get_storage.return_value = mock_storage
        
        # Mock AI服务
        mock_ai = Mock()
        mock_ai.is_available.return_value = True
        mock_ai.get_status.return_value = {'backend': 'ollama'}
        
        # Mock AI分析结果
        from ai.ollama_client import AIAnalysisResult
        mock_analysis = AIAnalysisResult(
            summary='测试摘要',
            category='编程',
            tags=['Python', '测试']
        )
        mock_ai.analyze_conversation.return_value = mock_analysis
        mock_get_ai.return_value = mock_ai
        
        # Mock爬虫结果
        mock_conversation_data = Mock()
        mock_conversation_data.title = '测试对话'
        mock_conversation_data.platform = 'chatgpt'
        mock_conversation_data.message_count = 5
        mock_conversation_data.word_count = 100
        mock_conversation_data.get_full_text.return_value = '测试对话内容'
        mock_conversation_data.to_dict.return_value = {
            'messages': [{'role': 'user', 'content': '测试'}]
        }
        mock_scrape.return_value = mock_conversation_data
        
        # 创建实例
        app = ChatCompass()
        
        # 调用添加对话
        conv_id = app.add_conversation_from_url('https://test.com/chat')
        
        # 验证
        assert conv_id == 'conv-123'
        mock_scrape.assert_called_once()
        mock_ai.analyze_conversation.assert_called_once()
        mock_storage.add_conversation.assert_called_once()
        
        app.close()


class TestStorageFactoryIntegration:
    """测试存储工厂集成"""
    
    def test_auto_register(self):
        """测试自动注册"""
        from database.base_storage import StorageFactory
        
        types = StorageFactory.get_available_types()
        
        assert 'sqlite' in types
        # elasticsearch可能不可用（未安装包）
    
    def test_create_with_config_dict(self):
        """测试从配置字典创建"""
        from database.base_storage import StorageFactory
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            config = {
                'type': 'sqlite',
                'db_path': db_path
            }
            
            storage = StorageFactory.create_from_config(config)
            assert storage is not None
            
            storage.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestEndToEnd:
    """端到端测试"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_storage_adapter_with_sqlite(self, temp_db):
        """测试存储适配器配合SQLite"""
        from database.sqlite_manager import SQLiteManager
        from database.storage_adapter import StorageAdapter
        
        # 创建存储和适配器
        storage = SQLiteManager(temp_db)
        adapter = StorageAdapter(storage)
        
        # 添加对话
        conv_id = adapter.add_conversation(
            source_url='https://test.com/1',
            platform='chatgpt',
            title='集成测试对话',
            raw_content={
                'messages': [
                    {'role': 'user', 'content': '测试内容'},
                    {'role': 'assistant', 'content': '好的'}
                ]
            },
            summary='测试摘要',
            category='测试',
            tags=['集成测试', 'Python']
        )
        
        assert conv_id is not None
        
        # 获取对话
        conversation = adapter.get_conversation(conv_id)
        assert conversation is not None
        assert conversation['title'] == '集成测试对话'
        assert conversation['platform'] == 'chatgpt'
        
        # 搜索对话
        results = adapter.search_conversations('测试')
        assert len(results) > 0
        
        # 获取统计
        stats = adapter.get_statistics()
        assert stats['total_conversations'] == 1
        
        adapter.close()
    
    def test_ai_service_integration(self):
        """测试AI服务集成"""
        from ai import AIService, AIConfig
        
        # 创建配置（禁用，使用mock）
        config = AIConfig(enabled=False)
        service = AIService(config=config)
        
        # 即使禁用，接口也应该可用（返回None或空结果）
        assert hasattr(service, 'analyze_conversation')
        assert hasattr(service, 'generate_summary')
        assert hasattr(service, 'generate_tags')
        
        # is_available应该返回False
        assert service.is_available() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
