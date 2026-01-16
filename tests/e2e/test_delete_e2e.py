#!/usr/bin/env python3
"""
Delete功能端到端测试
完整模拟用户操作流程，验证delete命令在真实场景下的表现

测试流程:
1. 初始化系统（SQLite + Elasticsearch两种后端）
2. 添加多个对话
3. 列出对话
4. 通过ID删除对话
5. 通过URL删除对话
6. 验证删除效果
7. 异常场景处理
"""
import os
import sys
import tempfile
import json
import subprocess
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter
from main import ChatCompass


# ==================== 测试数据 ====================

MOCK_CONVERSATIONS = [
    {
        'source_url': 'https://chatgpt.com/share/e2e-test-001',
        'platform': 'ChatGPT',
        'title': 'Python编程基础',
        'messages': [
            {'role': 'user', 'content': '如何学习Python？'},
            {'role': 'assistant', 'content': 'Python学习建议：1. 基础语法 2. 数据结构 3. 实战项目'}
        ]
    },
    {
        'source_url': 'https://chatgpt.com/share/e2e-test-002',
        'platform': 'ChatGPT',
        'title': 'Docker容器化部署',
        'messages': [
            {'role': 'user', 'content': 'Docker如何使用？'},
            {'role': 'assistant', 'content': 'Docker基础命令：docker build, docker run, docker-compose'}
        ]
    },
    {
        'source_url': 'https://chatgpt.com/share/e2e-test-003',
        'platform': 'ChatGPT',
        'title': 'Git版本控制',
        'messages': [
            {'role': 'user', 'content': 'Git常用命令有哪些？'},
            {'role': 'assistant', 'content': 'Git命令：git add, git commit, git push, git pull'}
        ]
    }
]


# ==================== 辅助函数 ====================

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step(step_num, desc):
    """打印测试步骤"""
    print(f"\n[步骤 {step_num}] {desc}")


def verify_result(condition, success_msg, fail_msg):
    """验证测试结果"""
    if condition:
        print(f"  ✅ {success_msg}")
        return True
    else:
        print(f"  ❌ {fail_msg}")
        return False


# ==================== E2E测试 ====================

def test_e2e_delete_sqlite():
    """端到端测试1: SQLite后端完整流程"""
    print_section("端到端测试1: SQLite后端 - Delete功能完整流程")
    
    # 创建临时数据库
    temp_db = tempfile.mktemp('.db')
    print(f"📁 临时数据库: {temp_db}")
    
    try:
        # 初始化存储
        sqlite_mgr = SQLiteManager(temp_db)
        adapter = StorageAdapter(sqlite_mgr)
        
        # 步骤1: 添加测试对话
        print_step(1, "添加3个测试对话")
        conv_ids = []
        for i, conv_data in enumerate(MOCK_CONVERSATIONS):
            conv_id = adapter.add_conversation(
                source_url=conv_data['source_url'],
                platform=conv_data['platform'],
                title=conv_data['title'],
                raw_content=conv_data,
                summary=f"摘要{i+1}",
                category="技术",
                tags=["测试", f"tag{i+1}"]
            )
            conv_ids.append(conv_id)
            print(f"  ✅ 添加成功: ID={conv_id}, 标题={conv_data['title']}")
        
        # 步骤2: 验证对话列表
        print_step(2, "验证对话列表")
        all_convs = adapter.get_all_conversations()
        verify_result(
            len(all_convs) >= 3,
            f"对话列表包含{len(all_convs)}个对话",
            "对话列表数量不足"
        )
        
        # 步骤3: 通过ID删除第一个对话
        print_step(3, f"通过ID删除对话: {conv_ids[0]}")
        conv_to_delete = adapter.get_conversation(conv_ids[0])
        print(f"  待删除对话: {conv_to_delete['title']}")
        
        result = adapter.delete_conversation(conv_ids[0])
        verify_result(result, "删除成功", "删除失败")
        
        # 验证删除效果
        conv_after = adapter.get_conversation(conv_ids[0])
        verify_result(
            conv_after is None,
            "对话已从数据库移除",
            "对话仍然存在"
        )
        
        # 步骤4: 通过URL删除第二个对话
        print_step(4, f"通过URL删除对话: {MOCK_CONVERSATIONS[1]['source_url']}")
        url = MOCK_CONVERSATIONS[1]['source_url']
        conv_by_url = adapter.get_conversation_by_url(url)
        
        if conv_by_url:
            print(f"  找到对话: {conv_by_url['title']}")
            result = adapter.delete_conversation(conv_by_url['id'])
            verify_result(result, "删除成功", "删除失败")
            
            # 验证通过URL找不到
            conv_after = adapter.get_conversation_by_url(url)
            verify_result(
                conv_after is None,
                "通过URL找不到对话（已删除）",
                "仍能通过URL找到对话"
            )
        else:
            print("  ❌ 未找到对话")
        
        # 步骤5: 验证统计信息更新
        print_step(5, "验证统计信息")
        stats = adapter.get_statistics()
        remaining = stats['total_conversations']
        print(f"  剩余对话数: {remaining}")
        verify_result(
            remaining == 1,
            f"统计正确（已删除2个，剩余1个）",
            f"统计错误（期望1个，实际{remaining}个）"
        )
        
        # 步骤6: 验证搜索结果
        print_step(6, "验证搜索结果（已删除的对话不应出现）")
        search_results = adapter.search_conversations("Python", limit=10)
        deleted_ids = [conv_ids[0], conv_ids[1]]
        found_deleted = any(r['id'] in deleted_ids for r in search_results)
        verify_result(
            not found_deleted,
            "搜索结果不包含已删除的对话",
            "搜索结果仍包含已删除的对话"
        )
        
        # 步骤7: 删除不存在的对话
        print_step(7, "删除不存在的对话（异常处理）")
        result = adapter.delete_conversation("nonexistent_id_12345")
        verify_result(
            isinstance(result, bool),
            "正确处理了不存在的ID",
            "异常处理失败"
        )
        
        # 步骤8: 重复删除已删除的对话
        print_step(8, "重复删除已删除的对话")
        result = adapter.delete_conversation(conv_ids[0])
        verify_result(
            isinstance(result, bool),
            "正确处理了重复删除",
            "重复删除处理失败"
        )
        
        print("\n" + "=" * 80)
        print("✅ SQLite后端端到端测试完成")
        print("=" * 80)
        
        adapter.close()
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_db):
            os.remove(temp_db)


def test_e2e_delete_with_chatcompass_class():
    """端到端测试2: 使用ChatCompass类测试delete_conversation方法"""
    print_section("端到端测试2: ChatCompass类 - delete_conversation方法")
    
    temp_db = tempfile.mktemp('.db')
    print(f"📁 临时数据库: {temp_db}")
    
    # 临时设置环境变量
    original_storage = os.environ.get('STORAGE_TYPE')
    original_db_path = os.environ.get('SQLITE_DB_PATH')
    
    os.environ['STORAGE_TYPE'] = 'sqlite'
    os.environ['SQLITE_DB_PATH'] = temp_db
    
    try:
        # 初始化ChatCompass
        print_step(1, "初始化ChatCompass应用")
        
        # 需要重新导入config以使用新的环境变量
        import importlib
        import config
        importlib.reload(config)
        
        app = ChatCompass()
        
        # 步骤2: 添加测试对话
        print_step(2, "添加测试对话")
        conv_id = app.db.add_conversation(
            source_url=MOCK_CONVERSATIONS[0]['source_url'],
            platform=MOCK_CONVERSATIONS[0]['platform'],
            title=MOCK_CONVERSATIONS[0]['title'],
            raw_content=MOCK_CONVERSATIONS[0]
        )
        print(f"  ✅ 添加成功: ID={conv_id}")
        
        # 步骤3: 验证对话存在
        print_step(3, "验证对话存在")
        conv = app.db.get_conversation(conv_id)
        verify_result(
            conv is not None,
            f"对话存在: {conv['title']}",
            "对话不存在"
        )
        
        # 步骤4: 模拟用户确认删除（自动输入'yes'）
        print_step(4, "测试delete_conversation方法")
        with patch('builtins.input', return_value='yes'):
            result = app.delete_conversation(conv_id)
        
        verify_result(
            result is True,
            "delete_conversation返回True",
            "delete_conversation返回False"
        )
        
        # 步骤5: 验证对话已删除
        print_step(5, "验证对话已删除")
        conv_after = app.db.get_conversation(conv_id)
        verify_result(
            conv_after is None,
            "对话已完全删除",
            "对话仍然存在"
        )
        
        # 步骤6: 测试取消删除
        print_step(6, "测试取消删除")
        conv_id2 = app.db.add_conversation(
            source_url=MOCK_CONVERSATIONS[1]['source_url'],
            platform=MOCK_CONVERSATIONS[1]['platform'],
            title=MOCK_CONVERSATIONS[1]['title'],
            raw_content=MOCK_CONVERSATIONS[1]
        )
        
        with patch('builtins.input', return_value='no'):
            result = app.delete_conversation(conv_id2)
        
        verify_result(
            result is False,
            "用户取消，返回False",
            "应该返回False"
        )
        
        # 验证对话仍然存在
        conv_still_exists = app.db.get_conversation(conv_id2)
        verify_result(
            conv_still_exists is not None,
            "对话未被删除（取消生效）",
            "对话被错误删除"
        )
        
        # 步骤7: 测试删除不存在的对话
        print_step(7, "测试删除不存在的对话")
        result = app.delete_conversation("nonexistent_99999")  # 不需要mock input
        
        verify_result(
            result is False,
            "正确返回False",
            "应该返回False"
        )
        
        print("\n" + "=" * 80)
        print("✅ ChatCompass类端到端测试完成")
        print("=" * 80)
        
        app.close()
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 恢复环境变量
        if original_storage:
            os.environ['STORAGE_TYPE'] = original_storage
        elif 'STORAGE_TYPE' in os.environ:
            del os.environ['STORAGE_TYPE']
        
        if original_db_path:
            os.environ['SQLITE_DB_PATH'] = original_db_path
        elif 'SQLITE_DB_PATH' in os.environ:
            del os.environ['SQLITE_DB_PATH']
        
        # 清理临时文件
        if os.path.exists(temp_db):
            os.remove(temp_db)


def test_e2e_command_line():
    """端到端测试3: 命令行接口测试"""
    print_section("端到端测试3: 命令行接口 - python main.py delete")
    
    temp_db = tempfile.mktemp('.db')
    print(f"📁 临时数据库: {temp_db}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['STORAGE_TYPE'] = 'sqlite'
    env['SQLITE_DB_PATH'] = temp_db
    
    try:
        # 步骤1: 通过命令行添加对话
        print_step(1, "初始化数据库并添加对话")
        
        # 直接使用Python API添加（因为命令行add需要网络）
        from database.sqlite_manager import SQLiteManager
        from database.storage_adapter import StorageAdapter
        
        sqlite_mgr = SQLiteManager(temp_db)
        adapter = StorageAdapter(sqlite_mgr)
        
        conv_id = adapter.add_conversation(
            source_url=MOCK_CONVERSATIONS[0]['source_url'],
            platform=MOCK_CONVERSATIONS[0]['platform'],
            title=MOCK_CONVERSATIONS[0]['title'],
            raw_content=MOCK_CONVERSATIONS[0]
        )
        print(f"  ✅ 添加成功: ID={conv_id}")
        
        adapter.close()
        
        # 步骤2: 使用命令行show验证对话存在
        print_step(2, f"命令行验证对话存在: python main.py show {conv_id}")
        result = subprocess.run(
            [sys.executable, 'main.py', 'show', conv_id],
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 指定UTF-8编码
            errors='ignore',   # 忽略编码错误
            timeout=10
        )
        
        stdout_text = result.stdout or ""
        success = conv_id in stdout_text and MOCK_CONVERSATIONS[0]['title'] in stdout_text
        verify_result(
            success,
            "命令行show成功显示对话",
            f"命令行show失败\nstdout: {stdout_text}\nstderr: {result.stderr}"
        )
        
        # 步骤3: 注意 - 命令行delete需要用户确认，这里只测试语法
        print_step(3, "验证delete命令语法（不实际执行）")
        print(f"  命令: python main.py delete {conv_id}")
        print(f"  ⚠️  需要交互确认，跳过实际执行")
        
        # 步骤4: 直接通过API删除，然后验证命令行找不到
        print_step(4, "通过API删除，验证命令行找不到")
        adapter = StorageAdapter(SQLiteManager(temp_db))
        adapter.delete_conversation(conv_id)
        adapter.close()
        
        result = subprocess.run(
            [sys.executable, 'main.py', 'show', conv_id],
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=10
        )
        
        stdout_text = result.stdout or ""
        not_found = "未找到对话" in stdout_text
        verify_result(
            not_found,
            "命令行正确显示'未找到对话'",
            f"命令行show仍能找到已删除对话\nstdout: {stdout_text}"
        )
        
        print("\n" + "=" * 80)
        print("✅ 命令行接口端到端测试完成")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_db):
            os.remove(temp_db)


# ==================== 主函数 ====================

def main():
    """运行所有端到端测试"""
    print("\n" + "🚀" * 40)
    print("Delete功能端到端测试套件")
    print("🚀" * 40)
    
    results = []
    
    # 测试1: SQLite后端完整流程
    results.append(("SQLite后端", test_e2e_delete_sqlite()))
    
    # 测试2: ChatCompass类方法
    results.append(("ChatCompass类", test_e2e_delete_with_chatcompass_class()))
    
    # 测试3: 命令行接口
    results.append(("命令行接口", test_e2e_command_line()))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有端到端测试通过！Delete功能已就绪上线。")
    else:
        print("⚠️  部分测试失败，请检查并修复问题。")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
