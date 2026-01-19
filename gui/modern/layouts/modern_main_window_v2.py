"""
现代化主窗口 V2 - 内嵌搜索 + 搜索结果展示 + 抓取队列
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFrame, QPushButton, QLabel, QScrollArea, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QShortcut, QKeySequence

# 尝试导入WebEngine
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("警告: PyQt6-WebEngine未安装,将使用QTextEdit替代")

from ..widgets.conversation_grid import ConversationGrid
from ..widgets.conversation_list import ConversationList
from ..widgets.search_result_item import SearchResultItem
from ..widgets.search_result_compact import SearchResultCompactItem
from ..widgets.scraping_status_panel import ScrapingStatusPanel
from ..widgets.add_dialog import AddDialog
from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Sizes, Spacing, BorderRadius


class ModernMainWindow(QMainWindow):
    """现代化主窗口 V2"""
    
    def __init__(self, database_manager=None):
        """初始化主窗口"""
        super().__init__()
        self.db_manager = database_manager
        self._drag_pos = None
        self._view_mode = 'grid'  # 'grid' or 'list'
        self._search_mode = False  # 是否在搜索模式
        self._search_expanded = False  # 搜索结果是否展开为详情
        self._search_results = []  # 搜索结果数据
        self._test_conversations = []
        self._current_matches = []  # 当前搜索匹配位置
        self._current_match_index = 0
        self._init_ui()
        self._apply_styles()
    
    def _create_title_bar(self) -> QFrame:
        """创建自定义标题栏 - 简化版"""
        colors = get_color_scheme()
        
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_secondary')};
                border-bottom: 1px solid {colors.get('border_default')};
            }}
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(12)
        
        # Logo
        logo_label = QLabel("🧭 ChatCompass")
        logo_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {colors.get('fg_primary')};
        """)
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        # 视图切换
        self.view_btn = QPushButton("📋 列表")
        self.view_btn.setFixedHeight(32)
        self.view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.get('fg_secondary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
            }}
        """)
        self.view_btn.clicked.connect(self._on_view_toggle)
        layout.addWidget(self.view_btn)
        
        # 最小化按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(44, 36)
        min_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.get('fg_secondary')};
                border: none;
                border-radius: 6px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_hover')};
            }}
        """)
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(44, 36)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.get('fg_secondary')};
                border: none;
                border-radius: 6px;
                font-size: 28px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('error')};
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # 启用拖动
        title_bar.mousePressEvent = self._title_bar_mouse_press
        title_bar.mouseMoveEvent = self._title_bar_mouse_move
        
        return title_bar
    
    def _create_search_bar(self) -> QWidget:
        """创建搜索栏"""
        colors = get_color_scheme()
        
        search_widget = QWidget()
        search_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('bg_secondary')};
                border-bottom: 1px solid {colors.get('border_default')};
            }}
        """)
        
        layout = QHBoxLayout(search_widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索对话标题、内容...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors.get('primary')};
            }}
        """)
        self.search_input.returnPressed.connect(self._perform_search)
        layout.addWidget(self.search_input, stretch=1)
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setFixedSize(80, 40)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
        """)
        search_btn.clicked.connect(self._perform_search)
        layout.addWidget(search_btn)
        
        # 清除按钮
        clear_btn = QPushButton("清除")
        clear_btn.setFixedSize(80, 40)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
            }}
        """)
        clear_btn.clicked.connect(self._clear_search)
        layout.addWidget(clear_btn)
        
        # 添加按钮
        add_btn = QPushButton("➕ 添加")
        add_btn.setFixedSize(100, 40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('success')};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #22C55E;
            }}
        """)
        add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(add_btn)
        
        return search_widget
    
    def _create_search_results_container(self) -> QWidget:
        """创建搜索结果容器"""
        colors = get_color_scheme()
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {colors.get('bg_primary')};
                border: none;
            }}
        """)
        
        # 结果列表容器
        results_widget = QWidget()
        self.search_results_layout = QVBoxLayout(results_widget)
        self.search_results_layout.setSpacing(Spacing.MD)
        self.search_results_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        self.search_results_layout.addStretch()
        
        scroll_area.setWidget(results_widget)
        layout.addWidget(scroll_area)
        
        container.hide()  # 默认隐藏
        return container
    
    def _create_detail_panel(self) -> QWidget:
        """创建详情面板"""
        colors = get_color_scheme()
        
        detail_container = QWidget()
        layout = QVBoxLayout(detail_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 摘要信息区
        summary_widget = QWidget()
        summary_widget.setFixedHeight(180)
        summary_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('bg_card')};
                border-bottom: 1px solid {colors.get('border_default')};
            }}
        """)
        
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(24, 16, 24, 16)
        summary_layout.setSpacing(12)
        
        # 标题
        self.detail_title = QLabel("选择对话查看详情")
        self.detail_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {colors.get('fg_primary')};
        """)
        summary_layout.addWidget(self.detail_title)
        
        # 元信息
        meta_container = QWidget()
        meta_layout = QHBoxLayout(meta_container)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(16)
        
        self.detail_platform = QLabel()
        self.detail_platform.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        meta_layout.addWidget(self.detail_platform)
        
        self.detail_time = QLabel()
        self.detail_time.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        meta_layout.addWidget(self.detail_time)
        
        self.detail_count = QLabel()
        self.detail_count.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        meta_layout.addWidget(self.detail_count)
        
        meta_layout.addStretch()
        summary_layout.addWidget(meta_container)
        
        # 导航按钮(搜索模式下显示)
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        
        self.match_info_label = QLabel()
        self.match_info_label.setStyleSheet(f"color: {colors.get('primary')}; font-weight: 500;")
        nav_layout.addWidget(self.match_info_label)
        
        self.prev_match_btn = QPushButton("⬆ 上一个")
        self.prev_match_btn.setFixedHeight(28)
        self.prev_match_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
                border-color: {colors.get('primary')};
            }}
        """)
        self.prev_match_btn.clicked.connect(self._prev_match)
        nav_layout.addWidget(self.prev_match_btn)
        
        self.next_match_btn = QPushButton("⬇ 下一个")
        self.next_match_btn.setFixedHeight(28)
        self.next_match_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
                border-color: {colors.get('primary')};
            }}
        """)
        self.next_match_btn.clicked.connect(self._next_match)
        nav_layout.addWidget(self.next_match_btn)
        
        nav_layout.addStretch()
        nav_container.hide()  # 默认隐藏
        self.nav_container = nav_container
        summary_layout.addWidget(nav_container)
        
        # 链接按钮
        self.detail_link_btn = QPushButton("🔗 打开原始链接")
        self.detail_link_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
        """)
        self.detail_link_btn.hide()
        summary_layout.addWidget(self.detail_link_btn)
        
        summary_layout.addStretch()
        layout.addWidget(summary_widget)
        
        # 原始内容区
        if HAS_WEBENGINE:
            self.detail_content = QWebEngineView()
            self.detail_content.setStyleSheet(f"""
                QWebEngineView {{
                    background-color: {colors.get('bg_card')};
                    border: none;
                }}
            """)
            self.detail_content.setHtml(f"""
                <html><body style="font-family: sans-serif; padding: 40px 24px; 
                background-color: {colors.get('bg_card')}; color: {colors.get('fg_secondary')};">
                <p style="text-align: center;">👈 点击左侧对话查看详情</p>
                </body></html>
            """)
        else:
            self.detail_content = QTextEdit()
            self.detail_content.setReadOnly(True)
            self.detail_content.setPlaceholderText("点击左侧对话查看详情...")
            self.detail_content.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {colors.get('bg_card')};
                    color: {colors.get('fg_primary')};
                    border: none;
                    padding: 24px;
                }}
            """)
        
        layout.addWidget(self.detail_content)
        
        return detail_container
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("ChatCompass - AI对话知识库")
        self.setFixedSize(1600, 900)  # 增加宽度以容纳抓取面板
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        # 搜索栏
        self.search_bar = self._create_search_bar()
        main_layout.addWidget(self.search_bar)
        
        # 内容区 - 三栏布局
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 左侧: 对话列表/搜索结果
        self.left_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.left_splitter.setHandleWidth(1)
        
        # 对话视图容器
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        self.conversation_grid = ConversationGrid()
        self.conversation_grid.conversation_selected.connect(self._on_conversation_selected)
        self.conversation_grid.star_toggled.connect(self._on_star_toggled)
        
        self.conversation_list = ConversationList()
        self.conversation_list.conversation_selected.connect(self._on_conversation_selected)
        self.conversation_list.star_toggled.connect(self._on_star_toggled)
        self.conversation_list.hide()
        
        self.search_results_container = self._create_search_results_container()
        
        left_layout.addWidget(self.conversation_grid)
        left_layout.addWidget(self.conversation_list)
        left_layout.addWidget(self.search_results_container)
        
        self.left_splitter.addWidget(left_container)
        
        # 中间: 详情面板
        self.detail_panel = self._create_detail_panel()
        self.left_splitter.addWidget(self.detail_panel)
        
        # 初始比例
        self.left_splitter.setSizes([320, 1080])
        self.left_splitter.setStretchFactor(0, 0)
        self.left_splitter.setStretchFactor(1, 1)
        
        content_layout.addWidget(self.left_splitter, stretch=1)
        
        # 右侧: 抓取状态面板
        self.scraping_panel = ScrapingStatusPanel()
        self.scraping_panel.task_cancelled.connect(self._on_task_cancelled)
        content_layout.addWidget(self.scraping_panel)
        
        main_layout.addWidget(content_container)
        
        # 加载测试数据
        self._load_test_data()
        
        # 设置键盘快捷键
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """设置键盘快捷键"""
        # Ctrl+F: 聚焦搜索框
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._focus_search)
        
        # Esc: 清除搜索/退出搜索模式
        esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        esc_shortcut.activated.connect(self._on_esc_pressed)
        
        # Ctrl+G: 切换视图模式
        view_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        view_shortcut.activated.connect(self._on_view_toggle)
        
        # Ctrl+N: 添加对话
        add_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        add_shortcut.activated.connect(self._on_add_clicked)
        
        # Ctrl+Down/Up: 导航搜索匹配
        next_shortcut = QShortcut(QKeySequence("Ctrl+Down"), self)
        next_shortcut.activated.connect(self._next_match)
        
        prev_shortcut = QShortcut(QKeySequence("Ctrl+Up"), self)
        prev_shortcut.activated.connect(self._prev_match)
        
        # 快捷键设置完成（静默模式，不打印）
        # print("快捷键已设置: Ctrl+F搜索, Esc清除, Ctrl+G切换视图, Ctrl+N添加, Ctrl+↑/↓导航")
    
    def _focus_search(self):
        """聚焦搜索框"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def _on_esc_pressed(self):
        """ESC键处理"""
        if self._search_mode:
            # 搜索模式下：清除搜索
            self._clear_search()
        elif self.search_input.text():
            # 有搜索文本但未搜索：清空输入框
            self.search_input.clear()
        else:
            # 其他情况：取消焦点
            self.search_input.clearFocus()
    
    def _apply_styles(self):
        """应用样式"""
        colors = get_color_scheme()
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors.get('bg_primary')};
            }}
            QSplitter::handle {{
                background-color: {colors.get('border_default')};
            }}
            QSplitter::handle:hover {{
                background-color: {colors.get('border_hover')};
            }}
        """)
    
    def _load_test_data(self):
        """加载测试数据"""
        from datetime import datetime, timedelta
        
        self._test_conversations = []
        platforms = ['ChatGPT', 'Claude', 'DeepSeek']
        categories = ['编程', '写作', '学习', '翻译', '其他']
        
        for i in range(12):
            messages = []
            for j in range(3):
                messages.extend([
                    {'role': 'user', 'content': f'用户消息 {j+1}：如何优化Python代码性能？'},
                    {'role': 'assistant', 'content': f'助手回复 {j+1}：可以使用多种方法优化Python性能...'}
                ])
            
            conv = {
                'id': i + 1,
                'title': f'测试对话 {i+1}: Python开发相关问题讨论',
                'platform': platforms[i % 3],
                'summary': '这是一段关于Python编程的对话内容，讨论了关于数据处理、算法优化和最佳实践等话题...',
                'message_count': (i + 1) * 3,
                'created_at': datetime.now() - timedelta(days=i),
                'starred': i % 4 == 0,
                'category': categories[i % 5],
                'messages': messages
            }
            self._test_conversations.append(conv)
        
        self.conversation_grid.load_conversations(self._test_conversations)
        self.conversation_list.load_conversations(self._test_conversations)
    
    def _perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        print(f"搜索: {query}")
        self._search_mode = True
        
        # 隐藏网格/列表，显示搜索结果
        self.conversation_grid.hide()
        self.conversation_list.hide()
        self.search_results_container.show()
        
        # 详情区域和抓取队列都收起，列表区域最大化
        # 注意：抓取队列面板在content_layout中，不在splitter里
        self.left_splitter.setSizes([1350, 50])
        self.scraping_panel.setFixedWidth(50)  # 临时缩小
        if not self.scraping_panel._collapsed:
            self.scraping_panel._on_toggle_clicked()  # 自动收起
        
        # 清空旧结果
        while self.search_results_layout.count() > 1:
            item = self.search_results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 模拟搜索结果
        results = []
        for conv in self._test_conversations:
            if query.lower() in conv['title'].lower() or query.lower() in conv['summary'].lower():
                # 模拟匹配上下文
                matches = [
                    {'context': f'...{query}相关的内容在这里...这是第一处匹配...', 'position': 100},
                    {'context': f'...另一处包含{query}的段落...这是第二处匹配...', 'position': 300},
                    {'context': f'...还有一个{query}的地方...第三处...', 'position': 500},
                ]
                results.append({'conversation': conv, 'matches': matches})
        
        # 保存搜索结果
        self._search_results = results
        self._search_expanded = False
        
        # 显示完整搜索结果(带匹配上下文)
        for result in results:
            item = SearchResultItem(result['conversation'], result['matches'])
            item.clicked.connect(self._on_search_result_clicked)
            item.expand_clicked.connect(self._on_expand_search_result)
            self.search_results_layout.insertWidget(self.search_results_layout.count() - 1, item)
        
        print(f"找到 {len(results)} 个结果")
    
    def _clear_search(self):
        """清除搜索"""
        print("清除搜索")
        self.search_input.clear()
        self._search_mode = False
        
        # 隐藏搜索结果，显示网格/列表
        self.search_results_container.hide()
        if self._view_mode == 'grid':
            self.conversation_grid.show()
        else:
            self.conversation_list.show()
        
        # 恢复布局比例
        self.left_splitter.setSizes([320, 1080])
        # 恢复抓取队列宽度
        if self.scraping_panel._collapsed:
            self.scraping_panel.setFixedWidth(50)
        else:
            self.scraping_panel.setFixedWidth(300)
        
        # 隐藏导航按钮
        self.nav_container.hide()
    
    def _on_search_result_clicked(self, conversation: dict):
        """搜索结果被点击 - 不展开详情"""
        print(f"点击搜索结果: {conversation['title']}")
    
    def _on_expand_search_result(self, conversation: dict):
        """展开搜索结果到详情"""
        print(f"展开搜索结果: {conversation['title']}")
        
        # 恢复详情区域
        self.left_splitter.setSizes([320, 1080])
        
        # 显示对话详情
        self._show_conversation_detail(conversation, search_mode=True)
    
    def _show_conversation_detail(self, conversation: dict, search_mode=False):
        """显示对话详情"""
        self.detail_title.setText(conversation['title'])
        self.detail_platform.setText(f"📱 {conversation['platform']}")
        self.detail_time.setText(f"🕒 {conversation['created_at']}")
        self.detail_count.setText(f"💬 {conversation['message_count']} 条消息")
        
        if search_mode:
            # 搜索模式：显示导航按钮
            query = self.search_input.text().strip()
            self._current_matches = [100, 300, 500]  # 模拟匹配位置
            self._current_match_index = 0
            self.match_info_label.setText(f"🔍 匹配 1/{len(self._current_matches)}")
            self.nav_container.show()
        else:
            # 普通模式：隐藏导航按钮
            self.nav_container.hide()
        
        # 渲染对话内容
        if HAS_WEBENGINE:
            html = self._generate_conversation_html(conversation, search_mode)
            self.detail_content.setHtml(html)
    
    def _generate_conversation_html(self, conversation: dict, search_mode=False) -> str:
        """生成对话HTML"""
        colors = get_color_scheme()
        query = self.search_input.text().strip() if search_mode else ""
        
        messages_html = ""
        for i, msg in enumerate(conversation.get('messages', [])[:5]):
            content = msg['content']
            # 高亮匹配
            if query and query.lower() in content.lower():
                content = content.replace(query, f'<mark style="background-color: #FEF08A; padding: 2px 4px; border-radius: 3px;">{query}</mark>')
            
            role_class = msg['role']
            avatar = '👤' if msg['role'] == 'user' else '🤖'
            role_name = '用户' if msg['role'] == 'user' else '助手'
            
            messages_html += f"""
                <div class="message {role_class}" id="msg-{i}">
                    <div class="avatar">{avatar}</div>
                    <div class="content">
                        <div class="role">{role_name}</div>
                        <div class="text">{content}</div>
                    </div>
                </div>
            """
        
        return f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                        background-color: {colors.get('bg_card')};
                        color: {colors.get('fg_primary')};
                        padding: 24px;
                        line-height: 1.6;
                    }}
                    .message {{
                        display: flex;
                        gap: 12px;
                        margin-bottom: 24px;
                        animation: fadeIn 0.3s ease;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                    .avatar {{
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 20px;
                        flex-shrink: 0;
                    }}
                    .user .avatar {{ background-color: {colors.get('primary')}; }}
                    .assistant .avatar {{ background-color: {colors.get('success')}; }}
                    .content {{ flex: 1; }}
                    .role {{
                        font-weight: 600;
                        margin-bottom: 6px;
                        color: {colors.get('fg_secondary')};
                        font-size: 14px;
                    }}
                    .text {{
                        background-color: {colors.get('bg_hover')};
                        padding: 12px 16px;
                        border-radius: 8px;
                        font-size: 15px;
                    }}
                    .assistant .text {{ background-color: {colors.get('bg_active')}; }}
                </style>
            </head>
            <body>
                {messages_html}
            </body>
            </html>
        """
    
    def _prev_match(self):
        """上一个匹配"""
        if self._current_matches:
            self._current_match_index = (self._current_match_index - 1) % len(self._current_matches)
            self.match_info_label.setText(f"🔍 匹配 {self._current_match_index + 1}/{len(self._current_matches)}")
            print(f"跳转到匹配 {self._current_match_index + 1}")
    
    def _next_match(self):
        """下一个匹配"""
        if self._current_matches:
            self._current_match_index = (self._current_match_index + 1) % len(self._current_matches)
            self.match_info_label.setText(f"🔍 匹配 {self._current_match_index + 1}/{len(self._current_matches)}")
            print(f"跳转到匹配 {self._current_match_index + 1}")
    
    def _on_conversation_selected(self, conversation: dict):
        """对话选中"""
        print(f"选中对话: {conversation['title']}")
        self._show_conversation_detail(conversation, search_mode=False)
    
    def _on_star_toggled(self, conv_id: int, starred: bool):
        """收藏切换"""
        print(f"对话 {conv_id} 收藏: {starred}")
    
    def _on_view_toggle(self):
        """视图切换"""
        if self._search_mode:
            return  # 搜索模式下不允许切换
        
        if self._view_mode == 'grid':
            self._view_mode = 'list'
            self.conversation_grid.hide()
            self.conversation_list.show()
            self.view_btn.setText("🎨 网格")
            print("切换到列表视图")
        else:
            self._view_mode = 'grid'
            self.conversation_list.hide()
            self.conversation_grid.show()
            self.view_btn.setText("📋 列表")
            print("切换到网格视图")
    
    def _on_add_clicked(self):
        """添加对话"""
        print("打开添加对话框")
        dialog = AddDialog(self)
        dialog.conversation_added.connect(self._on_conversation_added)
        dialog.exec()
    
    def _on_conversation_added(self, conv_data: dict):
        """对话添加完成"""
        print(f"添加对话: {conv_data}")
        
        # 添加到抓取队列
        import uuid
        task = {
            'id': str(uuid.uuid4()),
            'url': conv_data.get('url'),
            'platform': conv_data.get('platform'),
            'status': 'running',
            'progress': 50
        }
        self.scraping_panel.add_task(task)
    
    def _on_task_cancelled(self, task_id: str):
        """取消抓取任务"""
        print(f"取消任务: {task_id}")
        self.scraping_panel.remove_task(task_id)
    
    def _title_bar_mouse_press(self, event: QMouseEvent):
        """标题栏鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def _title_bar_mouse_move(self, event: QMouseEvent):
        """标题栏鼠标移动"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
