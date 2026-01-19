"""
对话列表视图组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any
from datetime import datetime

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius


class ConversationListItem(QFrame):
    """列表项组件"""
    
    # 信号
    clicked = pyqtSignal(dict)
    star_toggled = pyqtSignal(int, bool)
    
    def __init__(self, conversation: Dict[str, Any], parent=None):
        """初始化列表项
        
        Args:
            conversation: 对话数据字典
            parent: 父组件
        """
        super().__init__(parent)
        self.conversation = conversation
        self.is_starred = conversation.get('starred', False)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI - 简化版：只显示标题和平台"""
        colors = get_color_scheme()
        
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_card')};
                border: 1px solid {colors.get('border_default')};
                border-radius: {BorderRadius.SM}px;
                margin: 2px 0;
            }}
            QFrame:hover {{
                background-color: {colors.get('bg_hover')};
                border-color: {colors.get('border_hover')};
            }}
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # === 平台图标(emoji风格) ===
        platform = self.conversation.get('platform', 'Unknown')
        icon_emoji = self._get_platform_icon()
        icon_label = QLabel(icon_emoji)
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            background-color: {colors.get('bg_hover')};
            border-radius: 6px;
        """)
        layout.addWidget(icon_label)
        
        # === 标题(直接截取,不用边框) ===
        title = self.conversation.get('title', '未命名对话')
        # 直接在代码中截取标题
        display_title = title[:50] + '...' if len(title) > 50 else title
        self.title_label = QLabel(display_title)
        self.title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_BODY, Fonts.WEIGHT_MEDIUM))
        self.title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        self.title_label.setToolTip(title)  # 完整标题作为tooltip
        layout.addWidget(self.title_label, stretch=1)
        
        # === 平台标签 ===
        platform_tag = QLabel(platform)
        platform_tag.setFixedHeight(24)
        platform_tag.setStyleSheet(f"""
            background-color: {self._get_platform_color()};
            color: white;
            padding: 2px 12px;
            border-radius: {BorderRadius.SM}px;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(platform_tag)
        
        # === 收藏按钮 ===
        self.star_btn = QPushButton("⭐" if self.is_starred else "☆")
        self.star_btn.setFixedSize(28, 28)
        self.star_btn.setFlat(True)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.star_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
                border-radius: {BorderRadius.SM}px;
            }}
        """)
        self.star_btn.clicked.connect(self._on_star_clicked)
        layout.addWidget(self.star_btn)
        
        # 设置鼠标追踪
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _get_platform_icon(self) -> str:
        """获取平台图标"""
        platform = self.conversation.get('platform', '').lower()
        icons = {
            'chatgpt': '🤖',
            'claude': '🔮',
            'deepseek': '🔍'
        }
        return icons.get(platform, '💬')
    
    def _get_platform_color(self) -> str:
        """获取平台颜色"""
        colors = get_color_scheme()
        platform = self.conversation.get('platform', '').lower()
        color_map = {
            'chatgpt': colors.get('platform_chatgpt'),
            'claude': colors.get('platform_claude'),
            'deepseek': colors.get('platform_deepseek')
        }
        return color_map.get(platform, colors.get('primary'))
    
    def _format_time(self, timestamp) -> str:
        """格式化时间显示"""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days == 0:
            return "今天"
        elif diff.days == 1:
            return "昨天"
        elif diff.days < 7:
            return f"{diff.days}天前"
        elif diff.days < 30:
            return f"{diff.days // 7}周前"
        else:
            return timestamp.strftime("%Y-%m-%d")
    
    def _on_star_clicked(self):
        """收藏按钮点击"""
        self.is_starred = not self.is_starred
        self.star_btn.setText("⭐" if self.is_starred else "☆")
        self.star_toggled.emit(self.conversation.get('id', 0), self.is_starred)
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conversation)
        super().mousePressEvent(event)


class ConversationList(QWidget):
    """对话列表组件"""
    
    # 信号
    conversation_selected = pyqtSignal(dict)
    star_toggled = pyqtSignal(int, bool)
    
    def __init__(self, parent=None):
        """初始化列表视图"""
        super().__init__(parent)
        self.items: List[ConversationListItem] = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # === 滚动区域 ===
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
        
        # === 列表容器 ===
        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        self.list_layout.addStretch()
        
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
    
    def load_conversations(self, conversations: List[Dict[str, Any]]):
        """加载对话列表
        
        Args:
            conversations: 对话数据列表
        """
        # 清空现有列表项
        self.clear()
        
        # 创建列表项
        for conv in conversations:
            item = ConversationListItem(conv)
            item.clicked.connect(lambda c=conv: self.conversation_selected.emit(c))
            item.star_toggled.connect(
                lambda conv_id, starred: self.star_toggled.emit(conv_id, starred)
            )
            
            # 插入到stretch之前
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)
            self.items.append(item)
    
    def clear(self):
        """清空所有列表项"""
        # 移除所有列表项widget(保留最后的stretch)
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.items.clear()
