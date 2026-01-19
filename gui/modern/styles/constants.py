"""
设计系统常量
定义字体、间距、圆角、阴影等设计规范
"""

# ==================== 字体系统 ====================
class Fonts:
    """字体配置"""
    # 西文字体
    SANS_SERIF = "Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif"
    MONO = "Consolas, 'Courier New', monospace"
    
    # 中文字体
    CJK = "Microsoft YaHei UI, PingFang SC, Hiragino Sans GB, sans-serif"
    
    # 组合字体(优先西文,回退中文)
    PRIMARY = f"{SANS_SERIF}, {CJK}"
    CODE = f"{MONO}, {CJK}"
    
    # 字号
    SIZE_H1 = 24      # 大标题
    SIZE_H2 = 20      # 中标题
    SIZE_H3 = 16      # 小标题
    SIZE_BODY = 14    # 正文
    SIZE_SMALL = 12   # 小字
    SIZE_CAPTION = 11 # 说明文字
    
    # 字重
    WEIGHT_THIN = 100
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


# ==================== 间距系统 ====================
class Spacing:
    """间距配置(基于4px)"""
    XXS = 2    # 超小
    XS = 4     # 极小
    SM = 8     # 小
    MD = 12    # 中
    LG = 16    # 大
    XL = 20    # 极大
    XXL = 24   # 超大
    XXXL = 32  # 巨大
    XXXXL = 48 # 超级大
    
    # 常用组合
    CARD_PADDING = LG           # 卡片内边距
    SECTION_MARGIN = XXL        # 区块间距
    LIST_ITEM_SPACING = SM      # 列表项间距


# ==================== 圆角 ====================
class BorderRadius:
    """圆角配置"""
    NONE = 0
    SM = 4      # 小圆角(按钮、输入框)
    MD = 8      # 中圆角(卡片、面板)
    LG = 12     # 大圆角(模态框)
    XL = 16     # 超大圆角
    ROUND = 999 # 圆形(标签、头像)


# ==================== 阴影 ====================
class Shadows:
    """阴影配置"""
    # 暗色主题阴影
    DARK = {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.5)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.5)',
        'lg': '0 10px 20px rgba(0, 0, 0, 0.6)',
        'xl': '0 20px 40px rgba(0, 0, 0, 0.7)',
    }
    
    # 亮色主题阴影
    LIGHT = {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 20px rgba(0, 0, 0, 0.15)',
        'xl': '0 20px 40px rgba(0, 0, 0, 0.2)',
    }


# ==================== 动画时长 ====================
class Duration:
    """动画时长(毫秒)"""
    FAST = 150      # 快速(按钮点击、悬停)
    NORMAL = 250    # 正常(面板展开、切换)
    SLOW = 300      # 慢速(页面过渡)
    VERY_SLOW = 500 # 超慢(特殊动画)


# ==================== 缓动函数 ====================
class Easing:
    """缓动曲线"""
    EASE = "ease"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    LINEAR = "linear"
    
    # 自定义贝塞尔曲线
    SMOOTH = "cubic-bezier(0.4, 0, 0.2, 1)"  # Material Design
    BOUNCE = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"


# ==================== 尺寸规范 ====================
class Sizes:
    """组件尺寸"""
    # 顶栏高度
    TOPBAR_HEIGHT = 56
    
    # 侧边栏宽度
    SIDEBAR_WIDTH_EXPANDED = 120
    SIDEBAR_WIDTH_COLLAPSED = 64
    
    # 详情面板宽度
    DETAIL_PANEL_WIDTH = 400
    DETAIL_PANEL_MIN_WIDTH = 300
    DETAIL_PANEL_MAX_WIDTH = 600
    
    # 卡片尺寸
    CARD_WIDTH = 280
    CARD_HEIGHT = 180
    CARD_MIN_WIDTH = 240
    
    # 按钮高度
    BUTTON_HEIGHT_SM = 28
    BUTTON_HEIGHT_MD = 36
    BUTTON_HEIGHT_LG = 44
    
    # 输入框高度
    INPUT_HEIGHT = 36
    
    # 图标尺寸
    ICON_SM = 16
    ICON_MD = 20
    ICON_LG = 24
    ICON_XL = 32


# ==================== Z-Index层级 ====================
class ZIndex:
    """层级顺序"""
    BASE = 0            # 基础层
    CARD = 1            # 卡片层
    DROPDOWN = 10       # 下拉菜单
    STICKY = 100        # 固定元素
    MODAL_BACKDROP = 900   # 模态框背景
    MODAL = 1000        # 模态框
    POPOVER = 1100      # 弹出框
    TOOLTIP = 1200      # 提示框
    NOTIFICATION = 1300 # 通知


# ==================== 断点 ====================
class Breakpoints:
    """响应式断点"""
    SM = 768    # 小屏幕
    MD = 1024   # 中等屏幕
    LG = 1400   # 大屏幕
    XL = 1920   # 超大屏幕
