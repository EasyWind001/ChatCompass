"""
MainWindow - ChatCompass主窗口

主要功能:
- 对话列表显示
- 搜索和过滤
- 添加/查看/删除对话
- 系统托盘集成
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


class MainWindow(QMainWindow):
    """ChatCompass主窗口"""
    
    # Signals
    conversation_added = pyqtSignal(dict)  # 对话添加信号
    conversation_deleted = pyqtSignal(int)  # 对话删除信号
    
    def __init__(self, db_path: Optional[str] = None, parent=None):
        """
        初始化主窗口
        
        Args:
            db_path: 数据库路径 (可选)
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 数据库连接
        self.db = get_storage(db_path) if db_path else get_storage()
        
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
        
        # 加载数据
        self.refresh_list()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
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
                
    def refresh_list(self):
        """刷新对话列表"""
        try:
            conversations = self.db.list_conversations()
            self.conversation_list.load_conversations(conversations)
            self._update_stats()
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"刷新列表失败: {str(e)}"
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
            QMessageBox.critical(
                self,
                "错误",
                f"搜索失败: {str(e)}"
            )
            
    def _on_search(self):
        """搜索按钮点击处理"""
        keyword = self.search_widget.text()
        self.search_conversations(keyword)
        
    def _update_stats(self):
        """更新统计信息"""
        try:
            stats = self.db.get_stats()
            total = stats.get('total', 0)
            self.stats_label.setText(f"总计: {total} 条对话")
        except Exception:
            self.stats_label.setText("总计: 0 条对话")
            
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
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        # TODO: 保存窗口状态
        event.accept()
