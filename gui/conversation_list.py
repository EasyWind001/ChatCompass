"""
ConversationList - 对话列表组件

显示对话列表的表格视图
"""
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class ConversationList(QWidget):
    """对话列表组件"""
    
    # Signals
    conversation_selected = pyqtSignal(int)  # 对话选择信号 (conversation_id)
    
    def __init__(self, db, parent=None):
        """
        初始化对话列表
        
        Args:
            db: 数据库连接
            parent: 父窗口
        """
        super().__init__(parent)
        self.db = db
        self.conversations = []
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "平台", "时间"])
        
        # 表格设置
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        # 列宽设置
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # 连接信号
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
        
    def load_conversations(self, conversations: List[Dict[str, Any]]):
        """
        加载对话列表
        
        Args:
            conversations: 对话列表
        """
        self.conversations = conversations
        self.table.setRowCount(len(conversations))
        
        for row, conv in enumerate(conversations):
            # ID
            id_item = QTableWidgetItem(str(conv.get('id', '')))
            id_item.setData(Qt.ItemDataRole.UserRole, conv.get('id'))
            self.table.setItem(row, 0, id_item)
            
            # 标题
            title = conv.get('title', 'Untitled')
            title_item = QTableWidgetItem(title)
            title_item.setToolTip(title)
            self.table.setItem(row, 1, title_item)
            
            # 平台
            platform = conv.get('platform', 'unknown')
            platform_item = QTableWidgetItem(platform)
            
            # 平台颜色标识
            if platform == 'chatgpt':
                platform_item.setForeground(QColor('#10a37f'))
            elif platform == 'claude':
                platform_item.setForeground(QColor('#7c3aed'))
            elif platform == 'deepseek':
                platform_item.setForeground(QColor('#0066cc'))
                
            self.table.setItem(row, 2, platform_item)
            
            # 时间
            created_at = conv.get('created_at', '')
            if created_at:
                # 格式化时间
                if 'T' in str(created_at):
                    created_at = str(created_at).split('T')[0]
                elif ' ' in str(created_at):
                    created_at = str(created_at).split(' ')[0]
                    
            time_item = QTableWidgetItem(str(created_at))
            self.table.setItem(row, 3, time_item)
            
    def _on_selection_changed(self):
        """选择变化处理"""
        selected_rows = self.table.selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self.conversations):
                conv_id = self.conversations[row].get('id')
                if conv_id:
                    self.conversation_selected.emit(conv_id)
                    
    def get_selected_conversation(self) -> Optional[Dict[str, Any]]:
        """
        获取选中的对话
        
        Returns:
            选中的对话数据,如果没有选中则返回None
        """
        selected_rows = self.table.selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self.conversations):
                return self.conversations[row]
        return None
        
    def clear(self):
        """清空列表"""
        self.conversations = []
        self.table.setRowCount(0)
