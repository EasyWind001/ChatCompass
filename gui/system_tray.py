"""
系统托盘图标

功能:
1. 显示系统托盘图标
2. 托盘菜单
3. 快速操作
4. 状态显示
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
import logging

logger = logging.getLogger(__name__)


class SystemTray(QObject):
    """系统托盘管理器"""
    
    # 信号
    show_window = pyqtSignal()
    quit_app = pyqtSignal()
    toggle_monitor = pyqtSignal(bool)  # True=启用, False=禁用
    
    def __init__(self, app):
        """
        初始化系统托盘
        
        Args:
            app: QApplication实例
        """
        super().__init__()
        self.app = app
        self.tray_icon = None
        self.monitor_enabled = True
        
        self.setup_tray()
    
    def setup_tray(self):
        """设置托盘图标和菜单"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # 设置图标 (暂时使用默认图标)
        # TODO: 添加自定义图标
        icon = self.app.style().standardIcon(
            self.app.style().StandardPixmap.SP_ComputerIcon
        )
        self.tray_icon.setIcon(icon)
        
        # 设置提示文字
        self.tray_icon.setToolTip("ChatCompass - AI对话管理工具")
        
        # 创建菜单
        self.create_menu()
        
        # 双击打开主窗口
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        logger.info("系统托盘图标已创建")
    
    def create_menu(self):
        """创建托盘菜单"""
        menu = QMenu()
        
        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window.emit)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # 剪贴板监控开关
        self.monitor_action = QAction("启用剪贴板监控", self)
        self.monitor_action.setCheckable(True)
        self.monitor_action.setChecked(self.monitor_enabled)
        self.monitor_action.triggered.connect(self.on_monitor_toggle)
        menu.addAction(self.monitor_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()
    
    def on_monitor_toggle(self, checked: bool):
        """监控开关切换"""
        self.monitor_enabled = checked
        self.toggle_monitor.emit(checked)
        
        status = "启用" if checked else "禁用"
        self.show_message("剪贴板监控", f"已{status}剪贴板监控")
        logger.info(f"剪贴板监控已{status}")
    
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            logger.info("系统托盘图标已显示")
    
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            logger.info("系统托盘图标已隐藏")
    
    def show_message(self, title: str, message: str, 
                    icon=QSystemTrayIcon.MessageIcon.Information,
                    duration: int = 3000):
        """
        显示系统通知
        
        Args:
            title: 标题
            message: 消息内容
            icon: 图标类型
            duration: 显示时长(毫秒)
        """
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, duration)
    
    def update_tooltip(self, text: str):
        """更新提示文字"""
        if self.tray_icon:
            self.tray_icon.setToolTip(text)
