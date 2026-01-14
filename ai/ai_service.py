"""
AI服务管理器

统一管理AI分析功能，支持多种AI后端（Ollama、OpenAI等）
提供对话摘要、标签提取、自动分类等功能。

作者: ChatCompass Team
版本: v1.2.2
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from .ollama_client import OllamaClient, AIAnalysisResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """AI服务配置"""
    enabled: bool = True
    backend: str = "ollama"  # ollama, openai, deepseek
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    timeout: int = 60
    auto_analyze: bool = False  # 是否自动分析新对话
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        """从环境变量创建配置"""
        return cls(
            enabled=os.getenv('AI_ENABLED', 'true').lower() == 'true',
            backend=os.getenv('AI_BACKEND', 'ollama'),
            ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            ollama_model=os.getenv('OLLAMA_MODEL', 'qwen2.5:3b'),
            timeout=int(os.getenv('AI_TIMEOUT', '60')),
            auto_analyze=os.getenv('AI_AUTO_ANALYZE', 'false').lower() == 'true'
        )


class AIService:
    """AI服务管理器"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        """
        初始化AI服务
        
        Args:
            config: AI配置对象，如果为None则从环境变量读取
        """
        self.config = config or AIConfig.from_env()
        self.client = None
        
        if self.config.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化AI客户端"""
        try:
            if self.config.backend == 'ollama':
                self.client = OllamaClient(
                    base_url=self.config.ollama_host,
                    model=self.config.ollama_model,
                    timeout=self.config.timeout
                )
                logger.info(f"✅ Ollama客户端初始化成功: {self.config.ollama_model}")
            
            elif self.config.backend == 'openai':
                from .openai_client import OpenAIClient
                self.client = OpenAIClient()
                logger.info("✅ OpenAI客户端初始化成功")
            
            elif self.config.backend == 'deepseek':
                from .openai_client import DeepSeekClient
                self.client = DeepSeekClient()
                logger.info("✅ DeepSeek客户端初始化成功")
            
            else:
                raise ValueError(f"不支持的AI后端: {self.config.backend}")
        
        except Exception as e:
            logger.error(f"❌ AI客户端初始化失败: {e}")
            self.config.enabled = False
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        if not self.config.enabled or not self.client:
            return False
        
        try:
            if isinstance(self.client, OllamaClient):
                return self.client.is_available()
            else:
                # 其他客户端的检查逻辑
                return True
        except:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取AI服务状态"""
        status = {
            'enabled': self.config.enabled,
            'backend': self.config.backend,
            'available': False,
            'model': None,
            'available_models': []
        }
        
        if not self.config.enabled:
            status['message'] = 'AI功能未启用'
            return status
        
        if not self.client:
            status['message'] = 'AI客户端未初始化'
            return status
        
        try:
            status['available'] = self.is_available()
            
            if isinstance(self.client, OllamaClient):
                status['model'] = self.client.model
                if status['available']:
                    status['available_models'] = self.client.list_models()
            
            status['message'] = 'AI服务正常' if status['available'] else 'AI服务不可用'
        
        except Exception as e:
            status['message'] = f'状态检查失败: {str(e)}'
        
        return status
    
    def analyze_conversation(self, 
                            conversation_text: str,
                            title: str = "") -> Optional[AIAnalysisResult]:
        """
        分析对话内容
        
        Args:
            conversation_text: 对话文本
            title: 对话标题（可选）
        
        Returns:
            AIAnalysisResult对象，失败返回None
        """
        if not self.config.enabled:
            logger.warning("AI功能未启用")
            return None
        
        if not self.is_available():
            logger.warning("AI服务不可用")
            return None
        
        try:
            logger.info(f"开始分析对话{f': {title}' if title else ''}...")
            
            # 调用AI分析
            result = self.client.analyze_conversation(conversation_text)
            
            logger.info(f"✅ 分析完成: {result.category} | 置信度: {result.confidence}")
            logger.debug(f"   摘要: {result.summary[:50]}...")
            logger.debug(f"   标签: {', '.join(result.tags)}")
            
            return result
        
        except TimeoutError as e:
            logger.error(f"❌ 分析超时: {e}")
            return None
        
        except Exception as e:
            logger.error(f"❌ 分析失败: {e}")
            return None
    
    def generate_summary(self, 
                        conversation_text: str,
                        max_words: int = 150) -> Optional[str]:
        """
        快速生成摘要（不包含分类和标签）
        
        Args:
            conversation_text: 对话文本
            max_words: 最大字数
        
        Returns:
            摘要文本，失败返回None
        """
        if not self.is_available():
            return None
        
        try:
            if isinstance(self.client, OllamaClient):
                return self.client.generate_summary_only(conversation_text, max_words)
            else:
                # 其他客户端使用完整分析
                result = self.analyze_conversation(conversation_text)
                return result.summary if result else None
        
        except Exception as e:
            logger.error(f"❌ 生成摘要失败: {e}")
            return None
    
    def generate_tags(self,
                     conversation_text: str,
                     num_tags: int = 5) -> Optional[List[str]]:
        """
        快速生成标签
        
        Args:
            conversation_text: 对话文本
            num_tags: 标签数量
        
        Returns:
            标签列表，失败返回None
        """
        if not self.is_available():
            return None
        
        try:
            if isinstance(self.client, OllamaClient):
                return self.client.generate_tags_only(conversation_text, num_tags)
            else:
                # 其他客户端使用完整分析
                result = self.analyze_conversation(conversation_text)
                return result.tags if result else None
        
        except Exception as e:
            logger.error(f"❌ 生成标签失败: {e}")
            return None
    
    def batch_analyze(self,
                     conversations: List[Dict[str, str]],
                     callback=None) -> List[Optional[AIAnalysisResult]]:
        """
        批量分析对话
        
        Args:
            conversations: 对话列表，每个元素包含 'text' 和可选的 'title'
            callback: 进度回调函数 callback(current, total)
        
        Returns:
            分析结果列表
        """
        results = []
        total = len(conversations)
        
        for i, conv in enumerate(conversations, 1):
            text = conv.get('text', '')
            title = conv.get('title', '')
            
            result = self.analyze_conversation(text, title)
            results.append(result)
            
            if callback:
                callback(i, total)
        
        return results
    
    def pull_model(self, model_name: str = None) -> bool:
        """
        下载Ollama模型
        
        Args:
            model_name: 模型名称，默认使用配置的模型
        
        Returns:
            是否成功
        """
        if not isinstance(self.client, OllamaClient):
            logger.error("只有Ollama后端支持下载模型")
            return False
        
        import requests
        
        model = model_name or self.config.ollama_model
        
        try:
            logger.info(f"开始下载模型: {model}...")
            
            url = f"{self.config.ollama_host}/api/pull"
            response = requests.post(
                url,
                json={"name": model},
                stream=True,
                timeout=300  # 5分钟超时
            )
            
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    status = data.get('status', '')
                    
                    if 'total' in data and 'completed' in data:
                        percent = (data['completed'] / data['total']) * 100
                        logger.info(f"下载进度: {percent:.1f}%")
                    else:
                        logger.info(status)
            
            logger.info(f"✅ 模型下载完成: {model}")
            return True
        
        except Exception as e:
            logger.error(f"❌ 模型下载失败: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试AI连接
        
        Returns:
            测试结果字典
        """
        result = {
            'success': False,
            'backend': self.config.backend,
            'message': '',
            'test_response': None
        }
        
        if not self.is_available():
            result['message'] = 'AI服务不可用'
            return result
        
        try:
            # 简单测试
            test_text = "用户: 你好\n助手: 你好！有什么可以帮你的吗？"
            
            logger.info("执行连接测试...")
            response = self.client.generate_summary_only(test_text, max_words=20)
            
            if response:
                result['success'] = True
                result['message'] = 'AI服务连接正常'
                result['test_response'] = response
                logger.info("✅ 连接测试成功")
            else:
                result['message'] = 'AI服务无响应'
                logger.warning("⚠️ 连接测试失败：无响应")
        
        except Exception as e:
            result['message'] = f'连接测试失败: {str(e)}'
            logger.error(f"❌ 连接测试异常: {e}")
        
        return result


# 全局AI服务实例（单例模式）
_ai_service_instance = None


def get_ai_service() -> AIService:
    """获取全局AI服务实例（单例）"""
    global _ai_service_instance
    
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    
    return _ai_service_instance


def reset_ai_service():
    """重置全局AI服务实例（用于测试）"""
    global _ai_service_instance
    _ai_service_instance = None


# 使用示例
if __name__ == '__main__':
    import sys
    
    # 创建AI服务
    ai_service = AIService()
    
    # 检查状态
    status = ai_service.get_status()
    print(f"\n{'='*60}")
    print("AI服务状态")
    print(f"{'='*60}")
    for key, value in status.items():
        print(f"{key}: {value}")
    print(f"{'='*60}\n")
    
    if not status['available']:
        print("❌ AI服务不可用，退出测试")
        sys.exit(1)
    
    # 测试连接
    test_result = ai_service.test_connection()
    print(f"\n连接测试: {'✅ 成功' if test_result['success'] else '❌ 失败'}")
    print(f"消息: {test_result['message']}")
    if test_result['test_response']:
        print(f"测试响应: {test_result['test_response']}")
    
    # 测试分析
    test_conversation = """
用户: 我想学习Python数据分析，应该从哪里开始？

助手: 学习Python数据分析，我建议：
1. 掌握Python基础语法
2. 学习NumPy和Pandas
3. 了解数据可视化
4. 实践真实项目

用户: Pandas有哪些常用操作？

助手: Pandas常用操作包括：
- 数据读取: read_csv(), read_excel()
- 数据筛选: loc[], iloc[]
- 数据清洗: dropna(), fillna()
- 数据聚合: groupby(), agg()
"""
    
    print(f"\n{'='*60}")
    print("对话分析测试")
    print(f"{'='*60}")
    
    result = ai_service.analyze_conversation(test_conversation, "Python数据分析学习")
    
    if result:
        print(f"\n📝 摘要:\n{result.summary}")
        print(f"\n📁 分类: {result.category}")
        print(f"\n🏷️  标签: {', '.join(result.tags)}")
        print(f"\n📊 置信度: {result.confidence}")
    else:
        print("❌ 分析失败")
    
    print(f"\n{'='*60}\n")
