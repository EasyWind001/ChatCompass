"""
对话卡片网格视图 - 单列布局
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any

from .conversation_card import ConversationCard
from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Spacing


class ConversationGrid(QWidget):
    """对话卡片网格组件 - 单列布局"""
    
    # 信号
    conversation_selected = pyqtSignal(dict)  # 选中对话
    star_toggled = pyqtSignal(int, bool)  # 收藏切换
    
    def __init__(self, parent=None):
        """初始化网格视图"""
        super().__init__(parent)
        self.cards: List[ConversationCard] = []
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
        
        # === 卡片容器(单列垂直布局) ===
        container = QWidget()
        container.setFixedWidth(300)  # 固定宽度
        self.card_layout = QVBoxLayout(container)
        self.card_layout.setSpacing(Spacing.MD)
        self.card_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        self.card_layout.addStretch()  # 底部弹簧
        
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
    
    def load_conversations(self, conversations: List[Dict[str, Any]]):
        """加载对话列表
        
        Args:
            conversations: 对话数据列表
        """
        # 清空现有卡片
        self.clear()
        
        # 创建卡片(单列显示,每个卡片占满宽度)
        for conv in conversations:
            card = ConversationCard(conv)
            card.setFixedWidth(280)  # 固定宽度280px
            card.clicked.connect(lambda c=conv: self.conversation_selected.emit(c))
            # star_clicked信号暂时不连接,卡片组件需要添加
            # card.star_clicked.connect(
            #     lambda conv_id, starred: self.star_toggled.emit(conv_id, starred)
            # )
            
            # 插入到stretch之前
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)
            self.cards.append(card)
    
    def clear(self):
        """清空所有卡片"""
        # 移除所有卡片widget(保留最后的stretch)
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards.clear()
