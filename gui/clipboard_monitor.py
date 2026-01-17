"""
剪贴板监控器

功能:
1. 监听系统剪贴板变化
2. 检测AI对话链接
3. 弹出添加提示
4. 避免重复提示

支持平台:
- Windows
- macOS
- Linux
"""

import re
import time
import logging
from typing import Optional, Set
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
import pyperclip

logger = logging.getLogger(__name__)


class ClipboardMonitor(QObject):
    """剪贴板监控器"""
    
    # 信号
    ai_url_detected = pyqtSignal(str)  # 检测到AI对话URL
    
    # 支持的AI对话平台URL模式
    AI_URL_PATTERNS = [
        r'https?://chat\.openai\.com/c/[\w-]+',
        r'https?://chatgpt\.com/share/[\w-]+',
        r'https?://claude\.ai/chat/[\w-]+',
        r'https?://chat\.deepseek\.com/share/[\w-]+',  # 修复: DeepSeek分享链接格式
        r'https?://kimi\.moonshot\.cn/share/[\w-]+',
        r'https?://poe\.com/s/[\w-]+',
        r'https?://gemini\.google\.com/share/[\w-]+',
        r'https?://tongyi\.aliyun\.com/qianwen/share/[\w-]+',
    ]
    
    def __init__(self, storage, check_interval: int = 1000):
        """
        初始化剪贴板监控器
        
        Args:
            storage: 数据库存储实例
            check_interval: 检查间隔(毫秒)
        """
        super().__init__()
        self.storage = storage
        self.check_interval = check_interval
        
        # 状态
        self.is_running = False
        self.last_clipboard_content: Optional[str] = None
        self.detected_urls: Set[str] = set()  # 已检测过的URL
        
        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        
        logger.info("剪贴板监控器初始化完成")
    
    def start(self):
        """启动监控"""
        if self.is_running:
            logger.warning("监控器已在运行")
            return
        
        self.is_running = True
        self.last_clipboard_content = self._get_clipboard_content()
        self.timer.start(self.check_interval)
        logger.info(f"剪贴板监控已启动 (间隔: {self.check_interval}ms)")
    
    def stop(self):
        """停止监控"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.timer.stop()
        logger.info("剪贴板监控已停止")
    
    def check_clipboard(self):
        """检查剪贴板内容"""
        try:
            current_content = self._get_clipboard_content()
            
            # 内容未变化
            if current_content == self.last_clipboard_content:
                return
            
            self.last_clipboard_content = current_content
            
            # 检查是否为AI对话URL
            if current_content and self.is_valid_url(current_content):
                if self.is_ai_conversation_url(current_content):
                    # 避免重复提示
                    if current_content not in self.detected_urls:
                        self.detected_urls.add(current_content)
                        self.ai_url_detected.emit(current_content)
                        self.show_add_prompt(current_content)
                        logger.info(f"检测到AI对话URL: {current_content}")
        
        except Exception as e:
            logger.error(f"检查剪贴板时出错: {e}", exc_info=True)
    
    def _get_clipboard_content(self) -> Optional[str]:
        """获取剪贴板内容"""
        try:
            content = pyperclip.paste()
            return content.strip() if content else None
        except Exception as e:
            logger.error(f"获取剪贴板内容失败: {e}")
            return None
    
    def is_valid_url(self, text: str) -> bool:
        """
        验证是否为有效URL
        
        Args:
            text: 文本内容
            
        Returns:
            是否为有效URL
        """
        if not text:
            return False
        
        url_pattern = r'^https?://[\w\-\.]+\.[a-z]{2,}(/.*)?$'
        return bool(re.match(url_pattern, text, re.IGNORECASE))
    
    def is_ai_conversation_url(self, url: str) -> bool:
        """
        检测是否为AI对话URL
        
        Args:
            url: URL字符串
            
        Returns:
            是否为AI对话URL
        """
        for pattern in self.AI_URL_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def show_add_prompt(self, url: str):
        """
        显示添加提示对话框
        
        Args:
            url: AI对话URL
        """
        from gui.dialogs.add_prompt_dialog import AddPromptDialog
        
        dialog = AddPromptDialog(url, parent=None)
        
        if dialog.exec():  # 用户点击"添加"
            # 触发添加操作
            from gui.dialogs.add_dialog import AddDialog
            add_dialog = AddDialog(db=self.storage, parent=None)
            # 预填充URL到对话框
            add_dialog.url_input.setText(url)
            add_dialog.exec()
    
    def clear_detected_urls(self):
        """清空已检测URL缓存"""
        self.detected_urls.clear()
        logger.info("已清空URL检测缓存")
    
    def reset(self):
        """重置监控器状态"""
        self.stop()
        self.last_clipboard_content = None
        self.clear_detected_urls()
        logger.info("监控器已重置")
