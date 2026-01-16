"""最简单的数据库测试"""
import sys
import traceback

try:
    print("导入模块...")
    from database.db_manager import DatabaseManager
    
    print("初始化数据库...")
    db = DatabaseManager("test_simple.db")
    
    print("添加数据...")
    conv_id = db.add_conversation(
        source_url="https://test.com/1",
        platform="chatgpt",
        title="测试",
        raw_content={'messages': []},
    )
    
    print(f"成功! ID={conv_id}")
    db.close()
    
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
    sys.exit(1)
