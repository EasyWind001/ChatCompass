"""
添加提示对话框

快速提示用户是否添加检测到的AI对话链接
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)


class AddPromptDialog(QDialog):
    """添加提示对话框"""
    
    def __init__(self, url: str, parent=None):
        """
        初始化对话框
        
        Args:
            url: 检测到的AI对话URL
            parent: 父窗口
        """
        super().__init__(parent)
        self.url = url
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("发现AI对话链接")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("📋 检测到剪贴板中有AI对话链接")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 提示信息
        info_label = QLabel("是否要将此对话添加到ChatCompass?")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #555;
                padding: 5px;
            }
        """)
        layout.addWidget(info_label)
        
        # URL显示
        url_label = QLabel(f"链接: {self.url}")
        url_label.setWordWrap(True)
        url_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #3498db;
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(url_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 忽略按钮
        ignore_btn = QPushButton("忽略")
        ignore_btn.setMinimumWidth(100)
        ignore_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        ignore_btn.clicked.connect(self.reject)
        button_layout.addWidget(ignore_btn)
        
        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.setMinimumWidth(100)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        add_btn.clicked.connect(self.accept)
        add_btn.setDefault(True)  # 设为默认按钮(回车触发)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        # 底部提示
        tip_label = QLabel("💡 提示: 可以在设置中关闭剪贴板监控")
        tip_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #7f8c8d;
                padding: 5px;
            }
        """)
        layout.addWidget(tip_label)
        
        self.setLayout(layout)
        
        # 设置窗口标志 - 保持在最前
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint
        )
    
    def accept(self):
        """用户点击添加"""
        logger.info(f"用户选择添加URL: {self.url}")
        super().accept()
    
    def reject(self):
        """用户点击忽略"""
        logger.info(f"用户选择忽略URL: {self.url}")
        super().reject()
