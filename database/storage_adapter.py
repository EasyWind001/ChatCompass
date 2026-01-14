"""
存储适配器 - 为主程序提供统一的数据访问接口
支持SQLite和Elasticsearch无缝切换
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class StorageAdapter:
    """
    存储适配器
    
    将旧的DatabaseManager接口适配到新的BaseStorage接口
    这样主程序可以无需修改即可使用新的存储后端
    """
    
    def __init__(self, storage):
        """
        初始化适配器
        
        Args:
            storage: BaseStorage实例（SQLiteManager或ElasticsearchManager）
        """
        self.storage = storage
        self._storage_type = storage.__class__.__name__
    
    def add_conversation(self, 
                        source_url: str,
                        platform: str,
                        title: str,
                        raw_content: Dict[str, Any],
                        summary: Optional[str] = None,
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> str:
        """
        添加对话
        
        Args:
            source_url: 来源URL
            platform: 平台名称
            title: 标题
            raw_content: 原始内容（字典）
            summary: 摘要
            category: 分类
            tags: 标签列表
        
        Returns:
            对话ID
        """
        import json
        
        # 准备数据
        conversation = {
            'source_url': source_url,
            'platform': platform,
            'title': title,
            'raw_content': json.dumps(raw_content, ensure_ascii=False) if isinstance(raw_content, dict) else raw_content,
            'summary': summary,
            'category': category,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 添加统计信息
        if isinstance(raw_content, dict):
            messages = raw_content.get('messages', [])
            conversation['message_count'] = len(messages)
            conversation['word_count'] = sum(len(msg.get('content', '')) for msg in messages)
        
        return self.storage.add_conversation(conversation)
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """获取单个对话"""
        return self.storage.get_conversation(conv_id)
    
    def get_all_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取所有对话"""
        return self.storage.list_conversations(limit=limit, offset=offset)
    
    def search_conversations(self, 
                            keyword: str,
                            limit: int = 10,
                            context_size: int = 80) -> List[Dict[str, Any]]:
        """
        搜索对话
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            context_size: 上下文大小
        
        Returns:
            搜索结果列表
        """
        results = self.storage.search_conversations(keyword, limit=limit)
        
        # 为每个结果添加匹配上下文
        for result in results:
            self._add_match_context(result, keyword, context_size)
        
        return results
    
    def _add_match_context(self, 
                          result: Dict[str, Any],
                          keyword: str,
                          context_size: int = 80):
        """
        为搜索结果添加匹配上下文
        
        Args:
            result: 搜索结果
            keyword: 搜索关键词
            context_size: 上下文大小（单边字符数）
        """
        import json
        
        # 解析raw_content
        try:
            if isinstance(result.get('raw_content'), str):
                raw_content = json.loads(result['raw_content'])
            else:
                raw_content = result.get('raw_content', {})
            
            messages = raw_content.get('messages', [])
            matches = []
            
            # 在每条消息中查找匹配
            for i, msg in enumerate(messages):
                content = msg.get('content', '')
                role = msg.get('role', 'unknown')
                
                # 查找关键词位置
                keyword_lower = keyword.lower()
                content_lower = content.lower()
                
                pos = content_lower.find(keyword_lower)
                if pos != -1:
                    # 提取上下文
                    start = max(0, pos - context_size)
                    end = min(len(content), pos + len(keyword) + context_size)
                    
                    before = content[start:pos]
                    match_text = content[pos:pos + len(keyword)]
                    after = content[pos + len(keyword):end]
                    
                    # 如果不是从开头开始，加省略号
                    if start > 0:
                        before = '...' + before
                    if end < len(content):
                        after = after + '...'
                    
                    matches.append({
                        'message_index': i + 1,
                        'total_messages': len(messages),
                        'role': role,
                        'before_context': before,
                        'match_text': match_text,
                        'after_context': after
                    })
            
            result['matches'] = matches
        
        except Exception as e:
            result['matches'] = []
    
    def get_conversation_tags(self, conv_id: str) -> List[str]:
        """获取对话标签"""
        conversation = self.storage.get_conversation(conv_id)
        if conversation:
            tags = conversation.get('tags', [])
            if isinstance(tags, str):
                import json
                try:
                    tags = json.loads(tags)
                except:
                    tags = []
            return tags
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.storage.get_statistics()
        
        # 格式化为主程序期望的格式
        return {
            'total_conversations': stats.get('total_conversations', 0),
            'by_platform': stats.get('by_platform', {}),
            'by_category': stats.get('by_category', {}),
            'total_tags': stats.get('total_tags', 0)
        }
    
    def update_conversation(self, 
                           conv_id: str,
                           updates: Dict[str, Any]) -> bool:
        """更新对话"""
        updates['updated_at'] = datetime.now().isoformat()
        return self.storage.update_conversation(conv_id, updates)
    
    def delete_conversation(self, conv_id: str) -> bool:
        """删除对话"""
        return self.storage.delete_conversation(conv_id)
    
    def close(self):
        """关闭连接"""
        if hasattr(self.storage, 'close'):
            self.storage.close()
    
    @property
    def conn(self):
        """提供conn属性用于向后兼容（仅SQLite）"""
        if hasattr(self.storage, 'conn'):
            return self.storage.conn
        return None
    
    def __repr__(self):
        return f"<StorageAdapter backend={self._storage_type}>"
