"""
搜索结果精简列表项 - 用于查看完整对话时
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, BorderRadius


class SearchResultCompactItem(QFrame):
    """搜索结果精简列表项"""
    
    # 信号
    clicked = pyqtSignal(dict)
    
    def __init__(self, conversation: Dict[str, Any], match_count: int = 0, parent=None):
        """初始化精简列表项
        
        Args:
            conversation: 对话数据
            match_count: 匹配数量
            parent: 父组件
        """
        super().__init__(parent)
        self.conversation = conversation
        self.match_count = match_count
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_card')};
                border-left: 3px solid {colors.get('primary')};
                margin: 2px 0;
            }}
            QFrame:hover {{
                background-color: {colors.get('bg_hover')};
            }}
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 平台图标
        platform = self.conversation.get('platform', 'Unknown')
        icon_emoji = self._get_platform_icon()
        icon_label = QLabel(icon_emoji)
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 20px;
            background-color: {colors.get('bg_hover')};
            border-radius: 4px;
        """)
        layout.addWidget(icon_label)
        
        # 标题
        title = self.conversation.get('title', '未命名对话')
        display_title = title[:60] + '...' if len(title) > 60 else title
        title_label = QLabel(display_title)
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_SMALL, Fonts.WEIGHT_MEDIUM))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        title_label.setToolTip(title)
        layout.addWidget(title_label, stretch=1)
        
        # 匹配数标签
        if self.match_count > 0:
            match_label = QLabel(f"🔍 {self.match_count}")
            match_label.setStyleSheet(f"""
                color: {colors.get('primary')};
                font-size: 11px;
                font-weight: 500;
                padding: 2px 8px;
                background-color: {colors.get('bg_hover')};
                border-radius: 10px;
            """)
            layout.addWidget(match_label)
        
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
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conversation)
        super().mousePressEvent(event)
