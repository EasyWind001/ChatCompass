"""
搜索对话框组件
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QListWidget, QListWidgetItem, QWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius


class SearchDialog(QDialog):
    """搜索对话框"""
    
    # 信号
    conversation_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """初始化搜索对话框"""
        super().__init__(parent)
        self.conversations = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setWindowTitle("搜索对话")
        self.setFixedSize(700, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # === 标题 ===
        title_label = QLabel("🔍 搜索对话")
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 20, Fonts.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        layout.addWidget(title_label)
        
        # === 搜索栏 ===
        search_container = QHBoxLayout()
        search_container.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索标题、摘要、平台...")
        self.search_input.setFixedHeight(44)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 16px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {colors.get('primary')};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_container.addWidget(self.search_input)
        
        # 搜索按钮
        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(44, 44)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
        """)
        search_btn.clicked.connect(self._perform_search)
        search_container.addWidget(search_btn)
        
        layout.addLayout(search_container)
        
        # === 快捷筛选 ===
        filter_container = QHBoxLayout()
        filter_container.setSpacing(8)
        
        filter_label = QLabel("快捷筛选:")
        filter_label.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        filter_container.addWidget(filter_label)
        
        platforms = ["全部", "ChatGPT", "Claude", "DeepSeek"]
        for platform in platforms:
            btn = QPushButton(platform)
            btn.setFixedHeight(28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.get('bg_hover')};
                    color: {colors.get('fg_secondary')};
                    border: 1px solid {colors.get('border_default')};
                    border-radius: {BorderRadius.SM}px;
                    padding: 0 12px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('bg_active')};
                    color: {colors.get('fg_primary')};
                    border-color: {colors.get('primary')};
                }}
            """)
            btn.clicked.connect(lambda checked, p=platform: self._filter_by_platform(p))
            filter_container.addWidget(btn)
        
        filter_container.addStretch()
        layout.addLayout(filter_container)
        
        # === 结果列表 ===
        results_label = QLabel("搜索结果")
        results_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 14, Fonts.WEIGHT_SEMIBOLD))
        results_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {colors.get('bg_card')};
                border: 1px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {colors.get('fg_primary')};
                border-radius: {BorderRadius.SM}px;
                padding: 12px;
                margin: 4px 0;
            }}
            QListWidget::item:hover {{
                background-color: {colors.get('bg_hover')};
            }}
            QListWidget::item:selected {{
                background-color: {colors.get('bg_active')};
                border-left: 3px solid {colors.get('primary')};
            }}
        """)
        self.results_list.itemDoubleClicked.connect(self._on_result_selected)
        layout.addWidget(self.results_list)
        
        # === 底部按钮 ===
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(36)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 24px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
            }}
        """)
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # 应用对话框样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.get('bg_primary')};
            }}
        """)
    
    def set_conversations(self, conversations: list):
        """设置对话列表"""
        self.conversations = conversations
        self._update_results(conversations)
    
    def _update_results(self, conversations: list):
        """更新搜索结果"""
        self.results_list.clear()
        
        for conv in conversations:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, conv)
            
            # 显示格式: 平台 | 标题 | 消息数 | 时间
            text = f"{conv.get('platform', 'Unknown')} | {conv.get('title', '未命名')[:40]} | {conv.get('message_count', 0)}条消息"
            item.setText(text)
            
            self.results_list.addItem(item)
    
    def _on_search_text_changed(self, text: str):
        """搜索文本变化"""
        if not text.strip():
            self._update_results(self.conversations)
            return
        
        self._perform_search()
    
    def _perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip().lower()
        if not query:
            self._update_results(self.conversations)
            return
        
        # 搜索标题、摘要、平台
        filtered = [
            conv for conv in self.conversations
            if query in conv.get('title', '').lower() or
               query in conv.get('summary', '').lower() or
               query in conv.get('platform', '').lower()
        ]
        
        self._update_results(filtered)
    
    def _filter_by_platform(self, platform: str):
        """按平台筛选"""
        if platform == "全部":
            self._update_results(self.conversations)
        else:
            filtered = [
                conv for conv in self.conversations
                if conv.get('platform', '') == platform
            ]
            self._update_results(filtered)
    
    def _on_result_selected(self, item: QListWidgetItem):
        """结果被选中"""
        conv = item.data(Qt.ItemDataRole.UserRole)
        self.conversation_selected.emit(conv)
        self.close()
