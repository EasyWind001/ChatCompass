# v1.4.0 快速开始指南

## 🚀 5分钟快速上手

本指南帮助你快速了解 v1.4.0 改造项目的核心内容。

---

## 📖 第一步: 了解项目

### 阅读顺序 (5-10分钟)
1. **[README.md](README.md)** - 阅读"核心目标"和"设计理念"部分
2. **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - 浏览"色彩系统"和"组件规范"
3. **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - 查看"总体时间规划"

### 核心要点
- ✅ 目标: 现代化GUI，无年代感
- ✅ 风格: Fluent Design + Material You
- ✅ 周期: 3周 (Phase 1-3)
- ✅ 技术: PyQt6 + qfluentwidgets

---

## 🛠️ 第二步: 环境准备

### 安装依赖
```bash
# 进入项目目录
cd d:\Workspace\ChatCompass

# 安装新依赖
pip install PyQt6-Fluent-Widgets

# 验证安装
python -c "from qfluentwidgets import FluentWindow; print('✅ 安装成功')"
```

### 创建开发分支
```bash
# 创建 v1.4.0 开发分支
git checkout -b feature/v1.4.0-gui-modernization

# 或从现有分支拉取
git fetch origin
git checkout feature/v1.4.0-gui-modernization
```

---

## 📁 第三步: 创建目录结构

### 运行脚本
```bash
# Windows
mkdir gui\modern
mkdir gui\modern\layouts
mkdir gui\modern\widgets
mkdir gui\modern\dialogs
mkdir gui\modern\styles
mkdir gui\modern\styles\qss
mkdir gui\modern\animations

# Linux/macOS
mkdir -p gui/modern/{layouts,widgets,dialogs,styles/qss,animations}
```

### 创建初始文件
```bash
# 创建 __init__.py 文件
type nul > gui\modern\__init__.py
type nul > gui\modern\layouts\__init__.py
type nul > gui\modern\widgets\__init__.py
type nul > gui\modern\dialogs\__init__.py
type nul > gui\modern\styles\__init__.py
type nul > gui\modern\animations\__init__.py
```

---

## 🎨 第四步: 开始开发

### Phase 1 任务清单
参考 **[PHASE1_FOUNDATION.md](PHASE1_FOUNDATION.md)** 完成：

#### 1. 颜色系统 (1小时)
```python
# 创建 gui/modern/styles/colors.py
# 复制 PHASE1_FOUNDATION.md 中的颜色系统代码
```

#### 2. 主题管理器 (1小时)
```python
# 创建 gui/modern/styles/theme.py
# 复制 PHASE1_FOUNDATION.md 中的主题管理器代码
```

#### 3. QSS 样式 (2小时)
```css
/* 创建 gui/modern/styles/qss/dark.qss */
/* 复制 PHASE1_FOUNDATION.md 中的样式代码 */
```

#### 4. 主窗口布局 (4小时)
```python
# 创建 gui/modern/layouts/main_layout.py
# 复制 PHASE1_FOUNDATION.md 中的主窗口代码
```

#### 5. 对话卡片 (4小时)
```python
# 创建 gui/modern/widgets/conversation_card.py
# 复制 PHASE1_FOUNDATION.md 中的卡片代码
```

---

## ✅ 第五步: 测试验证

### 运行测试
```bash
# 启动新界面
python -c "
from PyQt6.QtWidgets import QApplication
from gui.modern.layouts.main_layout import ModernMainWindow
import sys

app = QApplication(sys.argv)
window = ModernMainWindow()
window.show()
sys.exit(app.exec())
"
```

### 验证清单
- [ ] 窗口正常启动
- [ ] 三栏布局显示正确
- [ ] 主题切换功能正常
- [ ] 导航栏响应正常
- [ ] 颜色系统应用正确

---

## 📝 第六步: 记录进度

### 更新 CHANGELOG.md
```markdown
#### [2026-01-XX] 完成 Task X.X
**新增**:
- ✅ 创建 xxx.py
- ✅ 实现 xxx 功能

**测试**:
- ✅ 功能测试通过
```

### 提交代码
```bash
# 添加文件
git add gui/modern/

# 提交
git commit -m "feat(v1.4.0): 实现 Phase 1 Task X.X"

# 推送
git push origin feature/v1.4.0-gui-modernization
```

---

## 🆘 遇到问题?

### 常见问题

**Q: qfluentwidgets 安装失败?**
```bash
# 尝试使用镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PyQt6-Fluent-Widgets
```

**Q: 导入报错?**
```python
# 确保项目根目录在 Python 路径中
import sys
sys.path.insert(0, 'd:/Workspace/ChatCompass')
```

**Q: 样式不生效?**
```python
# 检查 QSS 文件路径
from pathlib import Path
qss_path = Path('gui/modern/styles/qss/dark.qss')
print(f"文件存在: {qss_path.exists()}")
```

**Q: 主题切换无效?**
```python
# 确保连接信号
theme_manager.theme_changed.connect(self._on_theme_changed)
```

---

## 📚 下一步

完成 Phase 1 后:
1. 阅读 **PHASE2_INTERACTION.md** (待创建)
2. 开始实现动画系统
3. 优化搜索体验

---

## 🔗 快速链接

- [完整文档索引](INDEX.md)
- [设计系统规范](DESIGN_SYSTEM.md)
- [Phase 1 详细设计](PHASE1_FOUNDATION.md)
- [实施计划](IMPLEMENTATION_PLAN.md)

---

## 💡 开发技巧

### 使用代码片段
在 VSCode 中创建代码片段:
```json
{
  "Modern Component": {
    "prefix": "modern-component",
    "body": [
      "from PyQt6.QtWidgets import QWidget",
      "from qfluentwidgets import CardWidget",
      "",
      "class ${1:ComponentName}(CardWidget):",
      "    def __init__(self, parent=None):",
      "        super().__init__(parent)",
      "        self._init_ui()",
      "    ",
      "    def _init_ui(self):",
      "        pass"
    ]
  }
}
```

### 启用热重载
```python
# 使用 watchdog 实现热重载
pip install watchdog
```

### 调试技巧
```python
# 打印组件树
def print_widget_tree(widget, indent=0):
    print("  " * indent + widget.__class__.__name__)
    for child in widget.children():
        if isinstance(child, QWidget):
            print_widget_tree(child, indent + 1)
```

---

**预计完成时间**: Phase 1 约需 1周  
**难度**: ⭐⭐⭐☆☆ (中等)  
**建议**: 边做边记录，遇到问题及时更新文档

---

**最后更新**: 2026-01-18
