# 设计系统规范 - ChatCompass v1.4.0

## 📐 设计系统总览

本文档定义了 ChatCompass v1.4.0 的完整设计系统，包括颜色、字体、间距、组件规范等。

---

## 🎨 色彩系统

### 暗色主题 (Dark Mode) - 默认

#### 背景色阶
```python
BACKGROUND = {
    'primary': '#0D1117',      # 主背景 (最深)
    'secondary': '#161B22',    # 二级背景
    'tertiary': '#1C2128',     # 卡片背景
    'elevated': '#21262D',     # 悬停背景
    'overlay': '#2D333B',      # 浮层背景
}
```

#### 前景色阶
```python
FOREGROUND = {
    'primary': '#E6EDF3',      # 主文字 (最清晰)
    'secondary': '#8B949E',    # 次要文字
    'tertiary': '#6E7681',     # 三级文字
    'disabled': '#484F58',     # 禁用文字
    'placeholder': '#484F58',  # 占位符
}
```

#### 强调色
```python
ACCENT = {
    'primary': '#58A6FF',      # 主色调 (蓝色)
    'primary_hover': '#79C0FF',
    'primary_active': '#409EFF',
    
    'success': '#3FB950',      # 成功 (绿色)
    'warning': '#D29922',      # 警告 (橙色)
    'error': '#F85149',        # 错误 (红色)
    'info': '#58A6FF',         # 信息 (蓝色)
}
```

#### 平台识别色
```python
PLATFORM = {
    'chatgpt': '#10A37F',      # ChatGPT (青绿)
    'claude': '#7C3AED',       # Claude (紫色)
    'deepseek': '#0066CC',     # DeepSeek (蓝色)
    'gemini': '#4285F4',       # Gemini (谷歌蓝)
    'unknown': '#6E7681',      # 未知平台
}
```

#### 边框和分隔
```python
BORDER = {
    'default': '#30363D',      # 默认边框
    'subtle': '#21262D',       # 微妙边框
    'emphasis': '#58A6FF',     # 强调边框
}
```

---

### 亮色主题 (Light Mode)

#### 背景色阶
```python
BACKGROUND_LIGHT = {
    'primary': '#FFFFFF',      # 主背景
    'secondary': '#F6F8FA',    # 二级背景
    'tertiary': '#FFFFFF',     # 卡片背景 (带阴影)
    'elevated': '#F3F4F6',     # 悬停背景
    'overlay': '#FFFFFF',      # 浮层背景
}
```

#### 前景色阶
```python
FOREGROUND_LIGHT = {
    'primary': '#1F2328',      # 主文字
    'secondary': '#656D76',    # 次要文字
    'tertiary': '#8C959F',     # 三级文字
    'disabled': '#B1B7C0',     # 禁用文字
    'placeholder': '#8C959F',  # 占位符
}
```

#### 边框和分隔
```python
BORDER_LIGHT = {
    'default': '#D1D9E0',      # 默认边框
    'subtle': '#E8EAED',       # 微妙边框
    'emphasis': '#58A6FF',     # 强调边框
}
```

**注意**: 强调色和平台识别色在亮色模式下保持一致

---

## 🔤 字体系统

### 字体族
```python
FONT_FAMILY = {
    # 西文字体
    'en_primary': ['Segoe UI Variable', 'Inter', 'SF Pro Display'],
    
    # 中文字体
    'zh_primary': ['Microsoft YaHei UI', '思源黑体', 'PingFang SC'],
    
    # 等宽字体 (代码/链接)
    'monospace': ['JetBrains Mono', 'Fira Code', 'Consolas'],
    
    # 完整 fallback
    'default': [
        'Segoe UI Variable', 'Inter', 
        'Microsoft YaHei UI', '思源黑体',
        'SF Pro Display', 'PingFang SC',
        'Arial', 'sans-serif'
    ]
}
```

### 字号阶梯
```python
FONT_SIZE = {
    'xs': 11,      # 极小 (辅助信息)
    'sm': 12,      # 小 (次要文字)
    'base': 14,    # 基础 (正文)
    'md': 16,      # 中等 (小标题)
    'lg': 18,      # 大 (标题)
    'xl': 20,      # 特大 (主标题)
    'xxl': 24,     # 超大 (页面标题)
}
```

### 字重
```python
FONT_WEIGHT = {
    'light': 300,
    'regular': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
}
```

### 行高
```python
LINE_HEIGHT = {
    'tight': 1.2,      # 紧凑 (标题)
    'normal': 1.5,     # 正常 (正文)
    'relaxed': 1.75,   # 宽松 (长文本)
}
```

---

## 📏 间距系统

### 间距阶梯 (基于 4px)
```python
SPACING = {
    'xs': 4,       # 0.25rem
    'sm': 8,       # 0.5rem
    'md': 12,      # 0.75rem
    'base': 16,    # 1rem (基准)
    'lg': 20,      # 1.25rem
    'xl': 24,      # 1.5rem
    'xxl': 32,     # 2rem
    'xxxl': 48,    # 3rem
}
```

### 组件内边距
```python
PADDING = {
    'button': (8, 16),           # (垂直, 水平)
    'card': (16, 16),
    'panel': (20, 20),
    'dialog': (24, 24),
}
```

### 组件外边距
```python
MARGIN = {
    'component': 16,     # 组件之间
    'section': 24,       # 区块之间
    'page': 32,          # 页面边距
}
```

---

## 🔲 圆角系统

```python
RADIUS = {
    'none': 0,
    'sm': 4,       # 小圆角 (按钮)
    'base': 8,     # 基础圆角 (卡片)
    'md': 12,      # 中等圆角 (面板)
    'lg': 16,      # 大圆角 (对话框)
    'full': 9999,  # 全圆角 (标签)
}
```

---

## 🌫️ 阴影系统

### 阴影层级
```python
SHADOW = {
    'none': 'none',
    
    # 暗色模式阴影
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    'base': '0 2px 4px 0 rgba(0, 0, 0, 0.4)',
    'md': '0 4px 8px 0 rgba(0, 0, 0, 0.5)',
    'lg': '0 8px 16px 0 rgba(0, 0, 0, 0.6)',
    'xl': '0 12px 24px 0 rgba(0, 0, 0, 0.7)',
    
    # 亮色模式阴影
    'sm_light': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'base_light': '0 2px 4px 0 rgba(0, 0, 0, 0.1)',
    'md_light': '0 4px 8px 0 rgba(0, 0, 0, 0.12)',
    'lg_light': '0 8px 16px 0 rgba(0, 0, 0, 0.15)',
    'xl_light': '0 12px 24px 0 rgba(0, 0, 0, 0.18)',
}
```

### 使用场景
- `sm`: 按钮、标签
- `base`: 卡片、输入框
- `md`: 下拉菜单
- `lg`: 对话框、浮层
- `xl`: 模态框

---

## ⚡ 动画系统

### 时长
```python
DURATION = {
    'fast': 150,       # 快速 (悬停反馈)
    'base': 250,       # 基础 (页面切换)
    'slow': 350,       # 慢速 (复杂动画)
}
```

### 缓动函数
```python
EASING = {
    'linear': 'linear',
    'ease_in': 'cubic-bezier(0.4, 0, 1, 1)',
    'ease_out': 'cubic-bezier(0, 0, 0.2, 1)',       # 推荐
    'ease_in_out': 'cubic-bezier(0.4, 0, 0.2, 1)',
    'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',  # 弹性
}
```

### Qt 对应
```python
QT_EASING = {
    'linear': QEasingCurve.Type.Linear,
    'ease_out': QEasingCurve.Type.OutCubic,
    'ease_in_out': QEasingCurve.Type.InOutCubic,
    'spring': QEasingCurve.Type.OutBack,
}
```

---

## 🧩 组件规范

### 按钮 (Button)

#### 尺寸
```python
BUTTON_SIZE = {
    'small': {
        'height': 28,
        'padding': (6, 12),
        'font_size': 12,
    },
    'medium': {
        'height': 36,
        'padding': (8, 16),
        'font_size': 14,
    },
    'large': {
        'height': 44,
        'padding': (12, 24),
        'font_size': 16,
    },
}
```

#### 类型
- **Primary**: 主要操作，强调色背景
- **Secondary**: 次要操作，边框样式
- **Text**: 文本按钮，无背景

---

### 卡片 (Card)

#### 标准卡片
```python
CARD = {
    'width': 280,
    'height': 180,
    'padding': 16,
    'radius': 12,
    'shadow': 'base',
    'border': '1px solid BORDER.default',
}
```

#### 状态
- **Normal**: 默认状态
- **Hover**: 上浮 4px + 阴影加深
- **Active**: 边框高亮
- **Disabled**: 透明度 0.5

---

### 输入框 (Input)

#### 规格
```python
INPUT = {
    'height': 36,
    'padding': (8, 12),
    'radius': 8,
    'border': '1px solid BORDER.default',
    'focus_border': '2px solid ACCENT.primary',
}
```

#### 状态
- **Normal**: 默认边框
- **Focus**: 蓝色边框 + 外发光
- **Error**: 红色边框
- **Disabled**: 灰色背景

---

### 标签 (Tag)

```python
TAG = {
    'height': 24,
    'padding': (4, 10),
    'radius': 9999,  # 全圆角
    'font_size': 12,
}
```

---

## 📱 响应式断点

```python
BREAKPOINTS = {
    'xs': 0,        # 手机
    'sm': 640,      # 大手机
    'md': 1024,     # 平板
    'lg': 1400,     # 桌面
    'xl': 1920,     # 大屏
}
```

### 布局规则
- `< 1024px`: 单栏布局
- `1024-1400px`: 两栏布局（导航 + 内容）
- `>= 1400px`: 三栏布局（导航 + 内容 + 详情）

---

## 🎯 图标系统

### 图标库
- **主要**: Phosphor Icons (Regular weight)
- **备用**: Fluent UI System Icons

### 图标尺寸
```python
ICON_SIZE = {
    'xs': 14,
    'sm': 16,
    'base': 20,
    'md': 24,
    'lg': 32,
    'xl': 48,
}
```

### 图标颜色
- 默认跟随文字颜色
- 强调时使用 `ACCENT.primary`
- 平台图标使用 `PLATFORM` 颜色

---

## 🔧 实现示例

### QSS 样式模板

```css
/* 按钮 - Primary */
QPushButton#primary {
    background-color: #58A6FF;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#primary:hover {
    background-color: #79C0FF;
}

QPushButton#primary:pressed {
    background-color: #409EFF;
}

/* 卡片 */
QWidget#card {
    background-color: #1C2128;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}

QWidget#card:hover {
    border-color: #58A6FF;
}
```

### Python 常量定义

```python
# gui/modern/styles/colors.py
class DarkTheme:
    """暗色主题"""
    BG_PRIMARY = '#0D1117'
    BG_SECONDARY = '#161B22'
    BG_TERTIARY = '#1C2128'
    
    FG_PRIMARY = '#E6EDF3'
    FG_SECONDARY = '#8B949E'
    
    ACCENT_PRIMARY = '#58A6FF'
    ACCENT_SUCCESS = '#3FB950'
    ACCENT_ERROR = '#F85149'

class LightTheme:
    """亮色主题"""
    BG_PRIMARY = '#FFFFFF'
    BG_SECONDARY = '#F6F8FA'
    
    # ...
```

---

## 📋 检查清单

在实现新组件时，确保：

- [ ] 颜色符合色彩系统定义
- [ ] 字体使用系统字体族
- [ ] 间距遵循 4px 基准
- [ ] 圆角使用预定义值
- [ ] 阴影选择合适层级
- [ ] 动画时长合理
- [ ] 支持暗色/亮色主题
- [ ] 响应式适配
- [ ] 图标尺寸一致

---

## 🔄 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-01-18 | 初始版本 |

---

**最后更新**: 2026-01-18  
**维护者**: ChatCompass Team
