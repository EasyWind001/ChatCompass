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
    timeout: int = 180  # 增加到180秒处理大文本
    auto_analyze: bool = False  # 是否自动分析新对话
    enable_fallback: bool = True  # 超时时是否启用降级方案
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        """从环境变量创建配置"""
        return cls(
            enabled=os.getenv('AI_ENABLED', 'true').lower() == 'true',
            backend=os.getenv('AI_BACKEND', 'ollama'),
            ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            ollama_model=os.getenv('OLLAMA_MODEL', 'qwen2.5:3b'),
            timeout=int(os.getenv('AI_TIMEOUT', '180')),  # 默认180秒
            auto_analyze=os.getenv('AI_AUTO_ANALYZE', 'false').lower() == 'true',
            enable_fallback=os.getenv('AI_ENABLE_FALLBACK', 'true').lower() == 'true'
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
                            title: str = "",
                            show_progress: bool = True) -> Optional[AIAnalysisResult]:
        """
        分析对话内容
        
        Args:
            conversation_text: 对话文本
            title: 对话标题（可选）
            show_progress: 是否显示处理进度（推荐大文本时开启）
        
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
            text_length = len(conversation_text)
            title_info = f': {title}' if title else ''
            
            logger.info(f"🚀 开始分析对话{title_info}（{text_length:,} 字符）")
            
            # 大文本提示
            if text_length > 10000:
                logger.info(f"💡 检测到大文本，预计处理时间: {text_length//1000 * 2}-{text_length//1000 * 5}秒")
            
            # 调用AI分析
            result = self.client.analyze_conversation(conversation_text)
            
            logger.info(f"✅ 分析完成: {result.category} | 置信度: {result.confidence}")
            logger.info(f"   📝 摘要: {result.summary[:80]}{'...' if len(result.summary) > 80 else ''}")
            logger.info(f"   🏷️  标签: {', '.join(result.tags)}")
            
            return result
        
        except TimeoutError as e:
            logger.error(f"❌ 分析超时: {e}")
            logger.error(f"💡 建议: 1) 增加AI_TIMEOUT环境变量 2) 使用分段处理 3) 切换到更快的模型")
            
            # 降级方案：生成基础摘要
            if self.config.enable_fallback:
                logger.info("🔄 启动降级方案：生成基础摘要（基于规则）...")
                return self._fallback_analysis(conversation_text, title)
            else:
                logger.warning("⚠️  降级方案已禁用，返回None")
                return None
        
        except Exception as e:
            logger.error(f"❌ 分析失败: {e}")
            
            # 降级方案：生成基础摘要
            if self.config.enable_fallback:
                logger.info("🔄 启动降级方案：生成基础摘要（基于规则）...")
                return self._fallback_analysis(conversation_text, title)
            else:
                logger.warning("⚠️  降级方案已禁用，返回None")
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
    
    def _fallback_analysis(self, 
                           conversation_text: str,
                           title: str = "") -> Optional[AIAnalysisResult]:
        """
        降级分析方案（当AI分析失败或超时时）
        
        使用规则提取而非AI模型：
        1. 提取前150字作为摘要
        2. 基于关键词进行简单分类
        3. 提取高频词作为标签
        
        Args:
            conversation_text: 对话文本
            title: 对话标题
        
        Returns:
            AIAnalysisResult对象
        """
        try:
            from collections import Counter
            import re
            
            # 1. 生成简单摘要（取前150字 + 标题）
            summary = title if title else ""
            if not summary or len(summary) < 20:
                # 提取第一条用户消息
                first_msg = conversation_text.split('\n\n')[0] if '\n\n' in conversation_text else conversation_text
                summary = first_msg[:150]
            
            # 清理摘要
            summary = summary.strip()
            if len(summary) > 150:
                summary = summary[:147] + "..."
            
            # 2. 基于关键词的简单分类
            category = self._simple_categorize(conversation_text)
            
            # 3. 提取高频词作为标签
            tags = self._extract_simple_tags(conversation_text)
            
            logger.info(f"✅ 降级分析完成: {category} | 标签: {', '.join(tags)}")
            
            return AIAnalysisResult(
                summary=summary or "无法生成摘要",
                category=category,
                tags=tags,
                confidence=0.3  # 降低置信度，表明是降级方案
            )
        
        except Exception as e:
            logger.error(f"❌ 降级分析也失败: {e}")
            # 返回最基础的结果
            return AIAnalysisResult(
                summary=title[:100] if title else "对话内容",
                category="其他",
                tags=["未分类"],
                confidence=0.1
            )
    
    def _simple_categorize(self, text: str) -> str:
        """基于关键词的简单分类"""
        text_lower = text.lower()
        
        # 编程相关关键词
        if any(kw in text_lower for kw in [
            'python', 'java', 'javascript', 'code', 'function', 'class',
            'api', 'bug', 'debug', 'git', 'docker', 'database', '代码',
            '编程', '函数', '算法', 'sql', 'react', 'vue', 'node'
        ]):
            return "编程"
        
        # 写作相关
        if any(kw in text_lower for kw in [
            '写作', '文案', '文章', '润色', '修改', '优化',
            'write', 'article', 'essay', 'blog', '博客'
        ]):
            return "写作"
        
        # 学习相关
        if any(kw in text_lower for kw in [
            '学习', '教程', '如何', '怎么', '什么是', '解释',
            'learn', 'tutorial', 'how to', 'what is', 'explain'
        ]):
            return "学习"
        
        # 策划相关
        if any(kw in text_lower for kw in [
            '方案', '计划', '策划', '活动', '营销', '推广',
            'plan', 'strategy', 'marketing', 'campaign'
        ]):
            return "策划"
        
        # 休闲娱乐
        if any(kw in text_lower for kw in [
            '游戏', '电影', '音乐', '小说', '故事', '聊天',
            'game', 'movie', 'music', 'story', 'chat'
        ]):
            return "休闲娱乐"
        
        return "其他"
    
    def _extract_simple_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """提取简单标签（基于高频词）"""
        import re
        from collections import Counter
        
        # 分词（简单的空格和标点分隔）
        words = re.findall(r'[\w]+', text.lower())
        
        # 过滤停用词和短词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can',
            '的', '了', '是', '在', '和', '有', '我', '你', '他', '她', '它',
            '这', '那', '个', '们', '吗', '呢', '啊', '哦', '嗯'
        }
        
        # 过滤和统计
        words = [w for w in words if len(w) > 2 and w not in stop_words]
        word_freq = Counter(words)
        
        # 获取高频词
        common_words = word_freq.most_common(max_tags * 2)
        
        # 提取前N个作为标签（避免过于通用的词）
        tags = []
        for word, freq in common_words:
            if freq > 1 and word not in {'user', 'assistant', 'message', 'conversation'}:
                tags.append(word)
            if len(tags) >= max_tags:
                break
        
        # 如果标签太少，补充一些默认标签
        if len(tags) < 2:
            tags.append("对话")
        
        return tags[:max_tags]
    
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
