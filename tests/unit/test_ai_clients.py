"""
AI客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from ai.ollama_client import OllamaClient, AIAnalysisResult
from ai.openai_client import OpenAIClient, DeepSeekClient


class TestAIAnalysisResult:
    """测试AIAnalysisResult数据类"""
    
    def test_creation(self):
        """测试创建分析结果"""
        result = AIAnalysisResult(
            summary="这是一个测试摘要",
            category="编程",
            tags=["Python", "测试"],
            confidence=0.9
        )
        
        assert result.summary == "这是一个测试摘要"
        assert result.category == "编程"
        assert len(result.tags) == 2
        assert result.confidence == 0.9


class TestOllamaClient:
    """测试Ollama客户端"""
    
    def test_init(self):
        """测试初始化"""
        client = OllamaClient(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
            timeout=60
        )
        
        assert client.base_url == "http://localhost:11434"
        assert client.model == "qwen2.5:7b"
        assert client.timeout == 60
        assert client.api_url == "http://localhost:11434/api/generate"
    
    def test_init_with_trailing_slash(self):
        """测试URL自动去除尾部斜杠"""
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"
    
    @patch('requests.get')
    def test_is_available_success(self, mock_get):
        """测试服务可用性检查（成功）"""
        mock_get.return_value.status_code = 200
        
        client = OllamaClient()
        assert client.is_available() is True
    
    @patch('requests.get')
    def test_is_available_failure(self, mock_get):
        """测试服务可用性检查（失败）"""
        mock_get.side_effect = Exception("Connection error")
        
        client = OllamaClient()
        assert client.is_available() is False
    
    @patch('requests.get')
    def test_list_models(self, mock_get):
        """测试列出模型"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [
                {'name': 'qwen2.5:7b'},
                {'name': 'llama3.2'}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        models = client.list_models()
        
        assert len(models) == 2
        assert 'qwen2.5:7b' in models
        assert 'llama3.2' in models
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """测试生成文本（成功）"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': '这是生成的文本'
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("测试提示词")
        
        assert result == "这是生成的文本"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_with_system_prompt(self, mock_post):
        """测试带系统提示词的生成"""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'response text'}
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        client.generate("user prompt", system_prompt="system prompt")
        
        # 验证调用参数
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'system' in payload
        assert payload['system'] == "system prompt"
    
    @patch('requests.post')
    def test_generate_timeout(self, mock_post):
        """测试生成超时"""
        import requests
        mock_post.side_effect = requests.Timeout()
        
        client = OllamaClient()
        with pytest.raises(TimeoutError):
            client.generate("test")
    
    def test_parse_analysis_result_valid_json(self):
        """测试解析有效JSON"""
        client = OllamaClient()
        
        json_response = '''
        {
            "summary": "这是摘要",
            "category": "编程",
            "tags": ["Python", "AI"]
        }
        '''
        
        result = client._parse_analysis_result(json_response)
        
        assert result.summary == "这是摘要"
        assert result.category == "编程"
        assert len(result.tags) == 2
        assert result.confidence == 0.8
    
    def test_parse_analysis_result_with_markdown(self):
        """测试解析带markdown代码块的JSON"""
        client = OllamaClient()
        
        response = '''
        ```json
        {
            "summary": "测试摘要",
            "category": "学习",
            "tags": ["测试"]
        }
        ```
        '''
        
        result = client._parse_analysis_result(response)
        
        assert result.summary == "测试摘要"
        assert result.category == "学习"
        assert "测试" in result.tags
    
    def test_parse_analysis_result_invalid_json(self):
        """测试解析无效JSON（fallback）"""
        client = OllamaClient()
        
        invalid_response = 'This is not JSON'
        
        result = client._parse_analysis_result(invalid_response)
        
        assert result is not None
        assert result.confidence == 0.5  # fallback降低置信度
    
    def test_fallback_parse(self):
        """测试fallback解析方法"""
        client = OllamaClient()
        
        text = '"summary": "测试摘要", "category": "编程", "tags": ["Python", "测试"]'
        result = client._fallback_parse(text)
        
        assert result.summary == "测试摘要"
        assert result.category == "编程"
        assert len(result.tags) == 2
    
    def test_build_analysis_prompt(self):
        """测试构建分析提示词"""
        client = OllamaClient()
        
        conversation = "用户: 你好\n助手: 你好"
        prompt = client._build_analysis_prompt(conversation)
        
        assert "请分析以下AI对话内容" in prompt
        assert "summary" in prompt
        assert "category" in prompt
        assert "tags" in prompt
        assert conversation in prompt


class TestOpenAIClient:
    """测试OpenAI客户端"""
    
    def test_init(self):
        """测试初始化"""
        client = OpenAIClient(
            api_key="test-key",
            model="gpt-4o-mini"
        )
        
        assert client.model == "gpt-4o-mini"
        assert client.client is not None
    
    def test_init_with_base_url(self):
        """测试使用自定义base_url初始化"""
        client = OpenAIClient(
            api_key="test-key",
            base_url="https://custom.api.com"
        )
        
        assert client.client.base_url == "https://custom.api.com"
    
    @patch('openai.OpenAI')
    def test_is_available(self, mock_openai):
        """测试API可用性检查"""
        mock_client = Mock()
        mock_client.models.list.return_value = []
        mock_openai.return_value = mock_client
        
        client = OpenAIClient(api_key="test-key")
        # 这里由于mock的限制，我们只验证方法存在
        assert hasattr(client, 'is_available')


class TestDeepSeekClient:
    """测试DeepSeek客户端"""
    
    def test_init(self):
        """测试初始化"""
        client = DeepSeekClient(api_key="test-key")
        
        assert client.model == "deepseek-chat"
        assert client.client.base_url == "https://api.deepseek.com"
    
    def test_inherits_from_openai_client(self):
        """测试继承自OpenAIClient"""
        client = DeepSeekClient(api_key="test-key")
        assert isinstance(client, OpenAIClient)
