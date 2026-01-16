"""
Elasticsearch数据库管理器

实现基于Elasticsearch的数据存储和搜索功能。
支持中文分词、全文搜索、向量搜索等高级功能。

作者: ChatCompass Team
版本: v1.2.2
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError, ConnectionError as ESConnectionError
import logging
import os
from .base_storage import BaseStorage

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticsearchManager(BaseStorage):
    """Elasticsearch存储实现"""

    def __init__(self, host: str = "localhost", port: int = 9200,
                 index_prefix: str = "chatcompass",
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        初始化Elasticsearch连接
        
        Args:
            host: ES主机地址
            port: ES端口
            index_prefix: 索引名称前缀
            username: 用户名（可选）
            password: 密码（可选）
        """
        # 构建连接配置
        es_config = {
            'hosts': [f'{host}:{port}'],
            'retry_on_timeout': True,
            'max_retries': 3,
            'timeout': 30
        }
        
        # 添加认证信息
        if username and password:
            es_config['http_auth'] = (username, password)
        
        try:
            self.es = Elasticsearch(**es_config)
            
            # 检查连接
            if not self.es.ping():
                raise ESConnectionError("无法连接到Elasticsearch")
            
            logger.info(f"✅ 成功连接到Elasticsearch {host}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Elasticsearch连接失败: {e}")
            raise
        
        self.index_prefix = index_prefix
        self.conversation_index = f"{index_prefix}_conversations"
        self.message_index = f"{index_prefix}_messages"
        self.tag_index = f"{index_prefix}_tags"
        
        # 初始化索引
        self._create_indices()
    
    def _create_indices(self):
        """创建Elasticsearch索引和映射"""
        
        # Conversations索引映射（使用标准分析器，不依赖IK插件）
        conversation_mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "conversation_id": {"type": "keyword"},
                    "source_url": {"type": "keyword"},  # 添加source_url字段
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "platform": {"type": "keyword"},
                    "create_time": {"type": "date"},
                    "update_time": {"type": "date"},
                    "message_count": {"type": "integer"},
                    "total_tokens": {"type": "integer"},
                    "model": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "summary": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "category": {"type": "keyword"},
                    "raw_content": {
                        "type": "text",
                        "index": False  # 不索引，只存储原始内容
                    }
                }
            }
        }
        
        # Messages索引映射（使用标准分析器）
        message_mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "message_id": {"type": "keyword"},
                    "conversation_id": {"type": "keyword"},
                    "role": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "create_time": {"type": "date"},
                    "order_index": {"type": "integer"},
                    "parent_message_id": {"type": "keyword"},
                    "tokens": {"type": "integer"}
                }
            }
        }
        
        # Tags索引映射
        tag_mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "tag_id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "color": {"type": "keyword"},
                    "description": {"type": "text"},
                    "create_time": {"type": "date"}
                }
            }
        }
        
        # 创建索引
        for index_name, mapping in [
            (self.conversation_index, conversation_mapping),
            (self.message_index, message_mapping),
            (self.tag_index, tag_mapping)
        ]:
            try:
                if not self.es.indices.exists(index=index_name):
                    self.es.indices.create(index=index_name, body=mapping)
                    logger.info(f"✅ 创建索引: {index_name}")
                else:
                    logger.info(f"📋 索引已存在: {index_name}")
            except Exception as e:
                logger.error(f"❌ 创建索引失败 {index_name}: {e}")
                raise
    
    # ==================== 对话管理 ====================
    
    def save_conversation(self, conversation_id: str, title: str, 
                         platform: str = "chatgpt",
                         source_url: Optional[str] = None,
                         raw_content: Optional[str] = None,
                         create_time: Optional[str] = None,
                         **kwargs) -> bool:
        """保存对话"""
        try:
            doc = {
                "conversation_id": conversation_id,
                "source_url": source_url or "",  # 添加source_url
                "raw_content": raw_content or "",  # 添加raw_content
                "title": title,
                "platform": platform,
                "create_time": create_time or datetime.now().isoformat(),
                "update_time": datetime.now().isoformat(),
                "message_count": kwargs.get("message_count", 0),
                "total_tokens": kwargs.get("total_tokens", 0),
                "model": kwargs.get("model", ""),
                "tags": kwargs.get("tags", []),
                "summary": kwargs.get("summary", ""),
                "category": kwargs.get("category", "")
            }
            
            self.es.index(
                index=self.conversation_index,
                id=conversation_id,
                body=doc,
                refresh=True
            )
            
            logger.info(f"✅ 保存对话: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存对话失败: {e}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """获取对话详情"""
        try:
            result = self.es.get(index=self.conversation_index, id=conversation_id)
            conversation = result['_source']
            conversation['id'] = result['_id']  # 添加ID字段
            
            # 统一字段名
            if 'create_time' in conversation and 'created_at' not in conversation:
                conversation['created_at'] = conversation['create_time']
            if 'update_time' in conversation and 'updated_at' not in conversation:
                conversation['updated_at'] = conversation['update_time']
            
            return conversation
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"❌ 获取对话失败: {e}")
            return None
    
    def list_conversations(self, platform: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          limit: int = 50,
                          offset: int = 0,
                          sort_by: str = "update_time",
                          order: str = "desc") -> List[Dict]:
        """列出对话"""
        try:
            query = {"bool": {"must": []}}
            
            if platform:
                query["bool"]["must"].append({"term": {"platform": platform}})
            
            if tags:
                query["bool"]["must"].append({"terms": {"tags": tags}})
            
            # 如果没有任何条件，使用match_all
            if not query["bool"]["must"]:
                query = {"match_all": {}}
            
            result = self.es.search(
                index=self.conversation_index,
                body={
                    "query": query,
                    "sort": [{sort_by: {"order": order}}],
                    "from": offset,
                    "size": limit
                }
            )
            
            # 返回时包含文档ID，并统一字段名
            conversations = []
            for hit in result['hits']['hits']:
                conversation = hit['_source']
                conversation['id'] = hit['_id']  # 添加ID字段
                
                # 统一字段名：Elasticsearch使用create_time，但主程序期望created_at
                if 'create_time' in conversation and 'created_at' not in conversation:
                    conversation['created_at'] = conversation['create_time']
                if 'update_time' in conversation and 'updated_at' not in conversation:
                    conversation['updated_at'] = conversation['update_time']
                
                conversations.append(conversation)
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ 列出对话失败: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        try:
            # 删除对话
            self.es.delete(index=self.conversation_index, id=conversation_id, refresh=True)
            
            # 删除相关消息
            self.es.delete_by_query(
                index=self.message_index,
                body={"query": {"term": {"conversation_id": conversation_id}}},
                refresh=True
            )
            
            logger.info(f"✅ 删除对话: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除对话失败: {e}")
            return False
    
    def update_conversation(self, conversation_id: str, **kwargs) -> bool:
        """更新对话信息"""
        try:
            update_doc = {key: value for key, value in kwargs.items() if value is not None}
            update_doc["update_time"] = datetime.now().isoformat()
            
            self.es.update(
                index=self.conversation_index,
                id=conversation_id,
                body={"doc": update_doc},
                refresh=True
            )
            
            logger.info(f"✅ 更新对话: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新对话失败: {e}")
            return False
    
    # ==================== 消息管理 ====================
    
    def save_message(self, message_id: str, conversation_id: str,
                    role: str, content: str,
                    create_time: Optional[str] = None,
                    **kwargs) -> bool:
        """保存消息"""
        try:
            doc = {
                "message_id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "create_time": create_time or datetime.now().isoformat(),
                "order_index": kwargs.get("order_index", 0),
                "parent_message_id": kwargs.get("parent_message_id", ""),
                "tokens": kwargs.get("tokens", 0)
            }
            
            self.es.index(
                index=self.message_index,
                id=message_id,
                body=doc,
                refresh=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存消息失败: {e}")
            return False
    
    def get_messages(self, conversation_id: str,
                    limit: Optional[int] = None) -> List[Dict]:
        """获取对话的所有消息"""
        try:
            query_body = {
                "query": {"term": {"conversation_id": conversation_id}},
                "sort": [{"order_index": {"order": "asc"}}],
                "size": limit or 10000
            }
            
            result = self.es.search(index=self.message_index, body=query_body)
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            logger.error(f"❌ 获取消息失败: {e}")
            return []
    
    # ==================== 搜索功能 ====================
    
    def search(self, query: str,
              search_type: str = "full",
              platform: Optional[str] = None,
              tags: Optional[List[str]] = None,
              limit: int = 20,
              offset: int = 0) -> List[Dict]:
        """
        全文搜索
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型 (full/title/content)
            platform: 平台筛选
            tags: 标签筛选
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            搜索结果列表，包含匹配的对话和消息
        """
        try:
            results = []
            
            # 搜索对话标题和摘要
            if search_type in ["full", "title"]:
                conv_results = self._search_conversations(
                    query, platform, tags, limit, offset
                )
                results.extend(conv_results)
            
            # 搜索消息内容
            if search_type in ["full", "content"]:
                msg_results = self._search_messages(
                    query, platform, tags, limit, offset
                )
                results.extend(msg_results)
            
            # 按评分排序
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []
    
    def _search_conversations(self, query: str, platform: Optional[str],
                             tags: Optional[List[str]],
                             limit: int, offset: int) -> List[Dict]:
        """搜索对话"""
        try:
            must_clauses = [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "summary^2", "tags"],
                        "type": "best_fields",
                        "operator": "or"
                    }
                }
            ]
            
            if platform:
                must_clauses.append({"term": {"platform": platform}})
            
            if tags:
                must_clauses.append({"terms": {"tags": tags}})
            
            search_body = {
                "query": {"bool": {"must": must_clauses}},
                "highlight": {
                    "fields": {
                        "title": {},
                        "summary": {}
                    },
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"]
                },
                "from": offset,
                "size": limit
            }
            
            result = self.es.search(index=self.conversation_index, body=search_body)
            
            conversations = []
            for hit in result['hits']['hits']:
                conv = hit['_source'].copy()
                conv['id'] = hit['_id']  # 添加ID字段
                conv['score'] = hit['_score']
                conv['search_type'] = 'conversation'
                conv['highlights'] = hit.get('highlight', {})
                
                # 统一字段名
                if 'create_time' in conv and 'created_at' not in conv:
                    conv['created_at'] = conv['create_time']
                if 'update_time' in conv and 'updated_at' not in conv:
                    conv['updated_at'] = conv['update_time']
                
                conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ 搜索对话失败: {e}")
            return []
    
    def _search_messages(self, query: str, platform: Optional[str],
                        tags: Optional[List[str]],
                        limit: int, offset: int) -> List[Dict]:
        """搜索消息内容"""
        try:
            # 先搜索消息
            search_body = {
                "query": {
                    "match": {
                        "content": {
                            "query": query,
                            "operator": "or"
                        }
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    },
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"]
                },
                "from": offset,
                "size": limit
            }
            
            result = self.es.search(index=self.message_index, body=search_body)
            
            messages = []
            for hit in result['hits']['hits']:
                msg = hit['_source'].copy()
                msg['score'] = hit['_score']
                msg['search_type'] = 'message'
                msg['highlights'] = hit.get('highlight', {})
                
                # 获取所属对话信息
                conv = self.get_conversation(msg['conversation_id'])
                if conv:
                    # 应用平台和标签筛选
                    if platform and conv.get('platform') != platform:
                        continue
                    if tags and not any(tag in conv.get('tags', []) for tag in tags):
                        continue
                    
                    msg['conversation_title'] = conv['title']
                    msg['platform'] = conv['platform']
                    messages.append(msg)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ 搜索消息失败: {e}")
            return []
    
    # ==================== 标签管理 ====================
    
    def save_tag(self, tag_id: str, name: str, color: str = "#3b82f6",
                description: str = "") -> bool:
        """保存标签"""
        try:
            doc = {
                "tag_id": tag_id,
                "name": name,
                "color": color,
                "description": description,
                "create_time": datetime.now().isoformat()
            }
            
            self.es.index(
                index=self.tag_index,
                id=tag_id,
                body=doc,
                refresh=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存标签失败: {e}")
            return False
    
    def get_all_tags(self) -> List[Dict]:
        """获取所有标签"""
        try:
            result = self.es.search(
                index=self.tag_index,
                body={"query": {"match_all": {}}, "size": 1000}
            )
            
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            logger.error(f"❌ 获取标签失败: {e}")
            return []
    
    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        try:
            self.es.delete(index=self.tag_index, id=tag_id, refresh=True)
            return True
        except Exception as e:
            logger.error(f"❌ 删除标签失败: {e}")
            return False
    
    # ==================== 统计分析 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            stats = {}
            
            # 对话统计
            conv_count = self.es.count(index=self.conversation_index)
            stats['total_conversations'] = conv_count['count']
            
            # 消息统计
            msg_count = self.es.count(index=self.message_index)
            stats['total_messages'] = msg_count['count']
            
            # 标签统计
            tag_count = self.es.count(index=self.tag_index)
            stats['total_tags'] = tag_count['count']
            
            # 平台统计
            platform_agg = self.es.search(
                index=self.conversation_index,
                body={
                    "size": 0,
                    "aggs": {
                        "platforms": {
                            "terms": {"field": "platform"}
                        }
                    }
                }
            )
            
            stats['by_platform'] = {
                bucket['key']: bucket['doc_count']
                for bucket in platform_agg['aggregations']['platforms']['buckets']
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}
    
    # ==================== 批量操作 ====================
    
    def bulk_save_messages(self, messages: List[Dict]) -> int:
        """批量保存消息"""
        try:
            actions = []
            for msg in messages:
                action = {
                    "_index": self.message_index,
                    "_id": msg['message_id'],
                    "_source": msg
                }
                actions.append(action)
            
            success, failed = helpers.bulk(self.es, actions, refresh=True)
            logger.info(f"✅ 批量保存消息: 成功 {success}, 失败 {len(failed)}")
            return success
            
        except Exception as e:
            logger.error(f"❌ 批量保存消息失败: {e}")
            return 0
    
    # ==================== 数据迁移 ====================
    
    def migrate_from_sqlite(self, sqlite_db_path: str) -> Tuple[int, int]:
        """
        从SQLite迁移数据到Elasticsearch
        
        Returns:
            (成功对话数, 成功消息数)
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect(sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 迁移对话
            cursor.execute("SELECT * FROM conversations")
            conversations = cursor.fetchall()
            
            conv_count = 0
            for conv in conversations:
                conv_dict = dict(conv)
                if self.save_conversation(**conv_dict):
                    conv_count += 1
            
            # 迁移消息
            cursor.execute("SELECT * FROM messages")
            messages = cursor.fetchall()
            
            msg_list = [dict(msg) for msg in messages]
            msg_count = self.bulk_save_messages(msg_list)
            
            # 迁移标签
            cursor.execute("SELECT * FROM tags")
            tags = cursor.fetchall()
            
            for tag in tags:
                tag_dict = dict(tag)
                self.save_tag(**tag_dict)
            
            conn.close()
            
            logger.info(f"✅ 数据迁移完成: {conv_count}个对话, {msg_count}条消息")
            return conv_count, msg_count
            
        except Exception as e:
            logger.error(f"❌ 数据迁移失败: {e}")
            return 0, 0
    
    # ==================== 健康检查 ====================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            cluster_health = self.es.cluster.health()
            
            return {
                "status": cluster_health['status'],
                "cluster_name": cluster_health['cluster_name'],
                "number_of_nodes": cluster_health['number_of_nodes'],
                "active_shards": cluster_health['active_shards'],
                "indices": {
                    "conversations": self.es.count(index=self.conversation_index)['count'],
                    "messages": self.es.count(index=self.message_index)['count'],
                    "tags": self.es.count(index=self.tag_index)['count']
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def close(self):
        """关闭连接"""
        try:
            self.es.close()
            logger.info("✅ Elasticsearch连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭连接失败: {e}")
    
    # ==================== BaseStorage抽象方法实现 ====================
    
    def connect(self) -> None:
        """建立连接（已在__init__中实现）"""
        pass
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        try:
            return self.es.ping()
        except Exception:
            return False
    
    def add_conversation(self,
                        platform: str,
                        source_url: str,
                        title: str,
                        summary: str,
                        raw_content: str,
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> int:
        """添加对话（兼容BaseStorage接口）"""
        import hashlib
        import json
        
        # 生成conversation_id
        conversation_id = hashlib.md5(source_url.encode()).hexdigest()
        
        # 解析raw_content获取消息
        try:
            content_data = json.loads(raw_content)
            message_count = len(content_data.get('messages', []))
        except:
            message_count = 0
        
        # 保存对话
        self.save_conversation(
            conversation_id=conversation_id,
            title=title,
            platform=platform,
            source_url=source_url,  # 传递source_url
            raw_content=raw_content,  # 传递raw_content
            summary=summary,
            category=category or "",
            tags=tags or [],
            message_count=message_count
        )
        
        return int(conversation_id[:8], 16)  # 返回整数ID
    
    def get_conversation_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """通过URL获取对话"""
        import hashlib
        conversation_id = hashlib.md5(url.encode()).hexdigest()
        return self.get_conversation(conversation_id)
    
    def add_tags(self, conversation_id: int, tags: List[str]) -> None:
        """添加标签"""
        conv_id = format(conversation_id, 'x').zfill(8)
        conv = self.get_conversation(conv_id)
        if conv:
            existing_tags = set(conv.get('tags', []))
            existing_tags.update(tags)
            self.update_conversation(conv_id, tags=list(existing_tags))
    
    def remove_tags(self, conversation_id: int, tags: List[str]) -> None:
        """移除标签"""
        conv_id = format(conversation_id, 'x').zfill(8)
        conv = self.get_conversation(conv_id)
        if conv:
            existing_tags = set(conv.get('tags', []))
            existing_tags.difference_update(tags)
            self.update_conversation(conv_id, tags=list(existing_tags))
    
    def get_conversation_tags(self, conversation_id: int) -> List[str]:
        """获取对话标签"""
        conv_id = format(conversation_id, 'x').zfill(8)
        conv = self.get_conversation(conv_id)
        return conv.get('tags', []) if conv else []
    
    def search_conversations(self,
                            keyword: str,
                            limit: int = 50,
                            context_size: int = 100) -> List[Dict[str, Any]]:
        """全文搜索对话（兼容BaseStorage接口）"""
        return self.search(query=keyword, search_type="full", limit=limit)
    
    def advanced_search(self,
                       keyword: Optional[str] = None,
                       platform: Optional[str] = None,
                       category: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """高级搜索"""
        try:
            must_clauses = []
            
            if keyword:
                must_clauses.append({
                    "multi_match": {
                        "query": keyword,
                        "fields": ["title^3", "summary^2", "category", "tags"]
                    }
                })
            
            if platform:
                must_clauses.append({"term": {"platform": platform}})
            
            if category:
                must_clauses.append({"term": {"category": category}})
            
            if tags:
                must_clauses.append({"terms": {"tags": tags}})
            
            if date_from or date_to:
                range_query = {"range": {"create_time": {}}}
                if date_from:
                    range_query["range"]["create_time"]["gte"] = date_from.isoformat()
                if date_to:
                    range_query["range"]["create_time"]["lte"] = date_to.isoformat()
                must_clauses.append(range_query)
            
            query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}
            
            result = self.es.search(
                index=self.conversation_index,
                body={
                    "query": query,
                    "size": limit,
                    "sort": [{"create_time": {"order": "desc"}}]
                }
            )
            
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            logger.error(f"❌ 高级搜索失败: {e}")
            return []
    
    def optimize(self) -> None:
        """优化存储（强制刷新和合并）"""
        try:
            for index in [self.conversation_index, self.message_index, self.tag_index]:
                self.es.indices.refresh(index=index)
                self.es.indices.forcemerge(index=index, max_num_segments=1)
            logger.info("✅ 索引优化完成")
        except Exception as e:
            logger.error(f"❌ 索引优化失败: {e}")
    
    def backup(self, backup_path: str) -> bool:
        """备份数据（导出为JSON）"""
        import json
        try:
            data = {
                'conversations': self.list_conversations(limit=10000),
                'tags': self.get_all_tags()
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 数据已备份到: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            return False
    
    def export_data(self, export_format: str = 'json') -> str:
        """导出数据"""
        import json
        try:
            data = {
                'conversations': self.list_conversations(limit=10000),
                'tags': self.get_all_tags()
            }
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 导出失败: {e}")
            return "{}"
    
    def import_data(self, data: str, data_format: str = 'json') -> int:
        """导入数据"""
        import json
        try:
            data_dict = json.loads(data)
            count = 0
            
            # 导入对话
            for conv in data_dict.get('conversations', []):
                if self.save_conversation(**conv):
                    count += 1
            
            # 导入标签
            for tag in data_dict.get('tags', []):
                self.save_tag(**tag)
            
            logger.info(f"✅ 导入完成: {count}个对话")
            return count
            
        except Exception as e:
            logger.error(f"❌ 导入失败: {e}")
            return 0
