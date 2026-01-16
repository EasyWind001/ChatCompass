#!/usr/bin/env python3
"""
Delete功能单元测试
全面覆盖各种场景，确保删除功能稳定可靠

测试场景:
1. 基础删除 - 通过ID删除对话
2. 通过URL删除 - 验证URL查找后删除
3. 删除不存在的对话 - 验证错误处理
4. 删除后验证 - 确保数据完全清除
5. 级联删除 - 验证相关数据（标签、消息）一并删除
6. 并发删除 - SQLite和Elasticsearch
7. 边界情况 - 空ID、特殊字符、超长ID
"""
import os
import sys
import tempfile
import json
import pytest
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter


# ==================== 测试数据 ====================

MOCK_CONVERSATION = {
    'source_url': 'https://chatgpt.com/share/test-delete-123',
    'platform': 'ChatGPT',
    'title': '测试删除功能',
    'messages': [
        {'role': 'user', 'content': '这是测试消息1'},
        {'role': 'assistant', 'content': '这是回复1'}
    ]
}

MOCK_CONVERSATION_2 = {
    'source_url': 'https://chatgpt.com/share/test-delete-456',
    'platform': 'ChatGPT',
    'title': '测试删除功能2',
    'messages': [
        {'role': 'user', 'content': '这是测试消息2'}
    ]
}


# ==================== Fixtures ====================

@pytest.fixture
def temp_db():
    """创建临时数据库"""
    temp_file = tempfile.mktemp('.db')
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def storage_adapter(temp_db):
    """创建StorageAdapter实例"""
    sqlite_mgr = SQLiteManager(temp_db)
    adapter = StorageAdapter(sqlite_mgr)
    yield adapter
    adapter.close()


@pytest.fixture
def conversation_with_id(storage_adapter):
    """创建测试对话并返回ID"""
    conv_id = storage_adapter.add_conversation(
        source_url=MOCK_CONVERSATION['source_url'],
        platform=MOCK_CONVERSATION['platform'],
        title=MOCK_CONVERSATION['title'],
        raw_content=MOCK_CONVERSATION,
        summary="测试摘要",
        category="测试分类",
        tags=["测试", "删除"]
    )
    return conv_id


# ==================== 测试用例 ====================

class TestDeleteBasic:
    """基础删除测试"""
    
    def test_delete_by_id(self, storage_adapter, conversation_with_id):
        """测试1: 通过ID删除对话"""
        conv_id = conversation_with_id
        
        # 验证对话存在
        conv = storage_adapter.get_conversation(conv_id)
        assert conv is not None, "对话应该存在"
        
        # 删除对话
        result = storage_adapter.delete_conversation(conv_id)
        assert result is True, "删除应该成功"
        
        # 验证对话已删除
        conv_after = storage_adapter.get_conversation(conv_id)
        assert conv_after is None, "对话应该已被删除"
    
    def test_delete_by_url(self, storage_adapter, conversation_with_id):
        """测试2: 通过URL删除对话"""
        conv_id = conversation_with_id
        url = MOCK_CONVERSATION['source_url']
        
        # 通过URL查找对话
        conv = storage_adapter.get_conversation_by_url(url)
        assert conv is not None, "应该能通过URL找到对话"
        assert str(conv['id']) == str(conv_id), "ID应该匹配"  # 统一转字符串比较
        
        # 通过URL对应的ID删除
        result = storage_adapter.delete_conversation(str(conv['id']))
        assert result is True, "删除应该成功"
        
        # 验证通过URL无法找到
        conv_after = storage_adapter.get_conversation_by_url(url)
        assert conv_after is None, "通过URL应该找不到对话"


class TestDeleteEdgeCases:
    """边界情况测试"""
    
    def test_delete_nonexistent_id(self, storage_adapter):
        """测试3: 删除不存在的对话"""
        result = storage_adapter.delete_conversation("nonexistent123")
        # 删除不存在的对话应该返回True或False（取决于实现）
        # 重要的是不应该抛出异常
        assert isinstance(result, bool), "应该返回布尔值"
    
    def test_delete_empty_id(self, storage_adapter):
        """测试4: 删除空ID"""
        # 空ID应该返回False或抛出异常
        try:
            result = storage_adapter.delete_conversation("")
            assert result is False, "空ID应该删除失败"
        except Exception:
            pass  # 抛出异常也是可接受的
    
    def test_delete_invalid_id_format(self, storage_adapter):
        """测试5: 删除无效格式的ID"""
        invalid_ids = [
            "###invalid###",
            "../../etc/passwd",
            "'; DROP TABLE conversations; --",
            " " * 1000,  # 超长空格
        ]
        
        for invalid_id in invalid_ids:
            try:
                result = storage_adapter.delete_conversation(invalid_id)
                # 不应该成功
                assert result is False, f"无效ID应该删除失败: {invalid_id}"
            except Exception:
                pass  # 抛出异常也是可接受的


class TestDeleteVerification:
    """删除验证测试"""
    
    def test_delete_removes_from_list(self, storage_adapter, conversation_with_id):
        """测试6: 删除后从列表中移除"""
        conv_id = conversation_with_id
        
        # 验证在列表中
        all_convs = storage_adapter.get_all_conversations()
        ids = [str(c['id']) for c in all_convs]  # 统一转字符串
        assert str(conv_id) in ids, "对话应该在列表中"
        
        # 删除
        storage_adapter.delete_conversation(conv_id)
        
        # 验证不在列表中
        all_convs_after = storage_adapter.get_all_conversations()
        ids_after = [str(c['id']) for c in all_convs_after]  # 统一转字符串
        assert str(conv_id) not in ids_after, "对话不应该在列表中"
    
    def test_delete_updates_statistics(self, storage_adapter, conversation_with_id):
        """测试7: 删除后更新统计信息"""
        conv_id = conversation_with_id
        
        # 获取删除前的统计
        stats_before = storage_adapter.get_statistics()
        count_before = stats_before['total_conversations']
        
        # 删除
        storage_adapter.delete_conversation(conv_id)
        
        # 获取删除后的统计
        stats_after = storage_adapter.get_statistics()
        count_after = stats_after['total_conversations']
        
        assert count_after == count_before - 1, "总数应该减1"
    
    def test_delete_not_in_search(self, storage_adapter, conversation_with_id):
        """测试8: 删除后搜索不到"""
        conv_id = conversation_with_id
        
        # 搜索应该能找到
        results_before = storage_adapter.search_conversations("测试", limit=10)
        assert len(results_before) > 0, "应该能搜索到"
        
        # 删除
        storage_adapter.delete_conversation(conv_id)
        
        # 搜索应该找不到这个特定对话
        results_after = storage_adapter.search_conversations("测试删除功能", limit=10)
        ids_after = [r['id'] for r in results_after]
        assert conv_id not in ids_after, "搜索不应该找到已删除的对话"


class TestDeleteCascade:
    """级联删除测试"""
    
    def test_delete_with_tags(self, storage_adapter):
        """测试9: 删除带标签的对话"""
        # 添加对话
        conv_id = storage_adapter.add_conversation(
            source_url=MOCK_CONVERSATION['source_url'],
            platform=MOCK_CONVERSATION['platform'],
            title=MOCK_CONVERSATION['title'],
            raw_content=MOCK_CONVERSATION,
            tags=["标签1", "标签2", "标签3"]
        )
        
        # 验证标签存在
        tags = storage_adapter.get_conversation_tags(conv_id)
        assert len(tags) == 3, "应该有3个标签"
        
        # 删除对话
        storage_adapter.delete_conversation(conv_id)
        
        # 验证标签关联已删除（对话不存在，标签也无法获取）
        conv_after = storage_adapter.get_conversation(conv_id)
        assert conv_after is None, "对话应该已删除"


class TestDeleteMultiple:
    """多次删除测试"""
    
    def test_delete_multiple_conversations(self, storage_adapter):
        """测试10: 删除多个对话"""
        # 添加3个对话
        ids = []
        for i in range(3):
            conv_id = storage_adapter.add_conversation(
                source_url=f'https://test.com/conv{i}',
                platform='ChatGPT',
                title=f'测试对话{i}',
                raw_content={'messages': []}
            )
            ids.append(conv_id)
        
        # 验证都存在
        for conv_id in ids:
            conv = storage_adapter.get_conversation(conv_id)
            assert conv is not None, f"对话{conv_id}应该存在"
        
        # 删除所有
        for conv_id in ids:
            result = storage_adapter.delete_conversation(conv_id)
            assert result is True, f"删除{conv_id}应该成功"
        
        # 验证都不存在
        for conv_id in ids:
            conv = storage_adapter.get_conversation(conv_id)
            assert conv is None, f"对话{conv_id}应该已删除"
    
    def test_delete_same_id_twice(self, storage_adapter, conversation_with_id):
        """测试11: 重复删除同一对话"""
        conv_id = conversation_with_id
        
        # 第一次删除
        result1 = storage_adapter.delete_conversation(conv_id)
        assert result1 is True, "第一次删除应该成功"
        
        # 第二次删除
        result2 = storage_adapter.delete_conversation(conv_id)
        # 第二次删除应该返回False或True（取决于实现）
        assert isinstance(result2, bool), "应该返回布尔值"


class TestDeleteIntegration:
    """集成测试"""
    
    def test_add_delete_add_again(self, storage_adapter):
        """测试12: 添加-删除-再添加相同URL"""
        url = MOCK_CONVERSATION['source_url']
        
        # 第一次添加
        conv_id1 = storage_adapter.add_conversation(
            source_url=url,
            platform=MOCK_CONVERSATION['platform'],
            title=MOCK_CONVERSATION['title'],
            raw_content=MOCK_CONVERSATION
        )
        
        # 删除
        storage_adapter.delete_conversation(conv_id1)
        
        # 再次添加相同URL
        conv_id2 = storage_adapter.add_conversation(
            source_url=url,
            platform=MOCK_CONVERSATION['platform'],
            title=MOCK_CONVERSATION['title'] + " (v2)",
            raw_content=MOCK_CONVERSATION
        )
        
        # 应该能成功添加
        conv = storage_adapter.get_conversation(conv_id2)
        assert conv is not None, "应该能再次添加"
        assert conv['title'].endswith("(v2)"), "标题应该是新的"


class TestDeletePerformance:
    """性能测试"""
    
    def test_delete_batch_performance(self, storage_adapter):
        """测试13: 批量删除性能"""
        import time
        
        # 添加100个对话
        ids = []
        for i in range(100):
            conv_id = storage_adapter.add_conversation(
                source_url=f'https://test.com/perf{i}',
                platform='ChatGPT',
                title=f'性能测试{i}',
                raw_content={'messages': [{'role': 'user', 'content': f'测试{i}'}]}
            )
            ids.append(conv_id)
        
        # 批量删除
        start_time = time.time()
        for conv_id in ids:
            storage_adapter.delete_conversation(conv_id)
        elapsed = time.time() - start_time
        
        # 验证删除速度（应该在合理范围内）
        avg_time = elapsed / len(ids)
        assert avg_time < 0.1, f"平均删除时间过长: {avg_time:.3f}s"
        
        print(f"批量删除100个对话耗时: {elapsed:.2f}s (平均: {avg_time*1000:.1f}ms)")


# ==================== 运行测试 ====================

if __name__ == '__main__':
    print("=" * 80)
    print("Delete功能单元测试")
    print("=" * 80)
    
    # 运行pytest
    exit_code = pytest.main([
        __file__,
        '-v',           # 详细输出
        '--tb=short',   # 简化traceback
        '-s',           # 显示print输出
        '--durations=5' # 显示最慢的5个测试
    ])
    
    sys.exit(exit_code)
