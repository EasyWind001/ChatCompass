"""
快速测试基础功能
直接测试，不依赖pytest
"""
import sys
import os
from pathlib import Path
import tempfile
import shutil

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter


def test_basic_functions():
    """测试所有基础功能"""
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        print("="*70)
        print("ChatCompass 基础功能测试")
        print("="*70)
        
        # 初始化
        print("\n[1/10] 初始化数据库...")
        sqlite_manager = SQLiteManager(db_path)
        adapter = StorageAdapter(sqlite_manager)
        print("  ✅ 初始化成功")
        
        # 测试1: 列出空数据库
        print("\n[2/10] 测试列出对话（空数据库）...")
        conversations = adapter.get_all_conversations(limit=10)
        assert conversations == [], f"预期空列表，实际: {conversations}"
        print("  ✅ 空数据库测试通过")
        
        # 测试2: 添加对话
        print("\n[3/10] 测试添加对话...")
        sample_data = {
            'source_url': 'https://chatgpt.com/share/test123',
            'platform': 'ChatGPT',
            'title': '测试对话 - Python函数',
            'raw_content': {
                'messages': [
                    {'role': 'user', 'content': '帮我写个Python函数'},
                    {'role': 'assistant', 'content': 'def hello(): print("Hello")'}
                ]
            },
            'summary': '讨论Python函数编写',
            'category': '编程',
            'tags': ['python', '函数']
        }
        
        conv_id = adapter.add_conversation(**sample_data)
        assert conv_id is not None, "添加对话失败"
        print(f"  ✅ 添加成功，ID: {conv_id}")
        
        # 测试3: 列出对话（有数据）
        print("\n[4/10] 测试列出对话（有数据）...")
        conversations = adapter.get_all_conversations(limit=10)
        assert len(conversations) == 1, f"预期1条记录，实际: {len(conversations)}"
        
        # 关键测试：检查是否有id字段
        first_conv = conversations[0]
        if 'id' not in first_conv:
            print(f"  ❌ 错误：返回的对话缺少 'id' 字段！")
            print(f"  实际字段: {list(first_conv.keys())}")
            raise AssertionError("list命令返回的结果缺少id字段")
        
        print(f"  ✅ 列出成功，包含id字段")
        print(f"     ID: {first_conv['id']}")
        print(f"     标题: {first_conv['title']}")
        
        # 测试4: 获取对话详情
        print("\n[5/10] 测试获取对话详情...")
        conversation = adapter.get_conversation(conv_id)
        assert conversation is not None, "获取对话失败"
        assert 'id' in conversation, "对话详情缺少id字段"
        assert conversation['title'] == sample_data['title'], "标题不匹配"
        print(f"  ✅ 获取成功")
        
        # 测试5: 搜索功能
        print("\n[6/10] 测试搜索功能...")
        results = adapter.search_conversations('python', limit=10)
        assert len(results) > 0, "搜索失败"
        assert 'id' in results[0], "搜索结果缺少id字段"
        print(f"  ✅ 搜索成功，找到 {len(results)} 条结果")
        
        # 测试6: 获取标签
        print("\n[7/10] 测试获取标签...")
        tags = adapter.get_conversation_tags(conv_id)
        assert len(tags) == 2, f"标签数量错误，预期2，实际{len(tags)}"
        assert 'python' in tags, "缺少python标签"
        print(f"  ✅ 标签获取成功: {tags}")
        
        # 测试7: 统计信息
        print("\n[8/10] 测试统计信息...")
        stats = adapter.get_statistics()
        assert stats['total_conversations'] == 1, "统计错误"
        assert 'ChatGPT' in stats['by_platform'], "平台统计错误"
        print(f"  ✅ 统计成功")
        print(f"     总对话数: {stats['total_conversations']}")
        print(f"     平台分布: {stats['by_platform']}")
        
        # 测试8: 更新对话
        print("\n[9/10] 测试更新对话...")
        success = adapter.update_conversation(conv_id, {
            'title': '更新后的标题',
            'category': '新分类'
        })
        assert success is True, "更新失败"
        
        updated = adapter.get_conversation(conv_id)
        assert updated['title'] == '更新后的标题', "更新未生效"
        print(f"  ✅ 更新成功")
        
        # 测试9: 添加第二条对话
        print("\n[10/10] 测试多条对话...")
        conv_id2 = adapter.add_conversation(
            source_url='https://chatgpt.com/share/test456',
            platform='Claude',
            title='第二条对话',
            raw_content={'messages': []},
            category='学习'
        )
        
        conversations = adapter.get_all_conversations(limit=10)
        assert len(conversations) == 2, f"预期2条记录，实际{len(conversations)}"
        
        # 验证两条都有id
        for i, conv in enumerate(conversations, 1):
            assert 'id' in conv, f"第{i}条记录缺少id字段"
        
        print(f"  ✅ 多条对话测试通过")
        
        # 清理
        adapter.close()
        
        print("\n" + "="*70)
        print("✅ 所有测试通过！")
        print("="*70)
        
        print("\n测试覆盖:")
        print("  ✅ 1. 列出对话（空）")
        print("  ✅ 2. 添加对话")
        print("  ✅ 3. 列出对话（有数据）- 包含ID字段验证 ⭐")
        print("  ✅ 4. 获取对话详情")
        print("  ✅ 5. 搜索功能")
        print("  ✅ 6. 获取标签")
        print("  ✅ 7. 统计信息")
        print("  ✅ 8. 更新对话")
        print("  ✅ 9. 多条对话")
        print("  ✅ 10. ID字段完整性")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == '__main__':
    success = test_basic_functions()
    sys.exit(0 if success else 1)
