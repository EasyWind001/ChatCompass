"""
抓取状态面板 - 显示异步抓取任务列表
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius


class ScrapingTaskItem(QFrame):
    """抓取任务项"""
    
    # 信号
    cancel_clicked = pyqtSignal(str)  # task_id
    
    def __init__(self, task: Dict, parent=None):
        """初始化任务项
        
        Args:
            task: {'id': '...', 'url': '...', 'platform': '...', 'status': 'pending/running/success/error', 'progress': 0-100}
        """
        super().__init__(parent)
        self.task = task
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get('bg_card')};
                border: 1px solid {colors.get('border_default')};
                border-radius: {BorderRadius.SM}px;
                padding: 12px;
                margin: 4px 0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # 顶部：平台 + URL
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        platform_label = QLabel(f"📱 {self.task.get('platform', 'Unknown')}")
        platform_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], Fonts.SIZE_SMALL, Fonts.WEIGHT_MEDIUM))
        platform_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        top_layout.addWidget(platform_label)
        
        url = self.task.get('url', '')[:50] + ('...' if len(self.task.get('url', '')) > 50 else '')
        url_label = QLabel(url)
        url_label.setStyleSheet(f"color: {colors.get('fg_secondary')}; font-size: 11px;")
        top_layout.addWidget(url_label, stretch=1)
        
        # 取消按钮
        if self.task.get('status') in ['pending', 'running']:
            cancel_btn = QPushButton("✖")
            cancel_btn.setFixedSize(20, 20)
            cancel_btn.setFlat(True)
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {colors.get('error')};
                    border: none;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('bg_hover')};
                }}
            """)
            cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.task.get('id')))
            top_layout.addWidget(cancel_btn)
        
        layout.addLayout(top_layout)
        
        # 进度条或状态
        status = self.task.get('status', 'pending')
        if status == 'running':
            progress_bar = QProgressBar()
            progress_bar.setFixedHeight(6)
            progress_bar.setValue(self.task.get('progress', 0))
            progress_bar.setTextVisible(False)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 3px;
                    background-color: {colors.get('bg_hover')};
                }}
                QProgressBar::chunk {{
                    background-color: {colors.get('primary')};
                    border-radius: 3px;
                }}
            """)
            layout.addWidget(progress_bar)
        elif status == 'success':
            status_label = QLabel("✅ 抓取成功")
            status_label.setStyleSheet(f"color: {colors.get('success')}; font-size: 12px;")
            layout.addWidget(status_label)
        elif status == 'error':
            status_label = QLabel("❌ 抓取失败")
            status_label.setStyleSheet(f"color: {colors.get('error')}; font-size: 12px;")
            layout.addWidget(status_label)
        else:  # pending
            status_label = QLabel("⏳ 等待中...")
            status_label.setStyleSheet(f"color: {colors.get('fg_secondary')}; font-size: 12px;")
            layout.addWidget(status_label)


class ScrapingStatusPanel(QWidget):
    """抓取状态面板"""
    
    # 信号
    task_cancelled = pyqtSignal(str)
    toggle_collapsed = pyqtSignal(bool)  # 展开/收起信号
    
    def __init__(self, parent=None):
        """初始化面板"""
        super().__init__(parent)
        self.tasks: List[Dict] = []
        self._collapsed = False  # 是否收起
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setFixedWidth(300)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('bg_primary')};
                border-left: 1px solid {colors.get('border_default')};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题 + 收起/展开按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("📥 抓取队列")
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 16, Fonts.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        header_layout.addWidget(title_label)
        
        self.count_label = QLabel("0 个任务")
        self.count_label.setStyleSheet(f"color: {colors.get('fg_secondary')}; font-size: 13px;")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        
        # 收起/展开按钮
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {colors.get('fg_secondary')};
                border: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_hover')};
                border-radius: 4px;
            }}
        """)
        self.toggle_btn.clicked.connect(self._on_toggle_clicked)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(header_layout)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # 任务容器
        container = QWidget()
        self.task_layout = QVBoxLayout(container)
        self.task_layout.setSpacing(8)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        self.task_layout.addStretch()
        
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
        # 保存滚动区域引用
        self.scroll_area = scroll_area
    
    def _on_toggle_clicked(self):
        """收起/展开按钮点击"""
        self._collapsed = not self._collapsed
        
        if self._collapsed:
            # 收起状态
            self.setFixedWidth(50)
            self.scroll_area.hide()
            self.count_label.hide()
            self.toggle_btn.setText("▶")
        else:
            # 展开状态
            self.setFixedWidth(300)
            self.scroll_area.show()
            self.count_label.show()
            self.toggle_btn.setText("◀")
        
        self.toggle_collapsed.emit(self._collapsed)
    
    def add_task(self, task: Dict):
        """添加任务"""
        self.tasks.insert(0, task)
        self._refresh_tasks()
    
    def update_task(self, task_id: str, updates: Dict):
        """更新任务"""
        for task in self.tasks:
            if task.get('id') == task_id:
                task.update(updates)
                break
        self._refresh_tasks()
    
    def remove_task(self, task_id: str):
        """移除任务"""
        self.tasks = [t for t in self.tasks if t.get('id') != task_id]
        self._refresh_tasks()
    
    def _refresh_tasks(self):
        """刷新任务列表"""
        # 清空现有项
        while self.task_layout.count() > 1:
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加任务项
        for task in self.tasks:
            item = ScrapingTaskItem(task)
            item.cancel_clicked.connect(self.task_cancelled.emit)
            self.task_layout.insertWidget(self.task_layout.count() - 1, item)
        
        # 更新计数
        self.count_label.setText(f"{len(self.tasks)} 个任务")
