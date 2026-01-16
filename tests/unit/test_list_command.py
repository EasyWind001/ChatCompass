"""测试list命令的ID问题"""
import sys
import os
from pathlib import Path
import tempfile

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 测试SQLite
print("=" * 70)
print("测试 SQLite list 命令")
print("=" * 70)

from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter

temp_db = tempfile.mktemp(suffix=".db")

try:
    # 初始化
    print("\n[1] 初始化SQLite...")
    sqlite_mgr = SQLiteManager(temp_db)
    adapter = StorageAdapter(sqlite_mgr)
    print("  ✅ 初始化成功")
    
    # 添加测试数据
    print("\n[2] 添加测试对话...")
    conv_id = adapter.add_conversation(
        source_url='https://test.com/123',
        platform='Test',
        title='测试对话',
        raw_content={'messages': [{'role': 'user', 'content': 'test'}]}
    )
    print(f"  ✅ 添加成功，ID: {conv_id}")
    
    # 测试list
    print("\n[3] 测试list命令...")
    conversations = adapter.get_all_conversations(limit=10)
    
    print(f"\n  返回记录数: {len(conversations)}")
    
    if len(conversations) > 0:
        first = conversations[0]
        print(f"  第一条记录的字段: {list(first.keys())}")
        
        if 'id' in first:
            print(f"  ✅ 包含id字段: {first['id']}")
            print(f"  ✅ 标题: {first['title']}")
            print("\n✅ SQLite测试通过！")
        else:
            print("  ❌ 缺少id字段！")
            print(f"  完整数据: {first}")
            sys.exit(1)
    else:
        print("  ❌ 没有返回记录！")
        sys.exit(1)
    
    adapter.close()

finally:
    try:
        os.unlink(temp_db)
    except:
        pass

print("\n" + "=" * 70)
print("所有测试通过！")
print("=" * 70)
