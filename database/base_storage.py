"""
数据存储抽象接口

定义统一的存储接口，支持多种存储后端（SQLite, Elasticsearch等）
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime


class BaseStorage(ABC):
    """存储接口抽象基类"""
    
    # ==================== 连接管理 ====================
    
    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """检查连接状态"""
        pass
    
    # ==================== 对话管理 ====================
    
    @abstractmethod
    def add_conversation(self,
                        platform: str,
                        source_url: str,
                        title: str,
                        summary: str,
                        raw_content: str,
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> int:
        """
        添加对话
        
        Args:
            platform: 平台名称（chatgpt, claude等）
            source_url: 源URL
            title: 标题
            summary: 摘要
            raw_content: 原始内容（JSON字符串）
            category: 分类
            tags: 标签列表
        
        Returns:
            对话ID
        
        Raises:
            ValueError: 如果参数无效
        """
        pass
    
    @abstractmethod
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        获取对话详情
        
        Args:
            conversation_id: 对话ID
        
        Returns:
            对话详情字典，不存在返回None
        """
        pass
    
    @abstractmethod
    def get_conversation_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通过URL获取对话
        
        Args:
            url: 源URL
        
        Returns:
            对话详情字典，不存在返回None
        """
        pass
    
    @abstractmethod
    def list_conversations(self,
                          platform: Optional[str] = None,
                          category: Optional[str] = None,
                          limit: int = 50,
                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            platform: 平台过滤
            category: 分类过滤
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            对话列表
        """
        pass
    
    @abstractmethod
    def update_conversation(self,
                           conversation_id: int,
                           **kwargs: Any) -> bool:
        """
        更新对话信息
        
        Args:
            conversation_id: 对话ID
            **kwargs: 要更新的字段
        
        Returns:
            更新是否成功
        """
        pass
    
    @abstractmethod
    def delete_conversation(self, conversation_id: int) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话ID
        
        Returns:
            删除是否成功
        """
        pass
    
    # ==================== 标签管理 ====================
    
    @abstractmethod
    def add_tags(self, conversation_id: int, tags: List[str]) -> None:
        """
        添加标签
        
        Args:
            conversation_id: 对话ID
            tags: 标签列表
        """
        pass
    
    @abstractmethod
    def remove_tags(self, conversation_id: int, tags: List[str]) -> None:
        """
        移除标签
        
        Args:
            conversation_id: 对话ID
            tags: 标签列表
        """
        pass
    
    @abstractmethod
    def get_conversation_tags(self, conversation_id: int) -> List[str]:
        """
        获取对话标签
        
        Args:
            conversation_id: 对话ID
        
        Returns:
            标签列表
        """
        pass
    
    @abstractmethod
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        获取所有标签及使用次数
        
        Returns:
            标签列表，每个标签包含name和count
        """
        pass
    
    # ==================== 搜索功能 ====================
    
    @abstractmethod
    def search_conversations(self,
                            keyword: str,
                            limit: int = 50,
                            context_size: int = 100) -> List[Dict[str, Any]]:
        """
        全文搜索对话
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            context_size: 上下文字符数
        
        Returns:
            搜索结果列表，包含匹配片段和上下文
        """
        pass
    
    @abstractmethod
    def advanced_search(self,
                       keyword: Optional[str] = None,
                       platform: Optional[str] = None,
                       category: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """
        高级搜索
        
        Args:
            keyword: 关键词
            platform: 平台过滤
            category: 分类过滤
            tags: 标签过滤
            date_from: 起始日期
            date_to: 结束日期
            limit: 返回数量
        
        Returns:
            搜索结果列表
        """
        pass
    
    # ==================== 统计功能 ====================
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典，包含：
            - total_conversations: 总对话数
            - platforms: 各平台数量
            - categories: 各分类数量
            - total_tags: 总标签数
            - recent_conversations: 最近对话数
        """
        pass
    
    # ==================== 数据维护 ====================
    
    @abstractmethod
    def optimize(self) -> None:
        """优化存储（如重建索引、清理碎片等）"""
        pass
    
    @abstractmethod
    def backup(self, backup_path: str) -> bool:
        """
        备份数据
        
        Args:
            backup_path: 备份路径
        
        Returns:
            备份是否成功
        """
        pass
    
    @abstractmethod
    def export_data(self, export_format: str = 'json') -> str:
        """
        导出数据
        
        Args:
            export_format: 导出格式（json, csv等）
        
        Returns:
            导出的数据（字符串格式）
        """
        pass
    
    @abstractmethod
    def import_data(self, data: str, data_format: str = 'json') -> int:
        """
        导入数据
        
        Args:
            data: 数据内容
            data_format: 数据格式
        
        Returns:
            导入的记录数
        """
        pass


class StorageFactory:
    """存储工厂类"""
    
    _storage_types = {}
    
    @classmethod
    def register(cls, storage_type: str, storage_class: type):
        """
        注册存储类型
        
        Args:
            storage_type: 存储类型名称
            storage_class: 存储类
        """
        cls._storage_types[storage_type] = storage_class
    
    @classmethod
    def create(cls, storage_type: str, **kwargs) -> BaseStorage:
        """
        创建存储实例
        
        Args:
            storage_type: 存储类型（sqlite, elasticsearch等）
            **kwargs: 存储配置参数
        
        Returns:
            存储实例
        
        Raises:
            ValueError: 如果存储类型不支持
        """
        if storage_type not in cls._storage_types:
            raise ValueError(
                f"Unknown storage type: {storage_type}. "
                f"Available types: {list(cls._storage_types.keys())}"
            )
        
        storage_class = cls._storage_types[storage_type]
        return storage_class(**kwargs)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """获取所有可用的存储类型"""
        return list(cls._storage_types.keys())
