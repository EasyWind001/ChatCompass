"""
SQLite到Elasticsearch数据迁移工具

提供命令行工具用于将现有SQLite数据迁移到Elasticsearch。
支持增量迁移、数据验证和回滚。

使用方法:
    python -m database.migrate_to_es --source ./data/chatcompass.db --validate

作者: ChatCompass Team
版本: v1.2.2
"""

import argparse
import sys
import sqlite3
import logging
from typing import Tuple, Dict, Any
from pathlib import Path
from datetime import datetime
from .es_manager import ElasticsearchManager
from .sqlite_manager import SQLiteManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self, sqlite_path: str, es_host: str = "localhost",
                 es_port: int = 9200, index_prefix: str = "chatcompass"):
        """
        初始化迁移器
        
        Args:
            sqlite_path: SQLite数据库路径
            es_host: Elasticsearch主机
            es_port: Elasticsearch端口
            index_prefix: ES索引前缀
        """
        self.sqlite_path = sqlite_path
        
        # 检查SQLite文件是否存在
        if not Path(sqlite_path).exists():
            raise FileNotFoundError(f"SQLite数据库文件不存在: {sqlite_path}")
        
        # 初始化管理器
        try:
            self.sqlite_mgr = SQLiteManager(sqlite_path)
            self.es_mgr = ElasticsearchManager(
                host=es_host,
                port=es_port,
                index_prefix=index_prefix
            )
            logger.info("✅ 数据库连接初始化成功")
        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            raise
    
    def migrate_all(self, validate: bool = True) -> Dict[str, Any]:
        """
        执行完整数据迁移
        
        Args:
            validate: 是否在迁移后验证数据
        
        Returns:
            迁移统计信息
        """
        logger.info("=" * 60)
        logger.info("开始数据迁移: SQLite → Elasticsearch")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        stats = {
            'start_time': start_time.isoformat(),
            'conversations': 0,
            'messages': 0,
            'tags': 0,
            'errors': []
        }
        
        try:
            # 1. 迁移标签
            logger.info("\n📋 Step 1/3: 迁移标签...")
            stats['tags'] = self._migrate_tags()
            logger.info(f"✅ 标签迁移完成: {stats['tags']}个")
            
            # 2. 迁移对话
            logger.info("\n💬 Step 2/3: 迁移对话...")
            stats['conversations'] = self._migrate_conversations()
            logger.info(f"✅ 对话迁移完成: {stats['conversations']}个")
            
            # 3. 迁移消息
            logger.info("\n📨 Step 3/3: 迁移消息...")
            stats['messages'] = self._migrate_messages()
            logger.info(f"✅ 消息迁移完成: {stats['messages']}条")
            
            # 验证数据
            if validate:
                logger.info("\n🔍 验证数据完整性...")
                validation_result = self.validate_migration()
                stats['validation'] = validation_result
                
                if validation_result['status'] == 'success':
                    logger.info("✅ 数据验证通过")
                else:
                    logger.warning(f"⚠️ 数据验证警告: {validation_result['message']}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            stats['end_time'] = end_time.isoformat()
            stats['duration_seconds'] = duration
            stats['status'] = 'success'
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ 数据迁移完成！")
            logger.info(f"⏱️  总耗时: {duration:.2f}秒")
            logger.info(f"📊 迁移统计:")
            logger.info(f"   - 对话: {stats['conversations']}个")
            logger.info(f"   - 消息: {stats['messages']}条")
            logger.info(f"   - 标签: {stats['tags']}个")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 迁移失败: {e}")
            stats['status'] = 'failed'
            stats['error'] = str(e)
            return stats
    
    def _migrate_tags(self) -> int:
        """迁移标签"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tags")
            tags = cursor.fetchall()
            
            count = 0
            for tag in tags:
                tag_dict = {
                    'tag_id': tag['tag_id'],
                    'name': tag['name'],
                    'color': tag.get('color', '#3b82f6'),
                    'description': tag.get('description', '')
                }
                
                if self.es_mgr.save_tag(**tag_dict):
                    count += 1
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"❌ 标签迁移失败: {e}")
            return 0
    
    def _migrate_conversations(self) -> int:
        """迁移对话"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取对话及其标签
            cursor.execute("""
                SELECT c.*, GROUP_CONCAT(ct.tag_id) as tag_ids
                FROM conversations c
                LEFT JOIN conversation_tags ct ON c.conversation_id = ct.conversation_id
                GROUP BY c.conversation_id
            """)
            conversations = cursor.fetchall()
            
            count = 0
            for conv in conversations:
                conv_dict = {
                    'conversation_id': conv['conversation_id'],
                    'title': conv['title'],
                    'platform': conv['platform'],
                    'create_time': conv['create_time'],
                    'message_count': conv.get('message_count', 0),
                    'total_tokens': conv.get('total_tokens', 0),
                    'model': conv.get('model', ''),
                    'summary': conv.get('summary', ''),
                    'category': conv.get('category', ''),
                    'tags': conv['tag_ids'].split(',') if conv['tag_ids'] else []
                }
                
                if self.es_mgr.save_conversation(**conv_dict):
                    count += 1
                    
                    if count % 100 == 0:
                        logger.info(f"   已迁移: {count}个对话...")
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"❌ 对话迁移失败: {e}")
            return 0
    
    def _migrate_messages(self) -> int:
        """迁移消息（批量）"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM messages")
            total = cursor.fetchone()['total']
            logger.info(f"   总消息数: {total}条")
            
            # 分批迁移，每批1000条
            batch_size = 1000
            offset = 0
            total_migrated = 0
            
            while True:
                cursor.execute(f"""
                    SELECT * FROM messages
                    ORDER BY conversation_id, order_index
                    LIMIT {batch_size} OFFSET {offset}
                """)
                messages = cursor.fetchall()
                
                if not messages:
                    break
                
                # 准备批量数据
                batch_data = []
                for msg in messages:
                    msg_dict = {
                        'message_id': msg['message_id'],
                        'conversation_id': msg['conversation_id'],
                        'role': msg['role'],
                        'content': msg['content'],
                        'create_time': msg['create_time'],
                        'order_index': msg.get('order_index', 0),
                        'parent_message_id': msg.get('parent_message_id', ''),
                        'tokens': msg.get('tokens', 0)
                    }
                    batch_data.append(msg_dict)
                
                # 批量保存
                migrated = self.es_mgr.bulk_save_messages(batch_data)
                total_migrated += migrated
                
                logger.info(f"   进度: {total_migrated}/{total} ({total_migrated*100//total}%)")
                
                offset += batch_size
            
            conn.close()
            return total_migrated
            
        except Exception as e:
            logger.error(f"❌ 消息迁移失败: {e}")
            return 0
    
    def validate_migration(self) -> Dict[str, Any]:
        """验证迁移数据的完整性"""
        try:
            # 获取SQLite统计
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            sqlite_conv_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            sqlite_msg_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tags")
            sqlite_tag_count = cursor.fetchone()[0]
            
            conn.close()
            
            # 获取ES统计
            es_stats = self.es_mgr.get_statistics()
            
            # 对比数据
            conv_match = sqlite_conv_count == es_stats.get('total_conversations', 0)
            msg_match = sqlite_msg_count == es_stats.get('total_messages', 0)
            tag_match = sqlite_tag_count == es_stats.get('total_tags', 0)
            
            all_match = conv_match and msg_match and tag_match
            
            result = {
                'status': 'success' if all_match else 'mismatch',
                'sqlite': {
                    'conversations': sqlite_conv_count,
                    'messages': sqlite_msg_count,
                    'tags': sqlite_tag_count
                },
                'elasticsearch': {
                    'conversations': es_stats.get('total_conversations', 0),
                    'messages': es_stats.get('total_messages', 0),
                    'tags': es_stats.get('total_tags', 0)
                },
                'match': {
                    'conversations': conv_match,
                    'messages': msg_match,
                    'tags': tag_match
                }
            }
            
            if not all_match:
                mismatches = []
                if not conv_match:
                    mismatches.append('对话数量不匹配')
                if not msg_match:
                    mismatches.append('消息数量不匹配')
                if not tag_match:
                    mismatches.append('标签数量不匹配')
                result['message'] = ', '.join(mismatches)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 验证失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def incremental_migrate(self, since: str) -> Dict[str, Any]:
        """
        增量迁移（迁移指定时间后的数据）
        
        Args:
            since: 起始时间 (ISO格式)
        """
        logger.info(f"开始增量迁移: since {since}")
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 增量迁移对话
            cursor.execute("""
                SELECT * FROM conversations
                WHERE update_time >= ?
                ORDER BY update_time
            """, (since,))
            conversations = cursor.fetchall()
            
            conv_count = 0
            for conv in conversations:
                conv_dict = dict(conv)
                if self.es_mgr.save_conversation(**conv_dict):
                    conv_count += 1
            
            # 增量迁移消息
            cursor.execute("""
                SELECT m.* FROM messages m
                JOIN conversations c ON m.conversation_id = c.conversation_id
                WHERE c.update_time >= ?
                ORDER BY m.create_time
            """, (since,))
            messages = cursor.fetchall()
            
            msg_list = [dict(msg) for msg in messages]
            msg_count = self.es_mgr.bulk_save_messages(msg_list)
            
            conn.close()
            
            logger.info(f"✅ 增量迁移完成: {conv_count}个对话, {msg_count}条消息")
            
            return {
                'status': 'success',
                'conversations': conv_count,
                'messages': msg_count,
                'since': since
            }
            
        except Exception as e:
            logger.error(f"❌ 增量迁移失败: {e}")
            return {'status': 'error', 'error': str(e)}


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="ChatCompass数据迁移工具: SQLite → Elasticsearch"
    )
    
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='SQLite数据库路径'
    )
    
    parser.add_argument(
        '--es-host',
        type=str,
        default='localhost',
        help='Elasticsearch主机地址 (默认: localhost)'
    )
    
    parser.add_argument(
        '--es-port',
        type=int,
        default=9200,
        help='Elasticsearch端口 (默认: 9200)'
    )
    
    parser.add_argument(
        '--index-prefix',
        type=str,
        default='chatcompass',
        help='ES索引前缀 (默认: chatcompass)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='迁移后验证数据完整性'
    )
    
    parser.add_argument(
        '--incremental',
        type=str,
        help='增量迁移: 仅迁移此时间后的数据 (ISO格式: 2024-01-01T00:00:00)'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建迁移器
        migrator = DataMigrator(
            sqlite_path=args.source,
            es_host=args.es_host,
            es_port=args.es_port,
            index_prefix=args.index_prefix
        )
        
        # 执行迁移
        if args.incremental:
            result = migrator.incremental_migrate(args.incremental)
        else:
            result = migrator.migrate_all(validate=args.validate)
        
        # 输出结果
        if result['status'] == 'success':
            logger.info("\n✅ 迁移成功完成！")
            sys.exit(0)
        else:
            logger.error(f"\n❌ 迁移失败: {result.get('error', '未知错误')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ 程序错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
