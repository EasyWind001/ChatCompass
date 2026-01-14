"""
数据库健康检查工具

快速检查SQLite和Elasticsearch的健康状态。

使用方法:
    python -m database.health_check
    python -m database.health_check --storage elasticsearch

作者: ChatCompass Team  
版本: v1.2.2
"""

import argparse
import sys
import os
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def check_sqlite(db_path: str = None) -> Dict[str, Any]:
    """检查SQLite健康状态"""
    try:
        import sqlite3
        from pathlib import Path
        
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', './data/chatcompass.db')
        
        if not Path(db_path).exists():
            return {
                'status': 'error',
                'message': f'数据库文件不存在: {db_path}'
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # 统计数据
        stats = {}
        if 'conversations' in tables:
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats['conversations'] = cursor.fetchone()[0]
        
        if 'messages' in tables:
            cursor.execute("SELECT COUNT(*) FROM messages")
            stats['messages'] = cursor.fetchone()[0]
        
        if 'tags' in tables:
            cursor.execute("SELECT COUNT(*) FROM tags")
            stats['tags'] = cursor.fetchone()[0]
        
        # 检查FTS
        fts_tables = [t for t in tables if 'fts' in t.lower()]
        
        conn.close()
        
        return {
            'status': 'healthy',
            'type': 'SQLite',
            'database_path': db_path,
            'tables': tables,
            'fts_enabled': len(fts_tables) > 0,
            'statistics': stats
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'type': 'SQLite',
            'error': str(e)
        }


def check_elasticsearch(host: str = None, port: int = None) -> Dict[str, Any]:
    """检查Elasticsearch健康状态"""
    try:
        from database.es_manager import ElasticsearchManager
        
        if host is None:
            host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        if port is None:
            port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
        
        mgr = ElasticsearchManager(
            host=host,
            port=port,
            index_prefix='chatcompass'
        )
        
        health = mgr.health_check()
        mgr.close()
        
        return {
            'status': 'healthy' if health['status'] in ['green', 'yellow'] else 'warning',
            'type': 'Elasticsearch',
            'host': f'{host}:{port}',
            'cluster_name': health.get('cluster_name', 'N/A'),
            'cluster_status': health.get('status', 'unknown'),
            'nodes': health.get('number_of_nodes', 0),
            'active_shards': health.get('active_shards', 0),
            'statistics': health.get('indices', {})
        }
        
    except ImportError:
        return {
            'status': 'error',
            'type': 'Elasticsearch',
            'error': 'Elasticsearch依赖未安装 (pip install elasticsearch)'
        }
    except Exception as e:
        return {
            'status': 'error',
            'type': 'Elasticsearch',
            'error': str(e)
        }


def print_health_report(result: Dict[str, Any]):
    """打印健康检查报告"""
    storage_type = result.get('type', 'Unknown')
    status = result.get('status', 'unknown')
    
    # 状态图标
    status_icon = {
        'healthy': '✅',
        'warning': '⚠️',
        'error': '❌'
    }.get(status, '❓')
    
    print("\n" + "=" * 60)
    print(f"{status_icon} {storage_type} 健康检查")
    print("=" * 60)
    
    if status == 'error':
        print(f"\n❌ 状态: 错误")
        print(f"📝 错误信息: {result.get('error', '未知错误')}")
        if 'message' in result:
            print(f"💡 提示: {result['message']}")
    
    elif status == 'warning':
        print(f"\n⚠️ 状态: 警告")
        print(f"📋 详情: {result.get('cluster_status', 'N/A')}")
    
    else:
        print(f"\n✅ 状态: 健康")
    
    # SQLite详情
    if storage_type == 'SQLite' and status == 'healthy':
        print(f"\n📁 数据库路径: {result.get('database_path', 'N/A')}")
        print(f"🔍 FTS搜索: {'启用' if result.get('fts_enabled') else '未启用'}")
        
        if 'tables' in result:
            print(f"\n📊 数据表: {len(result['tables'])}个")
            for table in result['tables']:
                print(f"   - {table}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\n📈 数据统计:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
    
    # Elasticsearch详情
    elif storage_type == 'Elasticsearch' and status in ['healthy', 'warning']:
        print(f"\n🌐 连接地址: {result.get('host', 'N/A')}")
        print(f"🏷️  集群名称: {result.get('cluster_name', 'N/A')}")
        print(f"📊 集群状态: {result.get('cluster_status', 'unknown')}")
        print(f"🖥️  节点数量: {result.get('nodes', 0)}")
        print(f"📦 活跃分片: {result.get('active_shards', 0)}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\n📈 索引统计:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="ChatCompass数据库健康检查工具"
    )
    
    parser.add_argument(
        '--storage',
        type=str,
        choices=['sqlite', 'elasticsearch', 'all'],
        default='all',
        help='检查的存储类型 (默认: all)'
    )
    
    parser.add_argument(
        '--sqlite-path',
        type=str,
        help='SQLite数据库路径'
    )
    
    parser.add_argument(
        '--es-host',
        type=str,
        help='Elasticsearch主机地址'
    )
    
    parser.add_argument(
        '--es-port',
        type=int,
        help='Elasticsearch端口'
    )
    
    args = parser.parse_args()
    
    all_healthy = True
    
    # 检查SQLite
    if args.storage in ['sqlite', 'all']:
        result = check_sqlite(args.sqlite_path)
        print_health_report(result)
        
        if result['status'] != 'healthy':
            all_healthy = False
    
    # 检查Elasticsearch
    if args.storage in ['elasticsearch', 'all']:
        result = check_elasticsearch(args.es_host, args.es_port)
        print_health_report(result)
        
        if result['status'] == 'error':
            all_healthy = False
    
    # 返回状态码
    sys.exit(0 if all_healthy else 1)


if __name__ == '__main__':
    main()
