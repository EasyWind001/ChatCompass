"""
OpenAI API客户端（备用方案）
用于在线API调用
"""
import json
from typing import List
from openai import OpenAI

from .ollama_client import AIAnalysisResult


class OpenAIClient:
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥
            model: 模型名称（gpt-4o-mini, gpt-4o等）
            base_url: 自定义API地址（用于兼容其他服务如DeepSeek）
        """
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        try:
            # 发送一个简单的测试请求
            self.client.models.list()
            return True
        except:
            return False
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
    
    def analyze_conversation(self, conversation_text: str) -> AIAnalysisResult:
        """分析对话内容"""
        # 限制长度
        max_length = 12000
        if len(conversation_text) > max_length:
            conversation_text = conversation_text[:max_length] + "\n...(内容过长已截断)"
        
        prompt = f"""请分析以下AI对话内容，并按照JSON格式返回结果：

对话内容：
{conversation_text}

请提供：
1. summary: 一个简洁的摘要（100-150字），概括对话的核心主题和关键结论
2. category: 主要分类，从以下选项中选择一个：编程、写作、学习、策划、休闲娱乐、其他
3. tags: 3-5个关键词标签

返回格式（必须是有效的JSON）：
{{
    "summary": "对话摘要内容...",
    "category": "编程",
    "tags": ["Python", "数据分析", "pandas"]
}}"""
        
        system_prompt = "你是一个专业的AI对话分析助手。请严格按照JSON格式返回结果，不要添加其他文字。"
        
        response = self.generate(prompt, system_prompt)
        
        # 解析结果
        try:
            # 移除可能的markdown标记
            json_text = response
            if '```json' in json_text:
                json_text = json_text.split('```json')[1].split('```')[0]
            elif '```' in json_text:
                json_text = json_text.split('```')[1].split('```')[0]
            
            data = json.loads(json_text.strip())
            
            return AIAnalysisResult(
                summary=data.get('summary', '').strip(),
                category=data.get('category', '其他').strip(),
                tags=data.get('tags', []),
                confidence=0.9
            )
        except:
            # 降级处理
            return AIAnalysisResult(
                summary=response[:200],
                category="其他",
                tags=[],
                confidence=0.5
            )


# DeepSeek客户端（性价比高）
class DeepSeekClient(OpenAIClient):
    """DeepSeek API客户端（兼容OpenAI接口）"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.deepseek.com"
        )


# 使用示例
if __name__ == '__main__':
    # OpenAI
    # client = OpenAIClient(api_key="your-api-key")
    
    # DeepSeek（推荐，性价比高）
    client = DeepSeekClient(api_key="your-deepseek-api-key")
    
    test_conversation = "用户: 你好\n助手: 你好，有什么可以帮助你的吗？"
    
    try:
        result = client.analyze_conversation(test_conversation)
        print(f"摘要: {result.summary}")
        print(f"分类: {result.category}")
        print(f"标签: {result.tags}")
    except Exception as e:
        print(f"错误: {e}")
