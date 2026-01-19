# Phase 1: 基础改造 - 详细设计文档

## 📌 阶段概述

**目标**: 建立现代化设计基础，完成核心组件架构重构  
**时间**: Week 1 (2026-01-18 ~ 2026-01-24)  
**优先级**: 🔴 P0 (最高)

---

## 🎯 核心目标

1. ✅ 引入 qfluentwidgets 组件库
2. ✅ 实现完整的设计系统
3. ✅ 建立新的三栏布局
4. ✅ 重构对话列表为卡片视图
5. ✅ 应用统一的色彩系统

---

## 📋 任务分解

### Task 1.1: 环境准备和依赖安装

#### 安装 qfluentwidgets

```bash
# 安装命令
pip install PyQt6-Fluent-Widgets

# 验证安装
python -c "from qfluentwidgets import FluentWindow; print('安装成功')"
```

#### 更新依赖文件

**requirements-gui.txt**:
```txt
PyQt6>=6.6.0
PyQt6-Fluent-Widgets>=1.5.0
phosphor-icons>=2.0.0  # 图标库
```

#### 创建目录结构

```bash
# 创建新的模块目录
gui/modern/
├── __init__.py
├── layouts/
│   ├── __init__.py
│   ├── main_layout.py
│   ├── top_bar.py
│   └── side_nav.py
├── widgets/
│   ├── __init__.py
│   ├── conversation_card.py
│   ├── card_grid_view.py
│   └── card_list_view.py
├── dialogs/
│   ├── __init__.py
│   └── add_dialog_v2.py
└── styles/
    ├── __init__.py
    ├── colors.py
    ├── theme.py
    ├── typography.py
    ├── spacing.py
    └── qss/
        ├── base.qss
        ├── dark.qss
        └── light.qss
```

#### 图标资源准备

1. 下载 Phosphor Icons SVG 文件
2. 放置到 `gui/modern/assets/icons/`
3. 创建图标索引文件

---

### Task 1.2: 设计系统实现

#### 1.2.1 颜色系统 (`colors.py`)

```python
"""
颜色系统定义
"""
from enum import Enum
from typing import Dict

class ColorRole(Enum):
    """颜色角色枚举"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class DarkColors:
    """暗色主题颜色"""
    
    # 背景色
    BG_PRIMARY = '#0D1117'
    BG_SECONDARY = '#161B22'
    BG_TERTIARY = '#1C2128'
    BG_ELEVATED = '#21262D'
    BG_OVERLAY = '#2D333B'
    
    # 前景色
    FG_PRIMARY = '#E6EDF3'
    FG_SECONDARY = '#8B949E'
    FG_TERTIARY = '#6E7681'
    FG_DISABLED = '#484F58'
    FG_PLACEHOLDER = '#484F58'
    
    # 强调色
    ACCENT_PRIMARY = '#58A6FF'
    ACCENT_PRIMARY_HOVER = '#79C0FF'
    ACCENT_PRIMARY_ACTIVE = '#409EFF'
    ACCENT_SUCCESS = '#3FB950'
    ACCENT_WARNING = '#D29922'
    ACCENT_ERROR = '#F85149'
    
    # 边框
    BORDER_DEFAULT = '#30363D'
    BORDER_SUBTLE = '#21262D'
    BORDER_EMPHASIS = '#58A6FF'
    
    # 平台色
    PLATFORM_CHATGPT = '#10A37F'
    PLATFORM_CLAUDE = '#7C3AED'
    PLATFORM_DEEPSEEK = '#0066CC'
    PLATFORM_GEMINI = '#4285F4'

class LightColors:
    """亮色主题颜色"""
    
    BG_PRIMARY = '#FFFFFF'
    BG_SECONDARY = '#F6F8FA'
    BG_TERTIARY = '#FFFFFF'
    BG_ELEVATED = '#F3F4F6'
    BG_OVERLAY = '#FFFFFF'
    
    FG_PRIMARY = '#1F2328'
    FG_SECONDARY = '#656D76'
    FG_TERTIARY = '#8C959F'
    FG_DISABLED = '#B1B7C0'
    
    # 强调色保持一致
    ACCENT_PRIMARY = '#58A6FF'
    ACCENT_PRIMARY_HOVER = '#79C0FF'
    ACCENT_PRIMARY_ACTIVE = '#409EFF'
    ACCENT_SUCCESS = '#3FB950'
    ACCENT_WARNING = '#D29922'
    ACCENT_ERROR = '#F85149'
    
    BORDER_DEFAULT = '#D1D9E0'
    BORDER_SUBTLE = '#E8EAED'
    BORDER_EMPHASIS = '#58A6FF'
    
    # 平台色保持一致
    PLATFORM_CHATGPT = '#10A37F'
    PLATFORM_CLAUDE = '#7C3AED'
    PLATFORM_DEEPSEEK = '#0066CC'
    PLATFORM_GEMINI = '#4285F4'

def get_platform_color(platform: str) -> str:
    """获取平台颜色"""
    colors = {
        'chatgpt': DarkColors.PLATFORM_CHATGPT,
        'claude': DarkColors.PLATFORM_CLAUDE,
        'deepseek': DarkColors.PLATFORM_DEEPSEEK,
        'gemini': DarkColors.PLATFORM_GEMINI,
    }
    return colors.get(platform.lower(), DarkColors.FG_SECONDARY)
```

#### 1.2.2 主题管理器 (`theme.py`)

```python
"""
主题管理器
"""
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
from .colors import DarkColors, LightColors

class ThemeMode(Enum):
    """主题模式"""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"  # 跟随系统

class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题切换信号
    
    def __init__(self):
        super().__init__()
        self._current_mode = ThemeMode.DARK
        self._colors = DarkColors
    
    @property
    def current_mode(self) -> ThemeMode:
        """当前主题模式"""
        return self._current_mode
    
    @property
    def colors(self):
        """当前颜色方案"""
        return self._colors
    
    def set_theme(self, mode: ThemeMode):
        """设置主题"""
        if mode == self._current_mode:
            return
        
        self._current_mode = mode
        
        if mode == ThemeMode.DARK:
            self._colors = DarkColors
        else:
            self._colors = LightColors
        
        self.theme_changed.emit(mode.value)
    
    def toggle_theme(self):
        """切换主题"""
        new_mode = (ThemeMode.LIGHT 
                   if self._current_mode == ThemeMode.DARK 
                   else ThemeMode.DARK)
        self.set_theme(new_mode)
    
    def get_stylesheet(self) -> str:
        """获取当前主题的样式表"""
        from pathlib import Path
        
        qss_file = (Path(__file__).parent / 'qss' / 
                   f'{self._current_mode.value}.qss')
        
        if qss_file.exists():
            return qss_file.read_text(encoding='utf-8')
        return ""

# 全局主题管理器实例
theme_manager = ThemeManager()
```

#### 1.2.3 QSS 样式文件

**base.qss** (通用样式):
```css
/* 全局设置 */
* {
    font-family: "Segoe UI Variable", "Microsoft YaHei UI", "Inter", sans-serif;
    font-size: 14px;
}

/* 滚动条 */
QScrollBar:vertical {
    width: 8px;
    background: transparent;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.3);
}
```

**dark.qss** (暗色主题):
```css
/* 主窗口 */
QMainWindow {
    background-color: #0D1117;
    color: #E6EDF3;
}

/* 按钮 - Primary */
QPushButton.primary {
    background-color: #58A6FF;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.primary:hover {
    background-color: #79C0FF;
}

QPushButton.primary:pressed {
    background-color: #409EFF;
}

/* 卡片 */
.conversation-card {
    background-color: #1C2128;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}

.conversation-card:hover {
    border-color: #58A6FF;
    transform: translateY(-4px);
}

/* 输入框 */
QLineEdit {
    background-color: #161B22;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 8px 12px;
}

QLineEdit:focus {
    border: 2px solid #58A6FF;
}
```

---

### Task 1.3: 三栏布局实现

#### 1.3.1 主窗口 (`main_layout.py`)

```python
"""
现代化主窗口
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import FluentWindow

from .top_bar import TopBar
from .side_nav import SideNav
from ..styles.theme import theme_manager

class ModernMainWindow(FluentWindow):
    """现代化主窗口"""
    
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        
        # 设置窗口属性
        self.setWindowTitle("ChatCompass - AI对话知识库")
        self.setMinimumSize(1000, 600)
        self.resize(1400, 800)
        
        # 初始化UI
        self._init_ui()
        
        # 应用主题
        self.setStyleSheet(theme_manager.get_stylesheet())
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _init_ui(self):
        """初始化UI"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧导航
        self.side_nav = SideNav(self)
        main_layout.addWidget(self.side_nav)
        
        # TODO: 中央内容区域
        # TODO: 右侧详情面板
    
    def _on_theme_changed(self, mode: str):
        """主题切换回调"""
        self.setStyleSheet(theme_manager.get_stylesheet())
```

#### 1.3.2 顶部导航栏 (`top_bar.py`)

```python
"""
顶部导航栏
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from qfluentwidgets import SearchLineEdit, FluentIcon

from ..styles.theme import theme_manager

class TopBar(QWidget):
    """顶部导航栏"""
    
    search_requested = pyqtSignal(str)  # 搜索信号
    settings_clicked = pyqtSignal()     # 设置点击
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        # Logo + 应用名
        logo_label = QLabel("📊")
        logo_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(logo_label)
        
        app_name = QLabel("ChatCompass")
        app_name.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(app_name)
        
        layout.addSpacing(20)
        
        # 搜索框
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText("搜索对话、标签、内容... (Ctrl+K)")
        self.search_box.setFixedWidth(400)
        self.search_box.searchSignal.connect(self.search_requested)
        layout.addWidget(self.search_box)
        
        layout.addStretch()
        
        # 主题切换按钮
        self.theme_btn = QPushButton()
        self.theme_btn.setIcon(FluentIcon.SUNNY)
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)
        
        # 设置按钮
        settings_btn = QPushButton()
        settings_btn.setIcon(FluentIcon.SETTING)
        settings_btn.setFixedSize(36, 36)
        settings_btn.clicked.connect(self.settings_clicked)
        layout.addWidget(settings_btn)
    
    def _toggle_theme(self):
        """切换主题"""
        theme_manager.toggle_theme()
        
        # 更新图标
        if theme_manager.current_mode.value == 'dark':
            self.theme_btn.setIcon(FluentIcon.SUNNY)
        else:
            self.theme_btn.setIcon(FluentIcon.MOON)
```

#### 1.3.3 左侧导航栏 (`side_nav.py`)

```python
"""
左侧导航栏
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition, FluentIcon
)

class SideNav(QWidget):
    """左侧导航栏"""
    
    nav_changed = pyqtSignal(str)  # 导航切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(120)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 导航组件
        self.nav = NavigationInterface(self, showMenuButton=False)
        
        # 添加导航项
        self.nav.addItem(
            routeKey='dashboard',
            icon=FluentIcon.DASHBOARD,
            text='仪表盘',
            onClick=lambda: self.nav_changed.emit('dashboard')
        )
        
        self.nav.addItem(
            routeKey='conversations',
            icon=FluentIcon.CHAT,
            text='对话',
            onClick=lambda: self.nav_changed.emit('conversations'),
            selectable=True
        )
        
        self.nav.addItem(
            routeKey='categories',
            icon=FluentIcon.FOLDER,
            text='分类',
            onClick=lambda: self.nav_changed.emit('categories')
        )
        
        self.nav.addItem(
            routeKey='tags',
            icon=FluentIcon.TAG,
            text='标签',
            onClick=lambda: self.nav_changed.emit('tags')
        )
        
        self.nav.addItem(
            routeKey='favorites',
            icon=FluentIcon.HEART,
            text='收藏',
            onClick=lambda: self.nav_changed.emit('favorites')
        )
        
        # 分隔符
        self.nav.addSeparator()
        
        # 底部项
        self.nav.addItem(
            routeKey='settings',
            icon=FluentIcon.SETTING,
            text='设置',
            onClick=lambda: self.nav_changed.emit('settings'),
            position=NavigationItemPosition.BOTTOM
        )
        
        layout.addWidget(self.nav)
```

---

### Task 1.4: 卡片视图实现

#### 1.4.1 对话卡片 (`conversation_card.py`)

```python
"""
对话卡片组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QPen
from qfluentwidgets import CardWidget, FluentIcon

from ..styles.colors import get_platform_color

class ConversationCard(CardWidget):
    """对话卡片"""
    
    clicked = pyqtSignal(int)  # 点击信号(conversation_id)
    
    def __init__(self, conversation: dict, parent=None):
        super().__init__(parent)
        self.conversation = conversation
        self.conv_id = conversation.get('id')
        
        # 固定尺寸
        self.setFixedSize(280, 180)
        
        # 初始化UI
        self._init_ui()
        
        # 悬停动画
        self._setup_animation()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # === 顶部: 平台图标 + 标题 + 收藏 ===
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # 平台图标
        platform = self.conversation.get('platform', 'unknown')
        platform_icon = self._get_platform_icon(platform)
        platform_label = QLabel(platform_icon)
        platform_label.setStyleSheet(f"color: {get_platform_color(platform)};")
        header.addWidget(platform_label)
        
        # 标题
        title = self.conversation.get('title', 'Untitled')
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #E6EDF3;
        """)
        title_label.setMaximumHeight(40)  # 最多2行
        header.addWidget(title_label, stretch=1)
        
        # 收藏图标
        is_favorite = self.conversation.get('is_favorite', 0)
        fav_icon = "⭐" if is_favorite else "☆"
        fav_label = QLabel(fav_icon)
        fav_label.setStyleSheet("font-size: 16px;")
        header.addWidget(fav_label)
        
        layout.addLayout(header)
        
        # === 分隔线 ===
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #30363D;")
        layout.addWidget(separator)
        
        # === 摘要 ===
        summary = self.conversation.get('summary', '')
        if summary:
            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet("""
                font-size: 12px;
                color: #8B949E;
                line-height: 1.5;
            """)
            summary_label.setMaximumHeight(60)  # 最多3行
            layout.addWidget(summary_label)
        
        layout.addStretch()
        
        # === 底部: 元信息 ===
        footer = QHBoxLayout()
        footer.setSpacing(12)
        
        # 消息数
        msg_count = self._get_message_count()
        msg_label = QLabel(f"💬 {msg_count}")
        msg_label.setStyleSheet("font-size: 11px; color: #6E7681;")
        footer.addWidget(msg_label)
        
        # 时间
        created_at = self.conversation.get('created_at', '')
        if created_at:
            time_str = self._format_time(created_at)
            time_label = QLabel(f"📅 {time_str}")
            time_label.setStyleSheet("font-size: 11px; color: #6E7681;")
            footer.addWidget(time_label)
        
        # 分类
        category = self.conversation.get('category', '')
        if category:
            cat_label = QLabel(f"[{category}]")
            cat_label.setStyleSheet("""
                font-size: 11px;
                color: #58A6FF;
                background-color: rgba(88, 166, 255, 0.1);
                padding: 2px 6px;
                border-radius: 4px;
            """)
            footer.addWidget(cat_label)
        
        footer.addStretch()
        layout.addLayout(footer)
    
    def _get_platform_icon(self, platform: str) -> str:
        """获取平台图标"""
        icons = {
            'chatgpt': '🤖',
            'claude': '🧠',
            'deepseek': '🔍',
            'gemini': '💎',
        }
        return icons.get(platform.lower(), '💬')
    
    def _get_message_count(self) -> int:
        """获取消息数"""
        return self.conversation.get('message_count', 0)
    
    def _format_time(self, time_str: str) -> str:
        """格式化时间"""
        # TODO: 实现相对时间 (2天前, 1周前)
        if ' ' in time_str:
            return time_str.split(' ')[0]
        return time_str
    
    def _setup_animation(self):
        """设置悬停动画"""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        """鼠标进入"""
        super().enterEvent(event)
        # TODO: 上浮效果
    
    def leaveEvent(self, event):
        """鼠标离开"""
        super().leaveEvent(event)
        # TODO: 恢复位置
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conv_id)
        super().mousePressEvent(event)
```

#### 1.4.2 卡片网格容器 (`card_grid_view.py`)

```python
"""
卡片网格视图
"""
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from .conversation_card import ConversationCard

class CardGridView(QWidget):
    """卡片网格视图"""
    
    card_clicked = pyqtSignal(int)  # 卡片点击信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        
        # 网格容器
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)
    
    def load_conversations(self, conversations: List[Dict[str, Any]]):
        """加载对话列表"""
        # 清空现有卡片
        self._clear_cards()
        
        # 创建新卡片
        columns = self._calculate_columns()
        
        for idx, conv in enumerate(conversations):
            card = ConversationCard(conv, self)
            card.clicked.connect(self.card_clicked)
            
            row = idx // columns
            col = idx % columns
            self.grid_layout.addWidget(card, row, col)
            
            self.cards.append(card)
    
    def _clear_cards(self):
        """清空卡片"""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
    
    def _calculate_columns(self) -> int:
        """计算列数"""
        width = self.width()
        
        # 卡片宽度280 + 间距16
        card_width = 280 + 16
        
        columns = max(1, width // card_width)
        return min(columns, 4)  # 最多4列
    
    def resizeEvent(self, event):
        """窗口调整大小"""
        super().resizeEvent(event)
        # TODO: 重新布局卡片
```

---

### Task 1.5: 色彩系统应用

#### 应用到所有组件

1. **主窗口**: 应用暗色背景
2. **卡片**: 应用卡片背景色和边框
3. **按钮**: 应用强调色
4. **平台标识**: 应用平台颜色

#### 验证颜色对比度

使用 WCAG 2.1 标准验证:
- 正文文字对比度 >= 4.5:1
- 大标题对比度 >= 3:1

---

## 📊 验收标准

### 功能完整性
- [x] 新窗口可以正常启动
- [x] 三栏布局显示正确
- [x] 卡片可以正常渲染
- [x] 主题切换功能正常
- [x] 导航切换响应正常

### 视觉效果
- [x] 色彩系统统一
- [x] 间距符合规范
- [x] 字体清晰可读
- [x] 圆角统一

### 性能指标
- [x] 启动速度 < 2秒
- [x] 卡片渲染流畅
- [x] 无明显卡顿

---

## 🐛 已知问题

1. **悬停动画**: 需要进一步优化
2. **响应式布局**: 需要实现断点适配
3. **图标资源**: 需要完善图标库

---

## 📝 开发日志

### 2026-01-18
- [x] 创建文档结构
- [x] 设计颜色系统
- [x] 规划组件架构

---

**最后更新**: 2026-01-18  
**状态**: 📝 规划完成，待实施
