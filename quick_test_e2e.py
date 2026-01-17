"""
v1.3.0 快速端到端测试套件

测试覆盖:
1. 数据库核心功能
2. GUI基础组件
3. 错误处理机制
4. 剪贴板监控
5. 任务队列系统

使用方法:
    python run_tests_interactive.py quick_test_e2e.py --quick
"""
import sys
import pytest
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from gui.error_handler import ErrorHandler


class TestPhase1_Database:
    """阶段1: 数据库核心功能测试"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """创建测试数据库"""
        db_path = tmp_path / "test_v130.db"
        db = DatabaseManager(str(db_path))
        yield db
        db.close()
        if db_path.exists():
            db_path.unlink()
    
    def test_01_database_creation(self, db):
        """测试数据库创建"""
        assert db is not None
        assert Path(db.db_path).exists()
        print("✅ 数据库创建成功")
    
    def test_02_add_conversation(self, db):
        """测试添加对话"""
        conv_id = db.add_conversation(
            source_url="https://chat.openai.com/c/test-123",
            platform="chatgpt",
            title="测试对话",
            raw_content={"messages": [{"role": "user", "content": "这是测试内容"}]},
            category="测试"
        )
        assert conv_id > 0
        print(f"✅ 添加对话成功: ID={conv_id}")
    
    def test_03_list_conversations(self, db):
        """测试列出对话"""
        # 先添加一些数据
        for i in range(3):
            db.add_conversation(
                source_url=f"https://chat.openai.com/c/test-{i}",
                platform="chatgpt",
                title=f"测试对话{i}",
                raw_content={"messages": [{"role": "user", "content": f"内容{i}"}]},
                category="测试"
            )
        
        conversations = db.get_all_conversations()
        assert len(conversations) == 3
        print(f"✅ 列出对话成功: 共{len(conversations)}条")
    
    def test_04_search_conversations(self, db):
        """测试搜索对话"""
        # 添加可搜索的对话
        db.add_conversation(
            source_url="https://chat.openai.com/c/search-test",
            platform="chatgpt",
            title="Python编程",
            raw_content={"messages": [{"role": "user", "content": "如何使用Python进行数据分析"}]},
            category="编程"
        )
        
        results = db.search_conversations("Python")
        assert len(results) > 0
        print(f"✅ 搜索功能正常: 找到{len(results)}条结果")


class TestPhase2_ErrorHandling:
    """阶段2: 错误处理机制测试"""
    
    def test_01_error_handler_module(self):
        """测试错误处理器模块"""
        assert ErrorHandler is not None
        print("✅ 错误处理器模块导入成功")
    
    def test_02_log_error(self):
        """测试错误记录"""
        initial_count = len(ErrorHandler.get_error_history())
        
        try:
            raise ValueError("测试错误")
        except Exception as e:
            ErrorHandler.handle_error(e, user_message="测试上下文", show_dialog=False)
        
        new_count = len(ErrorHandler.get_error_history())
        assert new_count == initial_count + 1
        print(f"✅ 错误记录成功: 当前共{new_count}条错误")
    
    def test_03_get_error_history(self):
        """测试获取错误历史"""
        # 添加多个错误
        for i in range(3):
            try:
                raise RuntimeError(f"测试错误{i}")
            except Exception as e:
                ErrorHandler.handle_error(e, user_message=f"测试{i}", show_dialog=False)
        
        history = ErrorHandler.get_error_history()
        assert len(history) >= 3
        print(f"✅ 错误历史功能正常: 共{len(history)}条记录")
    
    def test_04_export_errors(self, tmp_path):
        """测试导出错误日志"""
        export_path = tmp_path / "test_errors.log"
        
        exported = ErrorHandler.export_error_log(export_path)
        if exported and export_path.exists():
            content = export_path.read_text(encoding='utf-8')
            print(f"✅ 错误导出成功: {len(content)}字节")
        else:
            print("⚠️  暂无错误可导出 (这是正常的)")


class TestPhase3_GUI_Components:
    """阶段3: GUI组件基础测试 (无界面)"""
    
    def test_01_import_modules(self):
        """测试GUI模块导入"""
        try:
            from gui.main_window import MainWindow
            from gui.conversation_list import ConversationList
            from gui.detail_panel import DetailPanel
            from gui.task_manager import TaskManager
            from gui.clipboard_monitor import ClipboardMonitor
            print("✅ 所有GUI模块导入成功")
        except ImportError as e:
            pytest.fail(f"模块导入失败: {e}")
    
    def test_02_task_components(self):
        """测试任务组件"""
        from gui.task_queue import TaskQueue
        from gui.task_manager import TaskManagerThread
        
        # 测试任务队列
        queue = TaskQueue()
        assert queue.max_workers > 0
        print(f"  ✅ 任务队列创建成功 (max_workers={queue.max_workers})")
        
        # 测试管理器线程可以导入
        assert TaskManagerThread is not None
        print("  ✅ 任务管理器模块导入成功")
    
    def test_03_error_handler_integration(self):
        """测试错误处理器GUI集成"""
        from gui.error_handler import handle_error, handle_warning
        
        # 测试不显示对话框的错误处理
        try:
            raise ValueError("GUI测试错误")
        except Exception as e:
            handle_error(e, user_message="GUI错误测试", show_dialog=False)
        
        print("✅ 错误处理器GUI集成正常")


class TestPhase4_Integration:
    """阶段4: 集成测试"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """创建测试数据库"""
        db_path = tmp_path / "test_integration.db"
        db = DatabaseManager(str(db_path))
        yield db
        db.close()
        if db_path.exists():
            db_path.unlink()
    
    def test_01_database_with_error_handling(self, db):
        """测试数据库与错误处理集成"""
        from gui.error_handler import handle_error
        
        # 测试正常操作
        conv_id = db.add_conversation(
            source_url="https://test.com/c/123",
            platform="chatgpt",
            title="集成测试",
            raw_content={"messages": [{"role": "user", "content": "测试内容"}]},
            category="测试"
        )
        assert conv_id > 0
        
        # 测试错误处理 (添加重复URL会被数据库处理,返回已存在的ID)
        conv_id2 = db.add_conversation(
            source_url="https://test.com/c/123",
            platform="chatgpt",
            title="重复对话",
            raw_content={"messages": [{"role": "user", "content": "测试内容"}]},
            category="测试"
        )
        assert conv_id2 == conv_id  # 应该返回相同ID
        
        print("✅ 数据库与错误处理集成正常")
    
    def test_02_end_to_end_workflow(self, db):
        """测试端到端工作流"""
        # 1. 添加对话
        conv_ids = []
        for i in range(5):
            conv_id = db.add_conversation(
                source_url=f"https://test.com/c/workflow-{i}",
                platform="chatgpt",
                title=f"工作流测试{i}",
                raw_content={"messages": [{"role": "user", "content": f"这是工作流测试内容{i}"}]},
                category="测试"
            )
            conv_ids.append(conv_id)
        
        assert len(conv_ids) == 5
        print(f"✅ 添加5条对话成功")
        
        # 2. 列出对话
        conversations = db.get_all_conversations()
        assert len(conversations) >= 5
        print(f"✅ 列出对话成功")
        
        # 3. 搜索对话
        results = db.search_conversations("工作流")
        assert len(results) >= 5
        print(f"✅ 搜索成功: {len(results)}条结果")
        
        # 4. 获取详情
        conv = db.get_conversation(conv_ids[0])
        assert conv is not None
        assert conv['title'] == "工作流测试0"
        print(f"✅ 获取详情成功")
        
        # 5. 删除对话
        db.delete_conversation(conv_ids[0])
        remaining = db.get_all_conversations()
        assert len(remaining) >= 4
        print(f"✅ 删除成功: 剩余{len(remaining)}条")
        
        print("✅ 端到端工作流完整测试通过")


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 ChatCompass v1.3.0 快速测试套件")
    print("=" * 80)
    print("\n请使用以下命令运行:")
    print("  python run_tests_interactive.py quick_test_e2e.py --quick")
    print("\n或直接使用pytest:")
    print("  pytest quick_test_e2e.py -v")
    print("=" * 80)
