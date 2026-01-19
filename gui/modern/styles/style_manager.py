"""
样式管理器
负责加载和应用QSS样式
"""
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from .color_scheme import Theme, get_color_scheme


class StyleManager:
    """样式管理器"""
    
    def __init__(self):
        """初始化样式管理器"""
        self._qss_dir = Path(__file__).parent / "qss"
        self._current_theme = Theme.LIGHT  # 默认使用亮色主题
    
    def load_qss(self, theme: Theme = None) -> str:
        """加载QSS样式文件
        
        Args:
            theme: 主题(None则使用当前主题)
            
        Returns:
            QSS样式字符串
        """
        if theme is None:
            theme = self._current_theme
        
        # 选择对应的QSS文件
        qss_file = self._qss_dir / f"{theme.value}_theme.qss"
        
        if not qss_file.exists():
            print(f"警告: 样式文件不存在 {qss_file}")
            return ""
        
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                qss = f.read()
            return qss
        except Exception as e:
            print(f"错误: 加载样式文件失败 {e}")
            return ""
    
    def apply_theme(self, app: QApplication, theme: Theme = None):
        """应用主题到应用程序
        
        Args:
            app: QApplication实例
            theme: 主题(None则使用当前主题)
        """
        if theme is not None:
            self._current_theme = theme
            get_color_scheme().switch_theme(theme)
        
        qss = self.load_qss(self._current_theme)
        app.setStyleSheet(qss)
    
    def switch_theme(self, app: QApplication):
        """切换主题
        
        Args:
            app: QApplication实例
        """
        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.apply_theme(app, new_theme)
    
    @property
    def current_theme(self) -> Theme:
        """获取当前主题"""
        return self._current_theme


# 全局样式管理器实例
_style_manager = StyleManager()


def get_style_manager() -> StyleManager:
    """获取全局样式管理器实例"""
    return _style_manager
