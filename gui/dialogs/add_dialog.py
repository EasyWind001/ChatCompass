"""
AddDialog - 添加对话对话框

允许用户输入URL添加新对话
"""
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from scrapers.scraper_factory import ScraperFactory


class ScraperThread(QThread):
    """爬虫线程"""
    
    # Signals
    progress = pyqtSignal(str)  # 进度消息
    finished = pyqtSignal(dict)  # 完成 (conversation data)
    error = pyqtSignal(str)  # 错误
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        
    def run(self):
        """运行爬虫"""
        try:
            self.progress.emit("🔍 识别平台...")
            
            # 创建爬虫
            scraper = ScraperFactory.create_scraper(self.url)
            if not scraper:
                self.error.emit("不支持的URL格式")
                return
                
            self.progress.emit(f"🌐 启动 {scraper.__class__.__name__}...")
            
            # 爬取
            conversation = scraper.scrape(self.url)
            
            if conversation:
                self.progress.emit("✅ 爬取成功!")
                self.finished.emit(conversation)
            else:
                self.error.emit("爬取失败:未获取到数据")
                
        except Exception as e:
            self.error.emit(f"爬取失败: {str(e)}")


class AddDialog(QDialog):
    """添加对话对话框"""
    
    def __init__(self, db, parent=None):
        """
        初始化对话框
        
        Args:
            db: 数据库连接
            parent: 父窗口
        """
        super().__init__(parent)
        self.db = db
        self.conversation = None
        self.scraper_thread = None
        
        self.setWindowTitle("添加对话")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # URL输入
        url_label = QLabel("对话URL:")
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "输入AI对话分享链接 (ChatGPT/Claude/DeepSeek)"
        )
        layout.addWidget(self.url_input)
        
        # 提示信息
        hint_label = QLabel(
            "支持的格式:\n"
            "• ChatGPT: https://chatgpt.com/share/...\n"
            "• Claude: https://claude.ai/share/...\n"
            "• DeepSeek: https://chat.deepseek.com/share/..."
        )
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(hint_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志输出
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加")
        self.add_btn.setDefault(True)
        self.add_btn.clicked.connect(self._on_add)
        button_layout.addWidget(self.add_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def _on_add(self):
        """添加按钮点击"""
        url = self.url_input.text().strip()
        
        # 验证URL
        if not url:
            QMessageBox.warning(self, "警告", "请输入URL")
            return
            
        if not url.startswith('http'):
            QMessageBox.warning(self, "警告", "URL格式无效")
            return
            
        # 禁用输入
        self.url_input.setEnabled(False)
        self.add_btn.setEnabled(False)
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.log_text.setVisible(True)
        self.log_text.clear()
        
        # 启动爬虫线程
        self.scraper_thread = ScraperThread(url)
        self.scraper_thread.progress.connect(self._on_progress)
        self.scraper_thread.finished.connect(self._on_finished)
        self.scraper_thread.error.connect(self._on_error)
        self.scraper_thread.start()
        
    def _on_progress(self, message: str):
        """进度更新"""
        self.log_text.append(message)
        
    def _on_finished(self, conversation: Dict[str, Any]):
        """爬取完成"""
        try:
            # 保存到数据库
            self.log_text.append("💾 保存到数据库...")
            
            conv_id = self.db.add_conversation(conversation)
            conversation['id'] = conv_id
            
            self.conversation = conversation
            
            self.log_text.append(f"✅ 成功! ID: {conv_id}")
            
            # 延迟关闭
            QThread.msleep(500)
            self.accept()
            
        except Exception as e:
            self._on_error(f"保存失败: {str(e)}")
            
    def _on_error(self, error_msg: str):
        """错误处理"""
        self.progress_bar.setVisible(False)
        self.log_text.append(f"❌ {error_msg}")
        
        # 重新启用输入
        self.url_input.setEnabled(True)
        self.add_btn.setEnabled(True)
        
        QMessageBox.critical(self, "错误", error_msg)
        
    def get_conversation(self) -> Optional[Dict[str, Any]]:
        """
        获取添加的对话数据
        
        Returns:
            对话数据,如果失败则返回None
        """
        return self.conversation
