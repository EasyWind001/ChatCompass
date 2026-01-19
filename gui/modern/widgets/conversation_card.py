"""
对话卡片组件
现代化的卡片式对话展示
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath
from datetime import datetime
from typing import Dict, Any

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius, Sizes


class ConversationCard(QFrame):
    """对话卡片组件"""
    
    # 信号
    clicked = pyqtSignal(dict)  # 点击卡片
    star_toggled = pyqtSignal(int, bool)  # 收藏切换
    
    def __init__(self, conversation: Dict[str, Any], parent=None):
        """初始化卡片
        
        Args:
            conversation: 对话数据字典
            parent: 父组件
        """
        super().__init__(parent)
        self.conversation = conversation
        self.is_starred = conversation.get('starred', False)
        self._is_hovered = False
        
        self._init_ui()
        self._setup_animation()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        # 卡片样式
        self.setObjectName("ConversationCard")
        self.setFixedSize(Sizes.CARD_WIDTH, Sizes.CARD_HEIGHT)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 设置样式
        platform_color = self._get_platform_color()
        self.setStyleSheet(f"""
            #ConversationCard {{
                background-color: {colors.get('bg_card')};
                border: 1px solid {colors.get('border_default')};
                border-top: 3px solid {platform_color};
                border-radius: {BorderRadius.MD}px;
            }}
            #ConversationCard:hover {{
                border-color: {colors.get('border_hover')};
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        layout.setSpacing(Spacing.SM)
        
        # === 顶部栏(平台图标 + 收藏) ===
        top_bar = QHBoxLayout()
        top_bar.setSpacing(Spacing.SM)
        
        # 平台标签
        platform_label = QLabel(self._get_platform_icon() + " " + self.conversation.get('platform', 'Unknown'))
        platform_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_SMALL, Fonts.WEIGHT_MEDIUM))
        platform_label.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        top_bar.addWidget(platform_label)
        
        top_bar.addStretch()
        
        # 收藏按钮
        self.star_btn = QPushButton("⭐" if self.is_starred else "☆")
        self.star_btn.setFixedSize(24, 24)
        self.star_btn.setFlat(True)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.star_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{
                transform: scale(1.2);
            }}
        """)
        self.star_btn.clicked.connect(self._on_star_clicked)
        top_bar.addWidget(self.star_btn)
        
        layout.addLayout(top_bar)
        
        # === 标题 ===
        title = self.conversation.get('title', '未命名对话')[:40]  # 限制长度
        title_label = QLabel(title)
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_BODY, Fonts.WEIGHT_SEMIBOLD))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(40)  # 最多2行
        layout.addWidget(title_label)
        
        # === 分隔线 ===
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {colors.get('border_default')};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # === 摘要 ===
        summary = self.conversation.get('summary', '暂无摘要')[:80]  # 限制长度
        summary_label = QLabel(summary + "...")
        summary_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_SMALL))
        summary_label.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        summary_label.setWordWrap(True)
        summary_label.setMaximumHeight(54)  # 最多3行
        layout.addWidget(summary_label)
        
        layout.addStretch()
        
        # === 底部信息 ===
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(Spacing.MD)
        
        # 消息数
        msg_count = self.conversation.get('message_count', 0)
        msg_label = QLabel(f"💬 {msg_count}")
        msg_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_CAPTION))
        msg_label.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        bottom_bar.addWidget(msg_label)
        
        # 时间
        timestamp = self.conversation.get('created_at', datetime.now())
        time_str = self._format_time(timestamp)
        time_label = QLabel(f"📅 {time_str}")
        time_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_CAPTION))
        time_label.setStyleSheet(f"color: {colors.get('fg_secondary')};")
        bottom_bar.addWidget(time_label)
        
        # 分类标签
        category = self.conversation.get('category')
        if category:
            cat_label = QLabel(category)
            cat_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_CAPTION))
            cat_label.setStyleSheet(f"""
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                padding: 2px 8px;
                border-radius: {BorderRadius.SM}px;
            """)
            bottom_bar.addWidget(cat_label)
        
        bottom_bar.addStretch()
        layout.addLayout(bottom_bar)
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
    
    def _setup_animation(self):
        """设置动画效果"""
        # 悬停上浮动画
        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
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
    
    def enterEvent(self, event):
        """鼠标进入"""
        self._is_hovered = True
        # 增强阴影
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(20)
            effect.setOffset(0, 4)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开"""
        self._is_hovered = False
        # 恢复阴影
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(10)
            effect.setOffset(0, 2)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
