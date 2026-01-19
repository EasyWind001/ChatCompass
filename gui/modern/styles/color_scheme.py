"""
现代化配色方案
提供暗色和亮色主题的完整色彩系统
"""
from enum import Enum
from PyQt6.QtGui import QColor


class Theme(Enum):
    """主题枚举"""
    DARK = "dark"
    LIGHT = "light"


class ColorScheme:
    """色彩系统配置"""
    
    # ==================== 暗色主题(更亮版本) ====================
    DARK = {
        # 背景色 - 提升亮度,采用偏蓝灰色调
        'bg_primary': '#1A1D29',        # 主背景(更亮的深蓝灰)
        'bg_secondary': '#22252F',      # 二级背景
        'bg_card': '#2A2E3A',           # 卡片背景(更明显的层次)
        'bg_hover': '#33374A',          # 悬停背景
        'bg_active': '#3D4254',         # 激活背景
        
        # 前景色 - 更高的对比度
        'fg_primary': '#F0F3F7',        # 主文字(更亮的白色)
        'fg_secondary': '#A8B2C1',      # 次要文字(更亮的灰色)
        'fg_disabled': '#5F6B7A',       # 禁用文字
        'fg_inverse': '#1A1D29',        # 反色文字
        
        # 边框色 - 更明显的边框
        'border_default': '#3D4254',    # 默认边框(更亮)
        'border_hover': '#A8B2C1',      # 悬停边框
        'border_active': '#5EB0FF',     # 激活边框(更亮的蓝)
        
        # 强调色 - 更明亮鲜艳
        'primary': '#5EB0FF',           # 主色调(更亮的蓝色)
        'primary_hover': '#80C4FF',     # 主色调悬停
        'primary_active': '#3D9EFF',    # 主色调激活
        
        'success': '#4FCB6B',           # 成功(更亮的绿色)
        'success_hover': '#6DE085',     # 成功悬停
        
        'warning': '#FFB84D',           # 警告(更亮的橙色)
        'warning_hover': '#FFC870',     # 警告悬停
        
        'error': '#FF6B6B',             # 错误(更亮的红色)
        'error_hover': '#FF8585',       # 错误悬停
        
        # 平台色 - 更鲜艳
        'platform_chatgpt': '#10D693',  # ChatGPT绿(更亮)
        'platform_claude': '#9F5AFF',   # Claude紫(更亮)
        'platform_deepseek': '#3D9EFF', # DeepSeek蓝(更亮)
        
        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.3)',         # 阴影(更淡)
        'overlay': 'rgba(0, 0, 0, 0.4)',        # 遮罩(更淡)
        'glassmorphism': 'rgba(42, 46, 58, 0.85)',  # 毛玻璃
    }
    
    # ==================== 亮色主题(清爽白色) ====================
    LIGHT = {
        # 背景色 - 纯白+浅灰层次
        'bg_primary': '#F8F9FA',        # 主背景(浅灰,更舒适)
        'bg_secondary': '#EBEDEF',      # 二级背景
        'bg_card': '#FFFFFF',           # 卡片背景(纯白)
        'bg_hover': '#F0F2F4',          # 悬停背景
        'bg_active': '#E3E6E9',         # 激活背景
        
        # 前景色 - 深色文字,高对比
        'fg_primary': '#1A1D29',        # 主文字(深色)
        'fg_secondary': '#5F6B7A',      # 次要文字
        'fg_disabled': '#A8B2C1',       # 禁用文字
        'fg_inverse': '#FFFFFF',        # 反色文字
        
        # 边框色 - 浅灰边框
        'border_default': '#D8DCE1',    # 默认边框
        'border_hover': '#A8B2C1',      # 悬停边框
        'border_active': '#3D9EFF',     # 激活边框
        
        # 强调色 - 鲜艳明亮
        'primary': '#3D9EFF',           # 主色调(亮蓝)
        'primary_hover': '#2589E8',     # 主色调悬停
        'primary_active': '#1975D1',    # 主色调激活
        
        'success': '#26D879',           # 成功(鲜绿)
        'success_hover': '#1FC768',     # 成功悬停
        
        'warning': '#FFB84D',           # 警告(亮橙)
        'warning_hover': '#FFA730',     # 警告悬停
        
        'error': '#FF6B6B',             # 错误(亮红)
        'error_hover': '#FF5252',       # 错误悬停
        
        # 平台色 - 更鲜艳版本
        'platform_chatgpt': '#10D693',  # ChatGPT绿(鲜艳)
        'platform_claude': '#9F5AFF',   # Claude紫(鲜艳)
        'platform_deepseek': '#3D9EFF', # DeepSeek蓝(鲜艳)
        
        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.08)',        # 阴影(更淡)
        'overlay': 'rgba(0, 0, 0, 0.25)',       # 遮罩
        'glassmorphism': 'rgba(255, 255, 255, 0.92)',  # 毛玻璃
    }
    
    def __init__(self, theme: Theme = Theme.LIGHT):
        """初始化配色方案
        
        Args:
            theme: 主题类型(暗色/亮色)
        """
        self._theme = theme
        self._colors = self.DARK if theme == Theme.DARK else self.LIGHT
    
    def get(self, key: str) -> str:
        """获取颜色值
        
        Args:
            key: 颜色键名
            
        Returns:
            颜色值(十六进制或rgba)
        """
        return self._colors.get(key, '#000000')
    
    def get_color(self, key: str) -> QColor:
        """获取QColor对象
        
        Args:
            key: 颜色键名
            
        Returns:
            QColor对象
        """
        color_str = self.get(key)
        if color_str.startswith('rgba'):
            # 解析rgba格式
            parts = color_str.replace('rgba(', '').replace(')', '').split(',')
            r, g, b, a = int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])
            return QColor(r, g, b, int(a * 255))
        else:
            # 十六进制格式
            return QColor(color_str)
    
    def switch_theme(self, theme: Theme):
        """切换主题
        
        Args:
            theme: 新主题
        """
        self._theme = theme
        self._colors = self.DARK if theme == Theme.DARK else self.LIGHT
    
    @property
    def theme(self) -> Theme:
        """当前主题"""
        return self._theme
    
    @property
    def is_dark(self) -> bool:
        """是否为暗色主题"""
        return self._theme == Theme.DARK


# 全局配色方案实例
_color_scheme = ColorScheme(Theme.DARK)


def get_color_scheme() -> ColorScheme:
    """获取全局配色方案实例"""
    return _color_scheme


def set_theme(theme: Theme):
    """设置全局主题"""
    _color_scheme.switch_theme(theme)
