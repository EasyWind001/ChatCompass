# ChatCompass 文档索引

> **最后更新**: 2026-01-19

---

## 📚 核心文档

### 用户指南
- **[README.md](../README.md)** - 项目主页，快速开始
- **[README_CN.md](../README_CN.md)** - 中文完整文档
- **[README_EN.md](../README_EN.md)** - English documentation
- **[CHANGELOG.md](../CHANGELOG.md)** - 版本更新日志

### 功能指南
- **[GUI_GUIDE.md](GUI_GUIDE.md)** - GUI图形界面使用指南
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 测试指南
- **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)** - 错误处理指南
- **[DOCKER_BUILD_GUIDE.md](DOCKER_BUILD_GUIDE.md)** - Docker构建指南

### 开发指南
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - 贡献指南
- **[BRANCH_MANAGEMENT.md](BRANCH_MANAGEMENT.md)** - 分支管理规范
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目技术总结

---

## 🚀 版本文档

### V1.4.0 - 现代化UI改造
**目录**: [`docs/v1.4.0/`](v1.4.0/)

- **[README.md](v1.4.0/README.md)** - V1.4.0项目概览
- **[V1.4.0_MODERNIZATION_PLAN.md](v1.4.0/V1.4.0_MODERNIZATION_PLAN.md)** - 现代化改造总规划
- **[DESIGN_SYSTEM.md](v1.4.0/DESIGN_SYSTEM.md)** - 设计系统文档
- **[IMPLEMENTATION_PLAN.md](v1.4.0/IMPLEMENTATION_PLAN.md)** - 实施计划
- **[PHASE1_FOUNDATION.md](v1.4.0/PHASE1_FOUNDATION.md)** - 阶段1基础改造
- **[PHASE1_PROGRESS.md](v1.4.0/PHASE1_PROGRESS.md)** - 阶段1进度
- **[LIGHT_THEME_DESIGN.md](v1.4.0/LIGHT_THEME_DESIGN.md)** - 亮色主题设计
- **[COLOR_ADJUSTMENT.md](v1.4.0/COLOR_ADJUSTMENT.md)** - 颜色调整
- **[CHANGELOG.md](v1.4.0/CHANGELOG.md)** - V1.4.0更新日志

### V1.3.0 - GUI图形界面
**目录**: [`docs/v1.3.0/`](v1.3.0/) (待整理)

核心特性：
- ✅ GUI图形界面
- ✅ 系统托盘监控
- ✅ 异步爬取队列
- ✅ 完善错误处理

文档：
- **[V1.3.0_PLAN.md](V1.3.0_PLAN.md)** - V1.3.0开发计划
- **[V1.3.0_RELEASE_NOTES.md](V1.3.0_RELEASE_NOTES.md)** - 发布说明
- **[V1.3.0_ERROR_HANDLING_IMPLEMENTATION.md](V1.3.0_ERROR_HANDLING_IMPLEMENTATION.md)** - 错误处理实施

### V1.2.2 - 搜索增强
核心特性：
- ✅ 搜索上下文定位
- ✅ 关键词高亮
- ✅ 多处匹配展示

文档：
- **[search_implementation.md](search_implementation.md)** - 搜索实现文档
- **[SEARCH_CONTEXT_FEATURE.md](SEARCH_CONTEXT_FEATURE.md)** - 搜索上下文功能

---

## 🗂️ 文档分类

### 技术文档
- **[FALLBACK_STRATEGY.md](FALLBACK_STRATEGY.md)** - 多层回退策略
- **[LARGE_TEXT_HANDLING.md](LARGE_TEXT_HANDLING.md)** - 大文本处理
- **[SEGMENT_SUMMARY_STRATEGY.md](SEGMENT_SUMMARY_STRATEGY.md)** - 分段摘要策略
- **[PERFORMANCE_TIPS.md](PERFORMANCE_TIPS.md)** - 性能优化技巧

### Docker文档
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Docker使用指南
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Docker快速开始

### 测试文档
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 测试指南
- **[PROGRESSIVE_TESTING_GUIDE.md](PROGRESSIVE_TESTING_GUIDE.md)** - 渐进式测试指南
- **[PROGRESSIVE_TESTING_SUMMARY.md](PROGRESSIVE_TESTING_SUMMARY.md)** - 渐进式测试总结

---

## 📦 归档文档

历史文档已移至：**[`docs/legacy/`](legacy/)**

包含：
- 各版本修复报告
- 测试完成报告
- 开发过程文档
- GitHub发布文档
- 快速开始指南（旧版）

**注意**: 归档文档仅供参考，可能已过时。

---

## 🧪 测试相关

### 手动测试工具
**目录**: [`tests/manual/`](../tests/manual/)

- `test_modern_ui_v2.py` - V2现代化界面测试
- `test_modern_ui.py` - V1现代化界面测试
- `ui_automation_v2_test.py` - UI自动化测试
- `ui_validation_v2.py` - UI验证工具
- `test_clipboard_monitor_fix.py` - 剪贴板监控测试
- `test_search_debug.py` - 搜索调试工具
- `quick_test_e2e.py` - 快速E2E测试
- `launch_v2_test.bat` - V2测试启动器

### 自动化测试
**目录**: [`tests/`](../tests/)

- `tests/gui/` - GUI单元测试 (76个)
- `tests/e2e/` - E2E端到端测试 (31个)
- `tests/unit/` - 单元测试 (19个)
- `tests/integration/` - 集成测试 (10个)

**运行测试**:
```bash
# 所有测试
pytest tests/ -v

# 特定类别
pytest tests/gui/ -v
pytest tests/e2e/ -v

# 渐进式测试
python run_tests_interactive.py
```

---

## 🔍 快速查找

### 我想...
- **开始使用** → [README.md](../README.md)
- **了解GUI功能** → [GUI_GUIDE.md](GUI_GUIDE.md)
- **贡献代码** → [CONTRIBUTING.md](../CONTRIBUTING.md)
- **查看更新** → [CHANGELOG.md](../CHANGELOG.md)
- **使用Docker** → [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **运行测试** → [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **了解V1.4.0** → [v1.4.0/README.md](v1.4.0/README.md)
- **查看技术细节** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### 遇到问题？
- **错误处理** → [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)
- **性能问题** → [PERFORMANCE_TIPS.md](PERFORMANCE_TIPS.md)
- **Docker问题** → [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **测试失败** → [PROGRESSIVE_TESTING_GUIDE.md](PROGRESSIVE_TESTING_GUIDE.md)

---

## 📝 文档规范

### 文档命名
- **核心文档**: 大写+下划线 (e.g., `GUI_GUIDE.md`)
- **版本文档**: 版本号前缀 (e.g., `V1.3.0_PLAN.md`)
- **归档文档**: 移至 `docs/legacy/`

### 文档结构
```markdown
# 标题

> **元信息**: 版本、日期、状态等

---

## 内容章节
...

---

## 相关链接
...
```

---

<div align="center">

**📖 更多文档**: [docs/](.)  
**🏠 返回主页**: [README.md](../README.md)  
**📬 问题反馈**: [GitHub Issues](https://github.com/yourusername/ChatCompass/issues)

Made with ❤️ by ChatCompass Team

</div>
