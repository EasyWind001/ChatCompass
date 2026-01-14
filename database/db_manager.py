"""
数据库管理器
处理所有数据库操作
"""
import sqlite3
import json
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "chatcompass.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库（创建表）"""
        # 确保数据库目录存在
        db_dir = Path(self.db_path).parent
        if db_dir and not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        
        # 读取并执行schema.sql
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                self.conn.executescript(schema_sql)
        else:
            # 如果schema.sql不存在，使用内联SQL
            self._create_tables_inline()
        
        self.conn.commit()
        print(f"[数据库] 初始化完成: {self.db_path}")
    
    def _create_tables_inline(self):
        """内联创建表（备用方案）"""
        cursor = self.conn.cursor()
        
        # 创建conversations表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                raw_content TEXT NOT NULL,
                summary TEXT,
                category TEXT,
                word_count INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_favorite INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        # 创建tags表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#3B82F6',
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_tags (
                conversation_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (conversation_id, tag_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        # 创建FTS5虚拟表
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
                title, summary, raw_content,
                content='conversations',
                content_rowid='id'
            )
        """)
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    # ==================== 对话操作 ====================
    
    def add_conversation(self, 
                        source_url: str,
                        platform: str,
                        title: str,
                        raw_content: dict,
                        summary: str = None,
                        category: str = None,
                        tags: List[str] = None) -> int:
        """
        添加新对话
        
        Returns:
            新对话的ID
        """
        cursor = self.conn.cursor()
        
        # 将raw_content转为JSON字符串
        content_json = json.dumps(raw_content, ensure_ascii=False)
        
        # 计算统计信息
        word_count = len(content_json)
        message_count = len(raw_content.get('messages', []))
        
        try:
            cursor.execute("""
                INSERT INTO conversations 
                (source_url, platform, title, raw_content, summary, category, word_count, message_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (source_url, platform, title, content_json, summary, category, word_count, message_count))
            
            conversation_id = cursor.lastrowid
            
            # 添加标签
            if tags:
                self._add_tags_to_conversation(conversation_id, tags)
            
            self.conn.commit()
            print(f"[数据库] 添加对话成功: ID={conversation_id}, 标题={title}")
            return conversation_id
            
        except sqlite3.IntegrityError:
            # URL已存在
            print(f"[数据库] 对话已存在: {source_url}")
            # 返回已存在的ID
            cursor.execute("SELECT id FROM conversations WHERE source_url = ?", (source_url,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """获取单个对话详情"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversations WHERE id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # 转换为字典
        conversation = dict(row)
        
        # 解析JSON
        conversation['raw_content'] = json.loads(conversation['raw_content'])
        
        # 获取标签
        conversation['tags'] = self.get_conversation_tags(conversation_id)
        
        return conversation
    
    def get_all_conversations(self, 
                             limit: int = 100, 
                             offset: int = 0,
                             category: str = None,
                             platform: str = None,
                             is_favorite: bool = None) -> List[Dict]:
        """
        获取对话列表
        
        Args:
            limit: 返回数量
            offset: 偏移量
            category: 按分类筛选
            platform: 按平台筛选
            is_favorite: 是否只显示收藏
        """
        cursor = self.conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM conversations WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if is_favorite is not None:
            query += " AND is_favorite = ?"
            params.append(1 if is_favorite else 0)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conv = dict(row)
            # 不解析完整内容（节省内存）
            conv['tags'] = self.get_conversation_tags(conv['id'])
            conversations.append(conv)
        
        return conversations
    
    def update_conversation(self, conversation_id: int, **kwargs):
        """更新对话信息"""
        # 白名单：仅允许更新这些字段
        allowed_fields = ['title', 'summary', 'category', 'notes', 'is_favorite']
        
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                # 字段名已通过白名单验证，安全拼接
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return
        
        params.append(conversation_id)
        
        cursor = self.conn.cursor()
        # 字段名通过白名单验证后拼接，参数使用占位符绑定
        sql = f"""
            UPDATE conversations 
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        cursor.execute(sql, params)
        
        self.conn.commit()
    
    def delete_conversation(self, conversation_id: int):
        """删除对话"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self.conn.commit()
        print(f"[数据库] 删除对话: ID={conversation_id}")
    
    # ==================== 标签操作 ====================
    
    def add_tag(self, name: str, color: str = '#3B82F6') -> int:
        """添加标签"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tags (name, color) VALUES (?, ?)
            """, (name, color))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # 标签已存在，返回已有ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_tag_id(self, name: str) -> Optional[int]:
        """获取标签ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_all_tags(self) -> List[Dict]:
        """获取所有标签"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY usage_count DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def _add_tags_to_conversation(self, conversation_id: int, tags: List[str]):
        """为对话添加标签"""
        cursor = self.conn.cursor()
        
        for tag_name in tags:
            # 确保标签存在
            tag_id = self.add_tag(tag_name)
            
            if tag_id:
                try:
                    # 添加关联
                    cursor.execute("""
                        INSERT INTO conversation_tags (conversation_id, tag_id)
                        VALUES (?, ?)
                    """, (conversation_id, tag_id))
                    
                    # 更新使用次数
                    cursor.execute("""
                        UPDATE tags SET usage_count = usage_count + 1
                        WHERE id = ?
                    """, (tag_id,))
                except sqlite3.IntegrityError:
                    # 关联已存在
                    pass
        
        self.conn.commit()
    
    def get_conversation_tags(self, conversation_id: int) -> List[str]:
        """获取对话的所有标签"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.name FROM tags t
            JOIN conversation_tags ct ON t.id = ct.tag_id
            WHERE ct.conversation_id = ?
        """, (conversation_id,))
        
        return [row[0] for row in cursor.fetchall()]
    
    # ==================== 全文搜索 ====================
    
    def search_conversations(self, 
                            keyword: str, 
                            limit: int = 50,
                            context_size: int = 100) -> List[Dict]:
        """
        全文搜索对话（增强版：带上下文定位）
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            context_size: 片段上下文字符数
        
        Returns:
            搜索结果列表，包含高亮片段和上下文
        """
        cursor = self.conn.cursor()
        
        # 先尝试FTS5搜索（使用通配符）
        try:
            # 为每个词添加通配符
            search_terms = keyword.split()
            fts_query = ' '.join([f'{term}*' for term in search_terms])
            
            cursor.execute("""
                SELECT 
                    c.id, c.title, c.summary, c.source_url, c.platform, 
                    c.category, c.created_at, c.raw_content,
                    snippet(conversations_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
                FROM conversations_fts
                JOIN conversations c ON conversations_fts.rowid = c.id
                WHERE conversations_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, limit))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['tags'] = self.get_conversation_tags(result['id'])
                
                # 增强：提取匹配片段的上下文
                result['matches'] = self._extract_context_matches(
                    result['raw_content'], 
                    keyword, 
                    context_size
                )
                
                results.append(result)
            
            # 如果FTS找到结果，直接返回
            if results:
                return results
        except Exception as e:
            print(f"[搜索] FTS搜索失败: {e}")
        
        # FTS没有结果，回退到LIKE搜索
        print(f"[搜索] 使用LIKE模糊搜索")
        cursor.execute("""
            SELECT 
                id, title, summary, source_url, platform, 
                category, created_at, raw_content,
                substr(raw_content, 1, 200) as snippet
            FROM conversations
            WHERE title LIKE ? OR summary LIKE ? OR raw_content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            result['tags'] = self.get_conversation_tags(result['id'])
            
            # 增强：提取匹配片段的上下文
            result['matches'] = self._extract_context_matches(
                result['raw_content'], 
                keyword, 
                context_size
            )
            
            results.append(result)
        
        return results
    
    def _extract_context_matches(self, 
                                 raw_content: str, 
                                 keyword: str, 
                                 context_size: int = 100) -> List[Dict]:
        """
        从对话内容中提取匹配片段及其上下文
        
        Args:
            raw_content: 对话原始内容（JSON字符串或字典）
            keyword: 搜索关键词
            context_size: 上下文字符数
        
        Returns:
            匹配片段列表，每个片段包含：
            - role: 消息角色（user/assistant）
            - message_index: 消息序号
            - match_text: 匹配的文本（高亮）
            - before_context: 前文
            - after_context: 后文
            - position: 在对话中的位置（第几条消息）
        """
        matches = []
        
        try:
            # 解析内容
            if isinstance(raw_content, str):
                content = json.loads(raw_content)
            else:
                content = raw_content
            
            messages = content.get('messages', [])
            keyword_lower = keyword.lower()
            
            # 遍历每条消息
            for msg_idx, message in enumerate(messages, 1):
                role = message.get('role', 'unknown')
                content_text = message.get('content', '')
                content_lower = content_text.lower()
                
                # 查找所有匹配位置
                start = 0
                while True:
                    pos = content_lower.find(keyword_lower, start)
                    if pos == -1:
                        break
                    
                    # 计算上下文范围
                    before_start = max(0, pos - context_size)
                    after_end = min(len(content_text), pos + len(keyword) + context_size)
                    
                    # 提取上下文
                    before = content_text[before_start:pos]
                    match = content_text[pos:pos + len(keyword)]
                    after = content_text[pos + len(keyword):after_end]
                    
                    # 添加省略号
                    if before_start > 0:
                        before = '...' + before
                    if after_end < len(content_text):
                        after = after + '...'
                    
                    matches.append({
                        'role': role,
                        'message_index': msg_idx,
                        'total_messages': len(messages),
                        'match_text': match,
                        'before_context': before,
                        'after_context': after,
                        'full_message': content_text  # 保留完整消息以便需要时显示
                    })
                    
                    start = pos + 1  # 继续查找下一个匹配
                    
                    # 限制每条消息最多3个匹配
                    if len([m for m in matches if m['message_index'] == msg_idx]) >= 3:
                        break
            
        except Exception as e:
            print(f"[搜索] 提取上下文失败: {e}")
        
        return matches
    
    # ==================== 统计信息 ====================
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 总对话数
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats['total_conversations'] = cursor.fetchone()[0]
        
        # 按平台统计
        cursor.execute("""
            SELECT platform, COUNT(*) as count 
            FROM conversations 
            GROUP BY platform
        """)
        stats['by_platform'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 按分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM conversations 
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 总标签数
        cursor.execute("SELECT COUNT(*) FROM tags")
        stats['total_tags'] = cursor.fetchone()[0]
        
        return stats


# 使用示例
if __name__ == '__main__':
    db = DatabaseManager("test.db")
    
    # 添加测试对话
    conversation_data = {
        'messages': [
            {'role': 'user', 'content': '你好'},
            {'role': 'assistant', 'content': '你好！有什么可以帮助你的吗？'}
        ]
    }
    
    conv_id = db.add_conversation(
        source_url="https://chatgpt.com/share/test123",
        platform="chatgpt",
        title="测试对话",
        raw_content=conversation_data,
        summary="这是一个测试对话",
        category="其他",
        tags=["测试", "示例"]
    )
    
    print(f"添加对话ID: {conv_id}")
    
    # 搜索
    results = db.search_conversations("测试")
    print(f"搜索结果: {len(results)}条")
    
    # 统计
    stats = db.get_statistics()
    print(f"统计信息: {stats}")
    
    db.close()
