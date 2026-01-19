"""
现代化主窗口
两栏布局: 单列卡片网格 + 详情面板(摘要+原始内容)
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFrame, QPushButton, QLabel, QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QMouseEvent

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
from ..widgets.scraping_status_panel import ScrapingStatusPanel
from ..widgets.add_dialog import AddDialog
from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Sizes


class ModernTopBar(QFrame):
    """现代化顶栏"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setFixedHeight(Sizes.TOPBAR_HEIGHT)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_secondary')};
                border-bottom: 1px solid {colors.get('border_default')};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # TODO: 实现顶栏内容(Logo, 搜索, 设置等)
        from PyQt6.QtWidgets import QLabel
        logo = QLabel("🧭 ChatCompass")
        logo.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {colors.get('fg_primary')};
        """)
        layout.addWidget(logo)
        layout.addStretch()


class ModernSideNav(QFrame):
    """现代化侧边导航"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setFixedWidth(Sizes.SIDEBAR_WIDTH_EXPANDED)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_secondary')};
                border-right: 1px solid {colors.get('border_default')};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(8)
        
        # TODO: 实现导航项
        from PyQt6.QtWidgets import QPushButton
        
        nav_items = [
            ("📊", "仪表盘"),
            ("💬", "所有对话"),
            ("📁", "分类"),
            ("🏷️", "标签"),
            ("⭐", "收藏"),
        ]
        
        for icon, text in nav_items:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 16px;
                    background: transparent;
                    border: none;
                    color: {colors.get('fg_secondary')};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('bg_hover')};
                    color: {colors.get('fg_primary')};
                }}
            """)
            layout.addWidget(btn)
        
        layout.addStretch()


class ModernMainWindow(QMainWindow):
    """现代化主窗口"""
    
    def __init__(self, database_manager=None):
        """初始化主窗口
        
        Args:
            database_manager: 数据库管理器实例
        """
        super().__init__()
        self.db_manager = database_manager
        self._drag_pos = None  # 用于窗口拖动
        self._view_mode = 'grid'  # 视图模式: 'grid' 或 'list'
        self._test_conversations = []  # 存储测试数据
        self._init_ui()
        self._apply_styles()
    
    def _create_title_bar(self) -> QFrame:
        """创建自定义标题栏
        
        Returns:
            标题栏组件
        """
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
        
        # Logo和标题
        logo_label = QLabel("🧭 ChatCompass")
        logo_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {colors.get('fg_primary')};
        """)
        layout.addWidget(logo_label)
        
        layout.addSpacing(20)
        
        # 搜索按钮
        search_btn = QPushButton("🔍 搜索")
        search_btn.setFixedHeight(32)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
                border-color: {colors.get('primary')};
            }}
        """)
        search_btn.clicked.connect(self._on_search_clicked)
        layout.addWidget(search_btn)
        
        # 添加按钮
        add_btn = QPushButton("➕ 添加")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
        """)
        add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(add_btn)
        
        # 视图切换按钮(列表/网格)
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
        
        layout.addStretch()
        
        # 最小化按钮(加大)
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
        
        # 关闭按钮(加大)
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
        
        # 启用鼠标拖动
        title_bar.mousePressEvent = self._title_bar_mouse_press
        title_bar.mouseMoveEvent = self._title_bar_mouse_move
        
        return title_bar
    
    def _title_bar_mouse_press(self, event: QMouseEvent):
        """标题栏鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def _title_bar_mouse_move(self, event: QMouseEvent):
        """标题栏鼠标移动事件(拖动窗口)"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
    
    def _create_detail_panel(self) -> QWidget:
        """创建详情面板(分为摘要+原始内容)
        
        Returns:
            详情面板组件
        """
        colors = get_color_scheme()
        
        # 容器
        detail_container = QWidget()
        layout = QVBoxLayout(detail_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # === 上部: 摘要信息区 ===
        summary_widget = QWidget()
        summary_widget.setFixedHeight(180)  # 固定高度
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
        
        # 元信息容器
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
        self.detail_link_btn.hide()  # 默认隐藏
        summary_layout.addWidget(self.detail_link_btn)
        
        summary_layout.addStretch()
        
        layout.addWidget(summary_widget)
        
        # === 下部: 原始内容区 (使用WebView显示原始HTML) ===
        if HAS_WEBENGINE:
            self.detail_content = QWebEngineView()
            self.detail_content.setStyleSheet(f"""
                QWebEngineView {{
                    background-color: {colors.get('bg_card')};
                    border: none;
                }}
            """)
            
            # 默认显示提示(靠上对齐)
            self.detail_content.setHtml(f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                            margin: 0;
                            padding: 40px 24px;
                            background-color: {colors.get('bg_card')};
                            color: {colors.get('fg_secondary')};
                        }}
                        .placeholder {{
                            text-align: center;
                            font-size: 16px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="placeholder">
                        <p>👈 点击左侧卡片查看对话内容</p>
                    </div>
                </body>
                </html>
            """)
        else:
            # 降级方案: 使用QTextEdit
            self.detail_content = QTextEdit()
            self.detail_content.setReadOnly(True)
            self.detail_content.setPlaceholderText("点击左侧卡片查看对话内容...")
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
        # 固定窗口大小,不可调整
        self.setFixedSize(1400, 900)
        # 无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 中央容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === 自定义标题栏 ===
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        # === 内容区域(两栏布局: 单列网格/列表 + 详情) ===
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.content_splitter.setHandleWidth(1)
        
        # 左侧容器(用于切换网格/列表视图)
        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 创建网格和列表视图
        self.conversation_grid = ConversationGrid()
        self.conversation_grid.conversation_selected.connect(self._on_conversation_selected)
        self.conversation_grid.star_toggled.connect(self._on_star_toggled)
        
        self.conversation_list = ConversationList()
        self.conversation_list.conversation_selected.connect(self._on_conversation_selected)
        self.conversation_list.star_toggled.connect(self._on_star_toggled)
        self.conversation_list.hide()  # 默认隐藏列表视图
        
        left_layout.addWidget(self.conversation_grid)
        left_layout.addWidget(self.conversation_list)
        
        self.content_splitter.addWidget(self.left_container)
        
        # 右侧: 详情面板(分为摘要+原始内容)
        self.detail_panel = self._create_detail_panel()
        self.content_splitter.addWidget(self.detail_panel)
        
        # 调整初始比例 (单列网格:详情 = 320:1080)
        # 单列卡片宽280px + 边距 = 约320px
        self.content_splitter.setSizes([320, 1080])
        self.content_splitter.setStretchFactor(0, 0)  # 左侧固定宽度
        self.content_splitter.setStretchFactor(1, 1)  # 右侧详情可伸缩
        
        main_layout.addWidget(self.content_splitter)
        
        # 加载测试数据
        self._load_test_data()
    
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
        
        # 生成测试对话数据
        self._test_conversations = []
        platforms = ['ChatGPT', 'Claude', 'DeepSeek']
        categories = ['编程', '写作', '学习', '翻译', '其他']
        
        for i in range(12):
            conv = {
                'id': i + 1,
                'title': f'测试对话 {i+1}: Python开发相关问题讨论',
                'platform': platforms[i % 3],
                'summary': '这是一段关于Python编程的对话内容，讨论了关于数据处理、算法优化和最佳实践等话题...',
                'message_count': (i + 1) * 3,
                'created_at': datetime.now() - timedelta(days=i),
                'starred': i % 4 == 0,
                'category': categories[i % 5]
            }
            self._test_conversations.append(conv)
        
        self.conversation_grid.load_conversations(self._test_conversations)
        self.conversation_list.load_conversations(self._test_conversations)
    
    def _on_conversation_selected(self, conversation: dict):
        """对话选中回调"""
        print(f"选中对话: {conversation['title']}")
        
        # 更新摘要信息
        self.detail_title.setText(conversation['title'])
        self.detail_platform.setText(f"📱 {conversation['platform']}")
        self.detail_time.setText(f"🕒 {conversation['created_at']}")
        self.detail_count.setText(f"💬 {conversation['message_count']} 条消息")
        
        # 显示并设置链接按钮
        if 'url' in conversation and conversation['url']:
            self.detail_link_btn.show()
            self.detail_link_btn.clicked.disconnect()  # 断开之前的连接
            self.detail_link_btn.clicked.connect(
                lambda: self._open_url(conversation['url'])
            )
        else:
            self.detail_link_btn.hide()
        
        # 渲染原始对话内容 (模拟HTML内容)
        # TODO: 后续从数据库读取完整HTML内容
        if HAS_WEBENGINE:
            html_content = self._generate_conversation_html(conversation)
            self.detail_content.setHtml(html_content)
        else:
            # 降级方案: 显示纯文本
            text_content = f"=== {conversation['title']} ===\n\n"
            text_content += f"平台: {conversation['platform']}\n"
            text_content += f"消息数: {conversation['message_count']}\n"
            text_content += f"创建时间: {conversation['created_at']}\n\n"
            text_content += "摘要:\n" + conversation.get('summary', '暂无摘要')
            self.detail_content.setPlainText(text_content)
    
    def _generate_conversation_html(self, conversation: dict) -> str:
        """生成对话HTML内容(模拟原始对话)
        
        Args:
            conversation: 对话数据
            
        Returns:
            HTML字符串
        """
        colors = get_color_scheme()
        
        # 模拟对话消息
        messages_html = ""
        for i in range(min(conversation['message_count'], 5)):
            messages_html += f"""
                <div class="message user">
                    <div class="avatar">👤</div>
                    <div class="content">
                        <div class="role">用户</div>
                        <div class="text">这是第 {i+1} 条用户消息...</div>
                    </div>
                </div>
                <div class="message assistant">
                    <div class="avatar">🤖</div>
                    <div class="content">
                        <div class="role">助手</div>
                        <div class="text">这是第 {i+1} 条助手回复...</div>
                    </div>
                </div>
            """
        
        return f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
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
                    .user .avatar {{
                        background-color: {colors.get('primary')};
                    }}
                    .assistant .avatar {{
                        background-color: {colors.get('success')};
                    }}
                    .content {{
                        flex: 1;
                    }}
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
                    .user .text {{
                        background-color: {colors.get('bg_hover')};
                    }}
                    .assistant .text {{
                        background-color: {colors.get('bg_active')};
                    }}
                </style>
            </head>
            <body>
                {messages_html}
                <div style="text-align: center; color: {colors.get('fg_secondary')}; margin-top: 24px;">
                    <p>💡 提示: 后续将从数据库加载完整对话内容</p>
                </div>
            </body>
            </html>
        """
    
    def _open_url(self, url: str):
        """打开原始链接"""
        import webbrowser
        webbrowser.open(url)
    
    def _on_star_toggled(self, conv_id: int, starred: bool):
        """收藏切换回调"""
        print(f"对话 {conv_id} 收藏状态: {starred}")
        # TODO: 更新数据库
    
    def _on_search_clicked(self):
        """搜索按钮点击"""
        print("打开搜索对话框")
        dialog = SearchDialog(self)
        dialog.set_conversations(self._test_conversations)
        dialog.conversation_selected.connect(self._on_conversation_selected)
        dialog.exec()
    
    def _on_add_clicked(self):
        """添加按钮点击"""
        print("打开添加对话框")
        dialog = AddDialog(self)
        dialog.conversation_added.connect(self._on_conversation_added)
        dialog.exec()
    
    def _on_conversation_added(self, conv_data: dict):
        """对话添加完成"""
        print(f"添加对话: {conv_data}")
        # TODO: 调用scraper抓取并保存到数据库
        # 临时添加到列表
        from datetime import datetime
        new_conv = {
            'id': len(self._test_conversations) + 1,
            'title': conv_data.get('title') or '新添加的对话',
            'platform': conv_data.get('platform'),
            'summary': '正在抓取对话内容...',
            'message_count': 0,
            'created_at': datetime.now(),
            'starred': False,
            'category': conv_data.get('category'),
            'url': conv_data.get('url')
        }
        self._test_conversations.insert(0, new_conv)
        
        # 刷新视图
        if self._view_mode == 'grid':
            self.conversation_grid.load_conversations(self._test_conversations)
        else:
            self.conversation_list.load_conversations(self._test_conversations)
    
    def _on_view_toggle(self):
        """视图切换"""
        if self._view_mode == 'grid':
            # 切换到列表视图
            self._view_mode = 'list'
            self.conversation_grid.hide()
            self.conversation_list.show()
            self.view_btn.setText("🎨 网格")
            print("切换到列表视图")
        else:
            # 切换到网格视图
            self._view_mode = 'grid'
            self.conversation_list.hide()
            self.conversation_grid.show()
            self.view_btn.setText("📋 列表")
            print("切换到网格视图")
