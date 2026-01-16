"""
AI服务测试

测试AI服务的各项功能，包括Ollama客户端和AI服务管理器。

作者: ChatCompass Team
版本: v1.2.2
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from ai.ollama_client import OllamaClient, AIAnalysisResult
from ai.ai_service import AIService, AIConfig, get_ai_service, reset_ai_service


# ==================== 辅助函数 ====================

def is_ollama_available():
    """检查Ollama是否可用"""
    try:
        import requests
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


# 跳过条件
skip_if_no_ollama = pytest.mark.skipif(
    not is_ollama_available(),
    reason="Ollama服务不可用"
)


# ==================== Fixtures ====================

@pytest.fixture
def ai_config():
    """创建测试用的AI配置"""
    return AIConfig(
        enabled=True,
        backend='ollama',
        ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
        ollama_model=os.getenv('OLLAMA_MODEL', 'qwen2.5:3b'),
        timeout=60,
        auto_analyze=False
    )


@pytest.fixture
def mock_ollama_client():
    """创建模拟的Ollama客户端"""
    client = Mock(spec=OllamaClient)
    client.is_available.return_value = True
    client.list_models.return_value = ['qwen2.5:3b', 'llama3.2']
    client.model = 'qwen2.5:3b'
    
    # 模拟分析结果
    client.analyze_conversation.return_value = AIAnalysisResult(
        summary="这是一个关于Python编程的对话。",
        category="编程",
        tags=["Python", "编程", "学习"],
        confidence=0.9
    )
    
    client.generate_summary_only.return_value = "简短的摘要"
    client.generate_tags_only.return_value = ["标签1", "标签2", "标签3"]
    
    return client


@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前重置单例"""
    reset_ai_service()
    yield
    reset_ai_service()


# ==================== OllamaClient测试 ====================

class TestOllamaClient:
    """测试Ollama客户端"""
    
    def test_init_from_env(self):
        """测试从环境变量初始化"""
        # 设置环境变量
        os.environ['OLLAMA_HOST'] = 'http://test-host:11434'
        os.environ['OLLAMA_MODEL'] = 'test-model'
        
        client = OllamaClient()
        
        assert client.base_url == 'http://test-host:11434'
        assert client.model == 'test-model'
        
        # 清理
        del os.environ['OLLAMA_HOST']
        del os.environ['OLLAMA_MODEL']
    
    def test_init_with_params(self):
        """测试使用参数初始化"""
        client = OllamaClient(
            base_url='http://custom-host:11434',
            model='custom-model',
            timeout=30
        )
        
        assert client.base_url == 'http://custom-host:11434'
        assert client.model == 'custom-model'
        assert client.timeout == 30
    
    @skip_if_no_ollama
    def test_is_available(self):
        """测试服务可用性检查"""
        client = OllamaClient()
        assert client.is_available() is True
    
    @skip_if_no_ollama
    def test_list_models(self):
        """测试列出模型"""
        client = OllamaClient()
        models = client.list_models()
        
        assert isinstance(models, list)
        # 如果Ollama正在运行，应该有模型
        if models:
            assert all(isinstance(m, str) for m in models)
    
    @patch('requests.post')
    def test_generate(self, mock_post):
        """测试文本生成"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '这是生成的文本'
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("测试提示词")
        
        assert result == '这是生成的文本'
        assert mock_post.called
    
    @patch('requests.post')
    def test_generate_timeout(self, mock_post):
        """测试超时处理"""
        import requests
        mock_post.side_effect = requests.Timeout()
        
        client = OllamaClient(timeout=1)
        
        with pytest.raises(TimeoutError):
            client.generate("测试提示词")
    
    def test_parse_analysis_result_success(self):
        """测试成功解析JSON结果"""
        client = OllamaClient()
        
        json_response = '''
        {
            "summary": "这是摘要",
            "category": "编程",
            "tags": ["Python", "数据分析"]
        }
        '''
        
        result = client._parse_analysis_result(json_response)
        
        assert result.summary == "这是摘要"
        assert result.category == "编程"
        assert result.tags == ["Python", "数据分析"]
    
    def test_parse_analysis_result_with_markdown(self):
        """测试解析带markdown标记的JSON"""
        client = OllamaClient()
        
        markdown_response = '''
        ```json
        {
            "summary": "这是摘要",
            "category": "编程",
            "tags": ["Python"]
        }
        ```
        '''
        
        result = client._parse_analysis_result(markdown_response)
        
        assert result.summary == "这是摘要"
        assert result.category == "编程"
    
    def test_parse_analysis_result_fallback(self):
        """测试备用解析"""
        client = OllamaClient()
        
        # 无效的JSON
        invalid_response = '这是一段普通文本，不是JSON'
        
        result = client._parse_analysis_result(invalid_response)
        
        # 应该返回结果，但置信度降低
        assert isinstance(result, AIAnalysisResult)
        assert result.confidence == 0.5


# ==================== AIConfig测试 ====================

class TestAIConfig:
    """测试AI配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = AIConfig()
        
        assert config.enabled is True
        assert config.backend == 'ollama'
        assert config.timeout == 60
    
    def test_from_env(self):
        """测试从环境变量创建"""
        # 设置环境变量
        os.environ['AI_ENABLED'] = 'false'
        os.environ['AI_BACKEND'] = 'openai'
        os.environ['OLLAMA_MODEL'] = 'test-model'
        
        config = AIConfig.from_env()
        
        assert config.enabled is False
        assert config.backend == 'openai'
        assert config.ollama_model == 'test-model'
        
        # 清理
        del os.environ['AI_ENABLED']
        del os.environ['AI_BACKEND']
        del os.environ['OLLAMA_MODEL']


# ==================== AIService测试 ====================

class TestAIService:
    """测试AI服务"""
    
    def test_init_with_config(self, ai_config):
        """测试使用配置初始化"""
        service = AIService(config=ai_config)
        
        assert service.config == ai_config
        assert service.config.enabled is True
    
    def test_init_disabled(self):
        """测试禁用AI服务"""
        config = AIConfig(enabled=False)
        service = AIService(config=config)
        
        assert service.client is None
    
    @skip_if_no_ollama
    def test_is_available(self, ai_config):
        """测试服务可用性"""
        service = AIService(config=ai_config)
        
        # 如果Ollama正在运行，应该可用
        available = service.is_available()
        assert isinstance(available, bool)
    
    @skip_if_no_ollama
    def test_get_status(self, ai_config):
        """测试获取状态"""
        service = AIService(config=ai_config)
        status = service.get_status()
        
        assert 'enabled' in status
        assert 'backend' in status
        assert 'available' in status
        assert 'model' in status
        assert status['backend'] == 'ollama'
    
    def test_analyze_conversation_success(self, ai_config, mock_ollama_client):
        """测试成功分析对话"""
        # 直接创建service并设置mock client
        service = AIService(config=ai_config)
        service.client = mock_ollama_client
        
        test_text = "用户: 你好\n助手: 你好！"
        result = service.analyze_conversation(test_text, "测试对话")
        
        assert result is not None
        assert result.summary == "这是一个关于Python编程的对话。"
        assert result.category == "编程"
        assert "Python" in result.tags
    
    def test_analyze_conversation_disabled(self):
        """测试禁用状态下的分析"""
        config = AIConfig(enabled=False)
        service = AIService(config=config)
        
        result = service.analyze_conversation("测试文本")
        assert result is None
    
    def test_generate_summary(self, ai_config, mock_ollama_client):
        """测试生成摘要"""
        service = AIService(config=ai_config)
        service.client = mock_ollama_client
        
        summary = service.generate_summary("测试对话内容")
        
        assert summary == "简短的摘要"
    
    def test_generate_tags(self, ai_config, mock_ollama_client):
        """测试生成标签"""
        service = AIService(config=ai_config)
        service.client = mock_ollama_client
        
        tags = service.generate_tags("测试对话内容")
        
        assert tags == ["标签1", "标签2", "标签3"]
    
    def test_batch_analyze(self, ai_config, mock_ollama_client):
        """测试批量分析"""
        service = AIService(config=ai_config)
        service.client = mock_ollama_client
        
        conversations = [
            {'text': '对话1', 'title': '标题1'},
            {'text': '对话2', 'title': '标题2'},
            {'text': '对话3'}
        ]
        
        # 测试进度回调
        progress_calls = []
        def callback(current, total):
            progress_calls.append((current, total))
        
        results = service.batch_analyze(conversations, callback=callback)
        
        assert len(results) == 3
        assert all(r is not None and isinstance(r, AIAnalysisResult) for r in results)
        assert progress_calls == [(1, 3), (2, 3), (3, 3)]
    
    def test_test_connection_success(self, ai_config, mock_ollama_client):
        """测试连接测试成功"""
        service = AIService(config=ai_config)
        service.client = mock_ollama_client
        
        result = service.test_connection()
        
        assert result['success'] is True
        assert result['backend'] == 'ollama'
        assert result['test_response'] is not None
    
    def test_test_connection_disabled(self):
        """测试禁用状态的连接测试"""
        config = AIConfig(enabled=False)
        service = AIService(config=config)
        
        result = service.test_connection()
        
        assert result['success'] is False
        assert 'AI服务不可用' in result['message']


# ==================== 单例模式测试 ====================

class TestSingleton:
    """测试单例模式"""
    
    def test_get_ai_service_singleton(self):
        """测试获取单例"""
        service1 = get_ai_service()
        service2 = get_ai_service()
        
        assert service1 is service2
    
    def test_reset_ai_service(self):
        """测试重置单例"""
        service1 = get_ai_service()
        reset_ai_service()
        service2 = get_ai_service()
        
        assert service1 is not service2


# ==================== 集成测试 ====================

@skip_if_no_ollama
class TestIntegration:
    """集成测试（需要Ollama服务）"""
    
    def test_full_analysis_flow(self):
        """测试完整分析流程"""
        service = AIService()
        
        if not service.is_available():
            pytest.skip("Ollama服务不可用")
        
        test_conversation = """
用户: 我想学习Python，有什么建议吗？

助手: 学习Python我建议：
1. 掌握基础语法
2. 做实践项目
3. 阅读优秀代码

用户: 谢谢！
"""
        
        # 测试完整分析
        result = service.analyze_conversation(test_conversation)
        
        if result:  # 可能因为模型未下载而失败
            assert isinstance(result, AIAnalysisResult)
            assert len(result.summary) > 0
            assert len(result.category) > 0
            assert len(result.tags) > 0
            assert 0 <= result.confidence <= 1
    
    def test_quick_summary(self):
        """测试快速摘要"""
        service = AIService()
        
        if not service.is_available():
            pytest.skip("Ollama服务不可用")
        
        summary = service.generate_summary("用户: 你好\n助手: 你好！")
        
        if summary:  # 可能因为模型未下载而失败
            assert isinstance(summary, str)
            assert len(summary) > 0


# ==================== 性能测试 ====================

@skip_if_no_ollama
class TestPerformance:
    """性能测试"""
    
    def test_analysis_time(self):
        """测试分析耗时"""
        import time
        
        service = AIService()
        
        if not service.is_available():
            pytest.skip("Ollama服务不可用")
        
        test_text = "用户: 你好\n助手: 你好！有什么可以帮你的吗？" * 10
        
        start_time = time.time()
        result = service.analyze_conversation(test_text)
        elapsed = time.time() - start_time
        
        # 应该在合理时间内完成（<30秒）
        if result:
            assert elapsed < 30, f"分析耗时过长: {elapsed:.2f}秒"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
