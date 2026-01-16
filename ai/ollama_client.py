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
                 timeout: int = 180):  # 增加到180秒
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务地址（默认从环境变量OLLAMA_HOST读取）
            model: 使用的模型名称（默认从环境变量OLLAMA_MODEL读取，推荐qwen2.5:3b）
            timeout: 请求超时时间（秒），默认180秒用于处理大文本
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
    
    def generate(self, prompt: str, system_prompt: str = None, show_progress: bool = False) -> str:
        """
        调用Ollama生成文本
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            show_progress: 是否显示流式进度（用于大文本）
        
        Returns:
            生成的文本
        """
        import logging
        logger = logging.getLogger(__name__)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": show_progress,  # 大文本时使用流式输出
            "options": {
                "temperature": 0.3,  # 降低随机性，提高稳定性
                "top_p": 0.9,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            if show_progress:
                # 流式响应（显示进度）
                import sys
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout,
                    stream=True
                )
                response.raise_for_status()
                
                full_response = ""
                logger.info("⏳ 正在生成回复...")
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get('response', '')
                        full_response += chunk
                        
                        # 显示进度点
                        if data.get('done'):
                            logger.info("✅ 生成完成")
                        else:
                            # 每10个字符显示一个进度点
                            if len(full_response) % 10 == 0:
                                sys.stderr.write('.')
                                sys.stderr.flush()
                
                sys.stderr.write('\n')
                return full_response.strip()
            else:
                # 非流式响应
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get('response', '').strip()
            
        except requests.Timeout:
            raise TimeoutError(f"Ollama请求超时（{self.timeout}秒），建议分批处理或增加超时时间")
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama请求失败: {str(e)}")
    
    def analyze_conversation(self, conversation_text: str) -> AIAnalysisResult:
        """
        分析对话内容，生成摘要、分类和标签
        
        使用分段摘要合并策略处理长文本：
        1. 检测到超长文本时，按对话轮次分段
        2. 对每段生成摘要（并行处理）
        3. 合并所有摘要再生成最终结果
        
        Args:
            conversation_text: 完整对话文本
        
        Returns:
            AIAnalysisResult对象
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 显示处理提示
        text_length = len(conversation_text)
        logger.info(f"📊 开始分析对话（{text_length:,} 字符）...")
        
        # 分段摘要策略：超过阈值时使用
        segment_threshold = 12000  # 12000字符开始分段
        max_segment_length = 6000  # 每段最多6000字符
        
        if text_length >= segment_threshold:
            logger.info(f"💡 检测到超长文本，启用分段摘要策略...")
            return self._analyze_with_segments(conversation_text)
        else:
            # 短文本直接分析
            return self._analyze_direct(conversation_text)
    
    def _analyze_direct(self, conversation_text: str) -> AIAnalysisResult:
        """直接分析（短文本）"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 如果仍然超过8000字符，做简单截断
        max_length = 8000
        if len(conversation_text) > max_length:
            logger.warning(f"⚠️  文本超过{max_length}字符，截取关键部分（前70%+后30%）")
            head_length = int(max_length * 0.7)
            tail_length = int(max_length * 0.3)
            conversation_text = (
                conversation_text[:head_length] + 
                "\n\n...[中间内容已省略]...\n\n" +
                conversation_text[-tail_length:]
            )
        
        # 构建提示词
        logger.info("🔄 正在调用AI模型...")
        prompt = self._build_analysis_prompt(conversation_text)
        system_prompt = "你是一个专业的AI对话分析助手，擅长提取关键信息、生成摘要和分类。"
        
        # 调用模型
        response = self.generate(prompt, system_prompt)
        
        logger.info("✅ AI分析完成，正在解析结果...")
        
        # 解析结果
        return self._parse_analysis_result(response)
    
    def _analyze_with_segments(self, conversation_text: str) -> AIAnalysisResult:
        """分段分析（超长文本）"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 步骤1：智能分段（按对话轮次）
        segments = self._split_into_segments(conversation_text)
        logger.info(f"📦 已分为 {len(segments)} 段（每段约 {len(conversation_text)//len(segments):,} 字符）")
        
        # 步骤2：对每段生成摘要
        segment_summaries = []
        for i, segment in enumerate(segments, 1):
            logger.info(f"🔍 正在分析第 {i}/{len(segments)} 段...")
            summary = self._summarize_segment(segment, i)
            segment_summaries.append(summary)
            logger.info(f"  ✅ 第 {i} 段摘要: {summary[:60]}...")
        
        # 步骤3：合并摘要
        logger.info(f"🔗 合并 {len(segment_summaries)} 个分段摘要...")
        combined_summary = "\n\n".join([
            f"[第{i+1}段] {summary}" 
            for i, summary in enumerate(segment_summaries)
        ])
        
        # 步骤4：基于合并摘要生成最终结果
        logger.info("🎯 生成最终分析结果...")
        final_prompt = f"""基于以下分段摘要，生成一个完整的对话分析：

{combined_summary}

请提供：
1. 整体摘要（100-150字，概括所有段落的核心内容）
2. 主要分类（从：编程、写作、学习、策划、休闲娱乐、其他 中选择最合适的）
3. 关键标签（3-5个，提取最重要的主题词）
4. 置信度（0-1之间的浮点数）

JSON格式输出：
{{
  "summary": "...",
  "category": "...",
  "tags": ["tag1", "tag2", "tag3"],
  "confidence": 0.85
}}"""
        
        system_prompt = "你是一个专业的AI对话分析助手，擅长从多个分段摘要中提取整体信息。"
        response = self.generate(final_prompt, system_prompt)
        
        logger.info("✅ 分段分析完成")
        
        return self._parse_analysis_result(response)
    
    def _split_into_segments(self, text: str, max_segment_length: int = 6000) -> list:
        """
        智能分段：按对话轮次分割
        
        优先在对话边界（User/Assistant）处分割，避免截断单条消息
        """
        # 处理空文本或极短文本
        if not text or len(text) <= max_segment_length:
            return [text] if text else []
        
        # 尝试按对话轮次分割（常见的分隔符）
        separators = [
            '\n\nUser:',
            '\n\nAssistant:',
            '\n\n用户:',
            '\n\n助手:',
            '\n\n## ',
            '\n\n### ',
            '\n\n---',
            '\n\n'
        ]
        
        segments = []
        remaining_text = text
        
        while len(remaining_text) > max_segment_length:
            # 在max_segment_length附近找最佳分割点
            search_start = max(0, max_segment_length - 500)
            search_end = min(len(remaining_text), max_segment_length + 500)
            search_range = remaining_text[search_start:search_end]
            
            # 寻找最近的分隔符
            best_split = -1
            for separator in separators:
                pos = search_range.rfind(separator)
                if pos != -1:
                    best_split = search_start + pos
                    break
            
            # 如果找不到分隔符，强制在max_segment_length处分割
            if best_split == -1:
                best_split = max_segment_length
            
            # 分割
            segments.append(remaining_text[:best_split].strip())
            remaining_text = remaining_text[best_split:].strip()
        
        # 添加最后一段
        if remaining_text:
            segments.append(remaining_text)
        
        return segments
    
    def _summarize_segment(self, segment: str, segment_num: int) -> str:
        """
        对单个分段生成摘要
        
        Args:
            segment: 分段文本
            segment_num: 分段序号
        
        Returns:
            该段的摘要（100-150字）
        """
        prompt = f"""请为以下对话片段生成简洁摘要（100-150字）：

{segment[:3000]}  {'...(后续内容省略)' if len(segment) > 3000 else ''}

摘要要求：
1. 概括这段对话的主要内容和结论
2. 保留关键信息（问题、解决方案、重要观点）
3. 100-150字以内
4. 直接输出摘要文本，不要额外解释

摘要："""
        
        system_prompt = f"你是一个摘要生成助手，正在处理长对话的第{segment_num}段。"
        
        try:
            summary = self.generate(prompt, system_prompt)
            return summary.strip()
        except Exception as e:
            # 降级：返回前150字
            return segment[:150] + "..."
    
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
