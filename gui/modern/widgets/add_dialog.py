"""
添加对话对话框组件
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QTextEdit, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..styles.color_scheme import get_color_scheme
from ..styles.constants import Fonts, Spacing, BorderRadius


class AddDialog(QDialog):
    """添加对话对话框"""
    
    # 信号
    conversation_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """初始化添加对话框"""
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        colors = get_color_scheme()
        
        self.setWindowTitle("添加对话")
        self.setFixedSize(650, 700)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # === 标题 ===
        title_label = QLabel("➕ 添加新对话")
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 20, Fonts.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        layout.addWidget(title_label)
        
        # === 表单区域 ===
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # URL输入
        url_label = QLabel("对话链接 (必填)")
        url_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 13, Fonts.WEIGHT_MEDIUM))
        url_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        form_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("粘贴ChatGPT、Claude或DeepSeek对话链接...")
        self.url_input.setFixedHeight(44)
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors.get('primary')};
            }}
        """)
        form_layout.addWidget(self.url_input)
        
        # 平台选择
        platform_label = QLabel("选择平台")
        platform_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 13, Fonts.WEIGHT_MEDIUM))
        platform_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        form_layout.addWidget(platform_label)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["自动识别", "ChatGPT", "Claude", "DeepSeek"])
        self.platform_combo.setFixedHeight(44)
        self.platform_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border-color: {colors.get('primary')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors.get('fg_secondary')};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                selection-background-color: {colors.get('bg_hover')};
            }}
        """)
        form_layout.addWidget(self.platform_combo)
        
        # 标题输入
        title_label = QLabel("对话标题 (可选)")
        title_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 13, Fonts.WEIGHT_MEDIUM))
        title_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        form_layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("留空则自动抓取...")
        self.title_input.setFixedHeight(44)
        self.title_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors.get('primary')};
            }}
        """)
        form_layout.addWidget(self.title_input)
        
        # 分类选择
        category_label = QLabel("分类 (可选)")
        category_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 13, Fonts.WEIGHT_MEDIUM))
        category_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        form_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["无", "编程", "写作", "学习", "翻译", "其他"])
        self.category_combo.setFixedHeight(44)
        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border-color: {colors.get('primary')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors.get('fg_secondary')};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                selection-background-color: {colors.get('bg_hover')};
            }}
        """)
        form_layout.addWidget(self.category_combo)
        
        # 备注输入
        notes_label = QLabel("备注 (可选)")
        notes_label.setFont(QFont(Fonts.PRIMARY.split(',')[0], 13, Fonts.WEIGHT_MEDIUM))
        notes_label.setStyleSheet(f"color: {colors.get('fg_primary')};")
        form_layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("添加备注信息...")
        self.notes_input.setFixedHeight(100)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors.get('bg_card')};
                color: {colors.get('fg_primary')};
                border: 2px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                padding: 12px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border-color: {colors.get('primary')};
            }}
        """)
        form_layout.addWidget(self.notes_input)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        # === 提示信息 ===
        hint_label = QLabel("💡 粘贴链接后，系统将自动抓取对话内容并保存到数据库")
        hint_label.setStyleSheet(f"""
            color: {colors.get('fg_secondary')};
            background-color: {colors.get('bg_hover')};
            border-radius: {BorderRadius.SM}px;
            padding: 12px;
            font-size: 13px;
        """)
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        # === 底部按钮 ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_primary')};
                border: 1px solid {colors.get('border_default')};
                border-radius: {BorderRadius.MD}px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('bg_active')};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("添加")
        add_btn.setFixedSize(100, 40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('primary')};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_hover')};
            }}
            QPushButton:disabled {{
                background-color: {colors.get('bg_hover')};
                color: {colors.get('fg_secondary')};
            }}
        """)
        add_btn.clicked.connect(self._on_add_clicked)
        buttons_layout.addWidget(add_btn)
        
        layout.addLayout(buttons_layout)
        
        # 应用对话框样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.get('bg_primary')};
            }}
        """)
    
    def _on_add_clicked(self):
        """添加按钮点击"""
        url = self.url_input.text().strip()
        if not url:
            # TODO: 显示错误提示
            return
        
        # 构建对话数据
        conv_data = {
            'url': url,
            'platform': self.platform_combo.currentText(),
            'title': self.title_input.text().strip(),
            'category': self.category_combo.currentText() if self.category_combo.currentIndex() > 0 else None,
            'notes': self.notes_input.toPlainText().strip()
        }
        
        self.conversation_added.emit(conv_data)
        self.close()
    
    def clear_form(self):
        """清空表单"""
        self.url_input.clear()
        self.title_input.clear()
        self.notes_input.clear()
        self.platform_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
