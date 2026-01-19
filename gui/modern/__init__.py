"""
现代化GUI模块
v1.4.0 GUI现代化改造
"""
from .layouts.modern_main_window import ModernMainWindow
from .styles.color_scheme import ColorScheme, Theme, get_color_scheme
from .styles.style_manager import StyleManager, get_style_manager

__all__ = [
    'ModernMainWindow',
    'ColorScheme',
    'Theme',
    'get_color_scheme',
    'StyleManager',
    'get_style_manager',
]
