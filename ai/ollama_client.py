"""
Ollama本地大模型客户端
用于生成摘要、分类和标签
"""
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    """AI分析结果"""
    summary: str
    category: str
    tags: List[str]
    confidence: float = 0.0  # 置信度


class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(self, 
                 base_url: str = None,
                 model: str = None,
                 timeout: int = 60):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务地址（默认从环境变量OLLAMA_HOST读取）
            model: 使用的模型名称（默认从环境变量OLLAMA_MODEL读取，推荐qwen2.5:3b）
            timeout: 请求超时时间（秒）
        """
        import os
        
        self.base_url = (base_url or os.getenv('OLLAMA_HOST', 'http://localhost:11434')).rstrip('/')
        self.model = model or os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')
        self.timeout = timeout
        self.api_url = f"{self.base_url}/api/generate"
    
    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """列出可用的模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用Ollama生成文本
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
        
        Returns:
            生成的文本
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # 降低随机性，提高稳定性
                "top_p": 0.9,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.Timeout:
            raise TimeoutError(f"Ollama请求超时（{self.timeout}秒）")
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama请求失败: {str(e)}")
    
    def analyze_conversation(self, conversation_text: str) -> AIAnalysisResult:
        """
        分析对话内容，生成摘要、分类和标签
        
        Args:
            conversation_text: 完整对话文本
        
        Returns:
            AIAnalysisResult对象
        """
        # 限制输入长度（避免超过模型上下文窗口）
        max_length = 8000
        if len(conversation_text) > max_length:
            conversation_text = conversation_text[:max_length] + "\n...(内容过长已截断)"
        
        # 构建提示词
        prompt = self._build_analysis_prompt(conversation_text)
        system_prompt = "你是一个专业的AI对话分析助手，擅长提取关键信息、生成摘要和分类。"
        
        # 调用模型
        response = self.generate(prompt, system_prompt)
        
        # 解析结果
        return self._parse_analysis_result(response)
    
    def _build_analysis_prompt(self, conversation_text: str) -> str:
        """构建分析提示词"""
        prompt = f"""请分析以下AI对话内容，并按照JSON格式返回结果：

对话内容：
{conversation_text}

请提供：
1. summary: 一个简洁的摘要（100-150字），概括对话的核心主题和关键结论
2. category: 主要分类，从以下选项中选择一个：编程、写作、学习、策划、休闲娱乐、其他
3. tags: 3-5个关键词标签（例如：Python、机器学习、数据分析等）

返回格式（必须是有效的JSON）：
{{
    "summary": "对话摘要内容...",
    "category": "编程",
    "tags": ["Python", "数据分析", "pandas"]
}}

请直接返回JSON，不要添加任何其他文字说明。"""
        
        return prompt
    
    def _parse_analysis_result(self, response: str) -> AIAnalysisResult:
        """解析AI返回的分析结果"""
        try:
            # 尝试提取JSON（处理可能的markdown代码块）
            json_text = response
            
            # 移除可能的markdown代码块标记
            if '```json' in json_text:
                json_text = json_text.split('```json')[1].split('```')[0]
            elif '```' in json_text:
                json_text = json_text.split('```')[1].split('```')[0]
            
            # 解析JSON
            data = json.loads(json_text.strip())
            
            return AIAnalysisResult(
                summary=data.get('summary', '').strip(),
                category=data.get('category', '其他').strip(),
                tags=data.get('tags', []),
                confidence=0.8
            )
            
        except json.JSONDecodeError:
            # JSON解析失败，尝试手动提取
            print(f"[警告] JSON解析失败，尝试手动提取。原始响应:\n{response}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> AIAnalysisResult:
        """备用解析方法（当JSON解析失败时）"""
        import re
        
        # 尝试提取摘要
        summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', response)
        summary = summary_match.group(1) if summary_match else response[:150]
        
        # 尝试提取分类
        category_match = re.search(r'"category"\s*:\s*"([^"]+)"', response)
        category = category_match.group(1) if category_match else "其他"
        
        # 尝试提取标签
        tags_match = re.search(r'"tags"\s*:\s*\[(.*?)\]', response)
        tags = []
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [t.strip(' "\'') for t in tags_str.split(',')]
        
        return AIAnalysisResult(
            summary=summary,
            category=category,
            tags=tags,
            confidence=0.5  # 降低置信度
        )
    
    def generate_summary_only(self, conversation_text: str, max_words: int = 150) -> str:
        """仅生成摘要（快速模式）"""
        prompt = f"""请为以下对话生成一个简洁的摘要（不超过{max_words}字）：

{conversation_text[:5000]}

摘要："""
        
        return self.generate(prompt)
    
    def generate_tags_only(self, conversation_text: str, num_tags: int = 5) -> List[str]:
        """仅生成标签（快速模式）"""
        prompt = f"""请为以下对话提取{num_tags}个关键词标签，用逗号分隔：

{conversation_text[:3000]}

标签："""
        
        response = self.generate(prompt)
        
        # 解析标签
        tags = [tag.strip() for tag in response.split(',')]
        return tags[:num_tags]


# 使用示例
if __name__ == '__main__':
    # 初始化客户端
    client = OllamaClient(model="qwen2.5:7b")
    
    # 检查服务是否可用
    if not client.is_available():
        print("错误: Ollama服务不可用，请确保已启动Ollama")
        print("启动命令: ollama serve")
        exit(1)
    
    print(f"可用模型: {client.list_models()}")
    
    # 测试对话
    test_conversation = """
用户: 你好，我想学习Python数据分析，应该从哪里开始？

助手: 很高兴帮助你！学习Python数据分析，我建议按以下步骤：

1. 掌握Python基础语法
2. 学习NumPy和Pandas库
3. 了解数据可视化（Matplotlib、Seaborn）
4. 实践项目

用户: Pandas有哪些常用的数据操作？

助手: Pandas的常用操作包括：
- 数据读取：read_csv(), read_excel()
- 数据筛选：loc[], iloc[]
- 数据清洗：dropna(), fillna()
- 数据聚合：groupby(), agg()
"""
    
    try:
        print("\n开始分析对话...")
        result = client.analyze_conversation(test_conversation)
        
        print(f"\n摘要: {result.summary}")
        print(f"分类: {result.category}")
        print(f"标签: {', '.join(result.tags)}")
        print(f"置信度: {result.confidence}")
        
    except Exception as e:
        print(f"错误: {e}")
