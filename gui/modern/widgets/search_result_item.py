"""
搜索结果项组件 - 展示匹配上下文
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, List

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius


class SearchResultItem(QFrame):
    """搜索结果项组件"""
    
    # 信号
    clicked = pyqtSignal(dict)
    expand_clicked = pyqtSignal(dict)
    
    def __init__(self, conversation: Dict[str, Any], matches: List[Dict], parent=None):
        """初始化搜索结果项
        
        Args:
            conversation: 对话数据
            matches: 匹配结果列表 [{'context': '...匹配上下文...', 'position': 123}, ...]
            parent: 父组件
        """
        super().__init__(parent)
        self.conversation = conversation
        self.matches = matches
        self._expanded = False
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_card')};
                border: 1px solid {colors.get('border_default')};
                border-left: 3px solid {colors.get('primary')};
                border-radius: {BorderRadius.SM}px;
                margin: 4px 0;
            }}
            QFrame:hover {{
                background-color: {colors.get('bg_hover')};
                border-color: {colors.get('primary')};
            }}
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)
        
        # === 顶部：标题 + 平台 + 匹配数 ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # 标题
        title = self.conversation.get('title', '未命名对话')
        title_label = QLabel(title)
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_BODY, Fonts.WEIGHT_SEMIBOLD))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        header_layout.addWidget(title_label, stretch=1)
        
        # 平台标签
        platform = self.conversation.get('platform', 'Unknown')
        platform_tag = QLabel(platform)
        platform_tag.setFixedHeight(22)
        platform_tag.setStyleSheet(f"""
            background-color: {self._get_platform_color()};
            color: white;
            padding: 2px 10px;
            border-radius: {BorderRadius.SM}px;
            font-size: 11px;
            font-weight: 500;
        """)
        header_layout.addWidget(platform_tag)
        
        # 匹配数标签
        match_count = len(self.matches)
        match_label = QLabel(f"🔍 {match_count} 处匹配")
        match_label.setStyleSheet(f"""
            color: {colors.get('primary')};
            font-size: 12px;
            font-weight: 500;
        """)
        header_layout.addWidget(match_label)
        
        main_layout.addLayout(header_layout)
        
        # === 匹配上下文(最多显示2条) ===
        self.context_container = QWidget()
        context_layout = QVBoxLayout(self.context_container)
        context_layout.setContentsMargins(0, 0, 0, 0)
        context_layout.setSpacing(8)
        
        display_matches = self.matches[:2]  # 只显示前2条
        for i, match in enumerate(display_matches):
            context_frame = QFrame()
            context_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.get('bg_hover')};
                    border-radius: {BorderRadius.SM}px;
                    padding: 8px;
                }}
            """)
            
            context_inner_layout = QVBoxLayout(context_frame)
            context_inner_layout.setContentsMargins(8, 6, 8, 6)
            context_inner_layout.setSpacing(4)
            
            # 位置标签
            pos_label = QLabel(f"📍 匹配 {i+1}")
            pos_label.setStyleSheet(f"color: {colors.get('fg_secondary')}; font-size: 11px;")
            context_inner_layout.addWidget(pos_label)
            
            # 上下文内容（高亮匹配部分）
            context_text = match.get('context', '...')
            context_label = QLabel(context_text)
            context_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_SMALL))
            context_label.setStyleSheet(f"color: {colors.get('fg_primary')}; line-height: 1.5;")
            context_label.setWordWrap(True)
            context_inner_layout.addWidget(context_label)
            
            context_layout.addWidget(context_frame)
        
        # 如果有更多匹配，显示提示
        if len(self.matches) > 2:
            more_label = QLabel(f"...还有 {len(self.matches) - 2} 处匹配")
            more_label.setStyleSheet(f"""
                color: {colors.get('fg_secondary')};
                font-size: 12px;
                font-style: italic;
                padding: 4px 0;
            """)
            context_layout.addWidget(more_label)
        
        main_layout.addWidget(self.context_container)
        
        # === 底部：展开按钮 ===
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        expand_btn = QPushButton("📖 查看完整对话")
        expand_btn.setFixedHeight(28)
        expand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: {BorderRadius.SM}px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
        """)
        expand_btn.clicked.connect(lambda: self.expand_clicked.emit(self.conversation))
        bottom_layout.addWidget(expand_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # 设置鼠标追踪
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
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
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conversation)
        super().mousePressEvent(event)
