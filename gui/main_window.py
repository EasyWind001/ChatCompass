"""
MainWindow - ChatCompass主窗口

主要功能:
- 对话列表显示
- 搜索和过滤
- 添加/查看/删除对话
- 系统托盘集成
- 剪贴板监控
"""
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QSplitter, QMessageBox,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from config import get_storage
from gui.conversation_list import ConversationList
from gui.detail_panel import DetailPanel
from gui.dialogs.add_dialog import AddDialog
from gui.clipboard_monitor import ClipboardMonitor
from gui.system_tray import SystemTray
from gui.task_manager import TaskManager
from gui.widgets.progress_widget import ProgressWidget
from gui.widgets.search_bar import SearchBar
from gui.error_handler import handle_error, handle_warning


class MainWindow(QMainWindow):
    """ChatCompass主窗口"""
    
    # Signals
    conversation_added = pyqtSignal(dict)  # 对话添加信号
    conversation_deleted = pyqtSignal(int)  # 对话删除信号
    
    def __init__(self, db_path: Optional[str] = None, db=None, parent=None, 
                 enable_tray: bool = True, enable_monitor: bool = True,
                 enable_async: bool = True):
        """
        初始化主窗口
        
        Args:
            db_path: 数据库路径 (可选)
            db: 数据库对象 (可选,用于测试)
            parent: 父窗口
            enable_tray: 是否启用系统托盘
            enable_monitor: 是否启用剪贴板监控
            enable_async: 是否启用异步任务队列
        """
        super().__init__(parent)
        
        # 数据库连接
        if db is not None:
            self.db = db  # 直接使用传入的db对象(测试用)
        elif db_path:
            self.db = get_storage(db_path)
        else:
            self.db = get_storage()
        
        # 组件引用
        self.clipboard_monitor: Optional[ClipboardMonitor] = None
        self.system_tray: Optional[SystemTray] = None
        self.task_manager: Optional[TaskManager] = None
        self.progress_widget: Optional[ProgressWidget] = None
        self.enable_tray = enable_tray
        self.enable_monitor = enable_monitor
        self.enable_async = enable_async
        
        # 设置窗口属性
        self.setWindowTitle("ChatCompass - AI对话知识库")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)
        
        # 初始化UI
        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._connect_signals()
        
        # 初始化监控和托盘
        self._init_monitor()
        self._init_tray()
        self._init_task_manager()
        
        # 加载数据
        self.refresh_list()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 搜索栏
        self.search_bar = SearchBar()
        main_layout.addWidget(self.search_bar)
        
        # 分割器 (列表 | 详情)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 对话列表
        self.conversation_list = ConversationList(self.db)
        splitter.addWidget(self.conversation_list)
        
        # 详情面板
        self.detail_panel = DetailPanel(self.db)
        splitter.addWidget(self.detail_panel)
        
        # 设置分割比例 (60% : 40%)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
        
    def _create_actions(self):
        """创建操作"""
        # 文件菜单操作
        self.add_action = QAction("添加对话(&A)", self)
        self.add_action.setShortcut(QKeySequence("Ctrl+N"))
        self.add_action.setStatusTip("添加新的AI对话")
        self.add_action.triggered.connect(self.show_add_dialog)
        
        self.import_action = QAction("批量导入(&I)", self)
        self.import_action.setShortcut(QKeySequence("Ctrl+I"))
        self.import_action.setStatusTip("从文件批量导入对话")
        # TODO: connect signal
        
        self.export_action = QAction("导出(&E)", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.setStatusTip("导出选中的对话")
        # TODO: connect signal
        
        self.quit_action = QAction("退出(&Q)", self)
        self.quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.quit_action.setStatusTip("退出程序")
        self.quit_action.triggered.connect(self.close)
        
        # 编辑菜单操作
        self.search_action = QAction("搜索(&S)", self)
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.search_action.setStatusTip("搜索对话")
        # TODO: focus search box
        
        self.delete_action = QAction("删除(&D)", self)
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.setStatusTip("删除选中的对话")
        # TODO: connect signal
        
        # 视图菜单操作
        self.refresh_action = QAction("刷新(&R)", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.setStatusTip("刷新对话列表")
        self.refresh_action.triggered.connect(self.refresh_list)
        
        self.table_view_action = QAction("表格视图(&T)", self)
        self.table_view_action.setCheckable(True)
        self.table_view_action.setChecked(True)
        # TODO: switch view mode
        
        self.card_view_action = QAction("卡片视图(&C)", self)
        self.card_view_action.setCheckable(True)
        # TODO: switch view mode
        
        # 帮助菜单操作
        self.help_action = QAction("帮助文档(&H)", self)
        self.help_action.setShortcut(QKeySequence("F1"))
        # TODO: open help
        
        self.about_action = QAction("关于(&A)", self)
        self.about_action.triggered.connect(self.show_about)
        
    def _create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction(self.add_action)
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        edit_menu.addAction(self.search_action)
        edit_menu.addAction(self.delete_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        view_menu.addAction(self.refresh_action)
        view_menu.addSeparator()
        view_menu.addAction(self.table_view_action)
        view_menu.addAction(self.card_view_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 查看错误日志
        view_errors_action = QAction("查看错误日志", self)
        view_errors_action.triggered.connect(self.show_error_viewer)
        help_menu.addAction(view_errors_action)
        
        help_menu.addAction(self.help_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)
        
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # 添加按钮
        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.refresh_action)
        
        self.toolbar.addSeparator()
        
        # 搜索框
        search_label = QLabel("搜索:")
        self.toolbar.addWidget(search_label)
        
        self.search_widget = QLineEdit()
        self.search_widget.setPlaceholderText("输入关键词搜索...")
        self.search_widget.setMinimumWidth(200)
        self.search_widget.returnPressed.connect(self._on_search)
        self.toolbar.addWidget(self.search_widget)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self._on_search)
        self.toolbar.addWidget(search_btn)
        
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # 统计标签
        self.stats_label = QLabel("总计: 0 条对话")
        self.statusbar.addPermanentWidget(self.stats_label)
        
        # 更新统计
        self._update_stats()
        
    def _connect_signals(self):
        """连接信号"""
        # 列表选择变化 -> 更新详情面板
        self.conversation_list.conversation_selected.connect(
            self.detail_panel.show_conversation
        )
        
        # 对话添加 -> 刷新列表
        self.conversation_added.connect(lambda: self.refresh_list())
        
        # 对话删除 -> 刷新列表
        self.conversation_deleted.connect(lambda: self.refresh_list())
        
        # 搜索栏信号
        self.search_bar.search_requested.connect(self._on_search_bar)
        self.search_bar.platform_filter_changed.connect(self._on_platform_filter)
        self.search_bar.clear_search.connect(self.refresh_list)
        
    def show_add_dialog(self):
        """显示添加对话框"""
        dialog = AddDialog(self.db, self)
        if dialog.exec():
            # 对话添加成功
            conversation = dialog.get_conversation()
            if conversation:
                self.conversation_added.emit(conversation)
                self.statusBar().showMessage(
                    f"✅ 成功添加: {conversation.get('title', 'Unknown')}", 
                    3000
                )
    
    def _on_clipboard_conversation_added(self, conversation: dict):
        """处理从剪贴板监控添加的对话"""
        # 刷新列表
        self.refresh_list()
        # 显示提示
        self.statusBar().showMessage(
            f"✅ 通过剪贴板添加: {conversation.get('title', 'Unknown')}", 
            5000
        )
                
    def refresh_list(self):
        """刷新对话列表"""
        try:
            conversations = self.db.get_all_conversations()
            self.conversation_list.load_conversations(conversations)
            self._update_stats()
        except Exception as e:
            handle_error(
                e,
                parent=self,
                user_message="刷新对话列表失败,请检查数据库连接"
            )
            
    def search_conversations(self, keyword: str):
        """
        搜索对话
        
        Args:
            keyword: 搜索关键词
        """
        try:
            if not keyword.strip():
                # 空关键词,显示所有对话
                self.refresh_list()
                return
                
            results = self.db.search_conversations(keyword)
            self.conversation_list.load_conversations(results)
            
            self.statusBar().showMessage(
                f"🔍 找到 {len(results)} 条结果",
                3000
            )
        except Exception as e:
            handle_error(
                e,
                parent=self,
                user_message=f"搜索关键词'{keyword}'失败,请重试"
            )
            
    def _on_search(self):
        """搜索按钮点击处理"""
        keyword = self.search_widget.text()
        self.search_conversations(keyword)
    
    def _on_search_bar(self, keyword: str):
        """搜索栏搜索处理"""
        if not keyword.strip():
            self.refresh_list()
        else:
            self.conversation_list.filter_by_title(keyword)
            self.statusBar().showMessage(f"🔍 搜索: {keyword}", 2000)
    
    def _on_platform_filter(self, platform: str):
        """平台过滤处理"""
        if not platform:
            self.refresh_list()
        else:
            self.conversation_list.filter_by_platform(platform)
            self.statusBar().showMessage(f"🔍 平台: {platform}", 2000)
        
    def _update_stats(self):
        """更新统计信息"""
        try:
            stats = self.db.get_stats()
            total = stats.get('total', 0)
            self.stats_label.setText(f"总计: {total} 条对话")
        except Exception:
            self.stats_label.setText("总计: 0 条对话")
    
    def delete_conversation(self):
        """删除选中的对话"""
        selected = self.conversation_list.get_selected_conversation()
        if not selected:
            handle_warning("请先选择要删除的对话", parent=self)
            return
        
        conv_id = selected.get('id')
        title = selected.get('title', 'Unknown')
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除对话:\n{title}\n\n此操作不可恢复!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_conversation(conv_id)
                self.conversation_deleted.emit(conv_id)
                self.statusBar().showMessage(f"✅ 已删除: {title}", 3000)
                # 清空详情面板
                self.detail_panel._clear()
            except Exception as e:
                handle_error(
                    e,
                    parent=self,
                    user_message=f"删除对话'{title}'失败,请重试"
                )
            
    def show_error_viewer(self):
        """显示错误查看器"""
        from gui.dialogs.error_viewer import ErrorViewerDialog
        dialog = ErrorViewerDialog(self)
        dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 ChatCompass",
            "<h3>ChatCompass v1.3.0</h3>"
            "<p>AI对话知识库管理系统</p>"
            "<p>功能特性:</p>"
            "<ul>"
            "<li>✅ 多平台支持 (ChatGPT/Claude/DeepSeek)</li>"
            "<li>✅ 智能搜索和上下文定位</li>"
            "<li>✅ 系统托盘监控</li>"
            "<li>✅ 异步爬取队列</li>"
            "</ul>"
            "<p><b>开源协议:</b> MIT License</p>"
            "<p><b>项目地址:</b> <a href='https://github.com/yourusername/ChatCompass'>GitHub</a></p>"
        )
        
    def _init_monitor(self):
        """初始化剪贴板监控"""
        if not self.enable_monitor:
            return
        
        self.clipboard_monitor = ClipboardMonitor(self.db)
        # 连接信号: 当通过剪贴板监控添加对话时，刷新列表
        self.clipboard_monitor.conversation_added.connect(self._on_clipboard_conversation_added)
        self.clipboard_monitor.start()
        self.statusBar().showMessage("✅ 剪贴板监控已启动", 2000)
        
    def _init_tray(self):
        """初始化系统托盘"""
        if not self.enable_tray:
            return
        
        from PyQt6.QtWidgets import QApplication
        self.system_tray = SystemTray(QApplication.instance())
        
        # 连接信号
        self.system_tray.show_window.connect(self.show_and_activate)
        self.system_tray.quit_app.connect(self.quit_app)
        self.system_tray.toggle_monitor.connect(self.toggle_monitor)
        
        self.system_tray.show()
        self.statusBar().showMessage("✅ 系统托盘已启动", 2000)
    
    def _init_task_manager(self):
        """初始化任务管理器"""
        if not self.enable_async:
            return
        
        self.task_manager = TaskManager(self.db, max_workers=3)
        
        # 创建进度组件
        self.progress_widget = ProgressWidget()
        
        # 连接信号
        self.task_manager.task_added.connect(self.on_task_added)
        self.task_manager.task_progress.connect(self.on_task_progress)
        self.task_manager.task_completed.connect(self.on_task_completed)
        self.task_manager.task_failed.connect(self.on_task_failed)
        
        self.progress_widget.cancel_task.connect(self.task_manager.cancel_task)
        self.progress_widget.clear_all.connect(self.task_manager.clear_completed)
        
        # 启动管理器
        self.task_manager.start()
        
        self.statusBar().showMessage("✅ 异步任务队列已启动", 2000)
    
    def on_task_added(self, task_id: str, url: str):
        """任务添加事件"""
        if self.progress_widget:
            self.progress_widget.add_task(task_id, url)
            # 显示进度组件
            if not self.progress_widget.isVisible():
                self.progress_widget.show()
    
    def on_task_progress(self, task_id: str, progress: int, message: str):
        """任务进度事件"""
        if self.progress_widget:
            self.progress_widget.update_progress(task_id, progress, message)
    
    def on_task_completed(self, task_id: str, result: dict):
        """任务完成事件"""
        if self.progress_widget:
            self.progress_widget.complete_task(task_id, success=True)
        
        # 刷新列表
        self.refresh_list()
        self.statusBar().showMessage(f"✅ 对话添加成功: {result.get('title', '未知')}", 5000)
    
    def on_task_failed(self, task_id: str, error: str):
        """任务失败事件"""
        if self.progress_widget:
            self.progress_widget.complete_task(task_id, success=False)
        
        self.statusBar().showMessage(f"❌ 任务失败: {error}", 5000)
    
    def show_and_activate(self):
        """显示并激活窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def toggle_monitor(self, enabled: bool):
        """切换剪贴板监控"""
        if not self.clipboard_monitor:
            return
        
        if enabled:
            self.clipboard_monitor.start()
            self.statusBar().showMessage("✅ 剪贴板监控已启用", 3000)
        else:
            self.clipboard_monitor.stop()
            self.statusBar().showMessage("⏸️ 剪贴板监控已禁用", 3000)
    
    def quit_app(self):
        """退出应用"""
        # 停止任务管理器
        if self.task_manager:
            self.task_manager.stop()
        
        # 停止监控
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        
        # 隐藏托盘
        if self.system_tray:
            self.system_tray.hide()
        
        # 关闭进度组件
        if self.progress_widget:
            self.progress_widget.close()
        
        # 退出
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.system_tray and self.system_tray.tray_icon.isVisible():
            # 最小化到托盘
            self.hide()
            self.system_tray.show_message(
                "ChatCompass",
                "应用已最小化到系统托盘",
                duration=2000
            )
            event.ignore()
        else:
            # 直接退出
            self.quit_app()
            event.accept()
