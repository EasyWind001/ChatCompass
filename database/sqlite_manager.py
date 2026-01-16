"""
SQLite存储管理器 - 实现BaseStorage接口
包装DatabaseManager以提供统一的存储接口
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from .base_storage import BaseStorage
from .db_manager import DatabaseManager


class SQLiteManager(BaseStorage):
    """SQLite存储管理器"""
    
    def __init__(self, db_path: str = "chatcompass.db"):
        """
        初始化SQLite存储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.db = DatabaseManager(db_path)
        self.conn = self.db.conn
    
    def add_conversation(self, conversation: Dict[str, Any]) -> str:
        """
        添加对话
        
        Args:
            conversation: 对话数据字典
        
        Returns:
            对话ID（字符串形式）
        """
        # 提取标签（如果有）
        tags = conversation.pop('tags', [])
        
        # 使用DatabaseManager的add_conversation方法
        conv_id = self.db.add_conversation(
            source_url=conversation['source_url'],
            platform=conversation['platform'],
            title=conversation['title'],
            raw_content=conversation['raw_content'],
            summary=conversation.get('summary'),
            category=conversation.get('category'),
            tags=tags
        )
        
        return str(conv_id)
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个对话
        
        Args:
            conv_id: 对话ID
        
        Returns:
            对话数据字典，如果不存在返回None
        """
        try:
            conversation = self.db.get_conversation(int(conv_id))
            if conversation:
                # 转换为字典
                return dict(conversation)
            return None
        except (ValueError, TypeError):
            # 无效的ID格式
            return None
    
    def update_conversation(self, conv_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新对话
        
        Args:
            conv_id: 对话ID
            updates: 更新的字段
        
        Returns:
            是否成功
        """
        try:
            cursor = self.conn.cursor()
            
            # 构建SET子句
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == 'tags':
                    continue  # 标签单独处理
                set_clauses.append(f"{key} = ?")
                if isinstance(value, (dict, list)):
                    values.append(json.dumps(value, ensure_ascii=False))
                else:
                    values.append(value)
            
            if set_clauses:
                values.append(int(conv_id))
                sql = f"UPDATE conversations SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(sql, values)
            
            # 处理标签
            if 'tags' in updates:
                self._update_tags(int(conv_id), updates['tags'])
            
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"Update failed: {e}")
            return False
    
    def delete_conversation(self, conv_id: str) -> bool:
        """
        删除对话
        
        Args:
            conv_id: 对话ID
        
        Returns:
            是否成功
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (int(conv_id),))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    
    def search_conversations(self, 
                            query: str,
                            filters: Optional[Dict[str, Any]] = None,
                            limit: int = 10,
                            offset: int = 0) -> List[Dict[str, Any]]:
        """
        搜索对话
        
        Args:
            query: 搜索关键词
            filters: 过滤条件
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            搜索结果列表
        """
        results = self.db.search_conversations(query, limit=limit)
        return [dict(r) for r in results]
    
    def list_conversations(self,
                          filters: Optional[Dict[str, Any]] = None,
                          limit: int = 100,
                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            filters: 过滤条件
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            对话列表
        """
        conversations = self.db.get_all_conversations(limit=limit)
        return [dict(c) for c in conversations]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return self.db.get_statistics()
    
    def batch_add(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加对话
        
        Args:
            conversations: 对话列表
        
        Returns:
            添加的对话ID列表
        """
        ids = []
        for conv in conversations:
            try:
                conv_id = self.add_conversation(conv)
                ids.append(conv_id)
            except Exception as e:
                print(f"Failed to add conversation: {e}")
                ids.append(None)
        return ids
    
    def close(self):
        """关闭连接"""
        if self.db and self.db.conn:
            self.db.close()
    
    # 实现BaseStorage的其他抽象方法
    
    def connect(self) -> bool:
        """连接到数据库（SQLite自动连接）"""
        return self.conn is not None
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.conn is not None
    
    def get_conversation_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """根据URL获取对话"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE source_url = ?", (url,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_conversation_tags(self, conv_id: str) -> List[str]:
        """获取对话标签"""
        return self.db.get_conversation_tags(int(conv_id))
    
    def add_tags(self, conv_id: str, tags: List[str]) -> bool:
        """添加标签到对话"""
        try:
            self._update_tags(int(conv_id), tags)
            return True
        except Exception as e:
            print(f"Add tags failed: {e}")
            return False
    
    def remove_tags(self, conv_id: str, tags: List[str]) -> bool:
        """从对话移除标签"""
        try:
            cursor = self.conn.cursor()
            for tag_name in tags:
                cursor.execute("""
                    DELETE FROM conversation_tags
                    WHERE conversation_id = ?
                    AND tag_id = (SELECT id FROM tags WHERE name = ?)
                """, (int(conv_id), tag_name))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Remove tags failed: {e}")
            return False
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY usage_count DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def advanced_search(self, 
                       query: str,
                       filters: Optional[Dict[str, Any]] = None,
                       sort_by: str = "relevance",
                       limit: int = 10) -> List[Dict[str, Any]]:
        """高级搜索（使用FTS5）"""
        return self.search_conversations(query, filters, limit)
    
    def backup(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def optimize(self) -> bool:
        """优化数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Optimize failed: {e}")
            return False
    
    def export_data(self, export_path: str, format: str = "json") -> bool:
        """导出数据"""
        try:
            import json as json_mod
            conversations = self.list_conversations(limit=10000)
            
            if format == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json_mod.dump(conversations, f, ensure_ascii=False, indent=2)
                return True
            else:
                print(f"Unsupported format: {format}")
                return False
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_data(self, import_path: str, format: str = "json") -> bool:
        """导入数据"""
        try:
            import json as json_mod
            
            if format == "json":
                with open(import_path, 'r', encoding='utf-8') as f:
                    conversations = json_mod.load(f)
                
                for conv in conversations:
                    try:
                        self.add_conversation(conv)
                    except Exception as e:
                        print(f"Failed to import conversation: {e}")
                return True
            else:
                print(f"Unsupported format: {format}")
                return False
        except Exception as e:
            print(f"Import failed: {e}")
            return False
    
    def _update_tags(self, conv_id: int, tags: List[str]):
        """更新对话标签"""
        cursor = self.conn.cursor()
        
        # 删除现有标签关联
        cursor.execute("DELETE FROM conversation_tags WHERE conversation_id = ?", (conv_id,))
        
        # 添加新标签
        for tag_name in tags:
            # 确保标签存在
            cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (tag_name,)
            )
            
            # 获取标签ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]
            
            # 创建关联
            cursor.execute(
                "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id) VALUES (?, ?)",
                (conv_id, tag_id)
            )
        
        self.conn.commit()
    
    def __repr__(self):
        return f"<SQLiteManager db_path='{self.db_path}'>"
