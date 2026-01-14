"""
基础爬虫抽象类
定义所有平台爬虫的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """单条消息数据结构"""
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp
        }


@dataclass
class ConversationData:
    """对话数据结构"""
    platform: str
    url: str
    title: str
    messages: List[Message]
    metadata: Dict = None
    
    def to_dict(self) -> dict:
        return {
            'platform': self.platform,
            'url': self.url,
            'title': self.title,
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata or {}
        }
    
    @property
    def message_count(self) -> int:
        return len(self.messages)
    
    @property
    def word_count(self) -> int:
        """计算总字数"""
        return sum(len(msg.content) for msg in self.messages)
    
    def get_full_text(self) -> str:
        """获取完整对话文本（用于AI分析）"""
        text_parts = []
        for msg in self.messages:
            prefix = "用户" if msg.role == "user" else "助手"
            text_parts.append(f"{prefix}: {msg.content}")
        return "\n\n".join(text_parts)


class BaseScraper(ABC):
    """爬虫基类"""
    
    def __init__(self):
        self.platform_name = self.__class__.__name__.replace('Scraper', '').lower()
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """判断是否能处理该URL"""
        pass
    
    @abstractmethod
    def scrape(self, url: str) -> ConversationData:
        """抓取对话内容"""
        pass
    
    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        return url.startswith('http://') or url.startswith('https://')
