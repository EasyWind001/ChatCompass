# ChatCompass - AI对话知识库管理系统

<div align="center">

**一站式管理你的AI对话，让知识不再流失**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v1.3.0-blue.svg)](https://github.com/yourusername/ChatCompass/releases)
[![Tests](https://img.shields.io/badge/Tests-136%20Passed-brightgreen.svg)](tests/)

[English](README_EN.md) | [功能特性](#-功能特性) | [快速开始](#-快速开始) | [文档](#-文档)

</div>

---

## 📖 项目简介

ChatCompass 是一款专为管理AI对话而设计的**本地知识库系统**。

### 🎯 核心优势

- 🖥️ **现代化GUI**：清爽简洁的图形界面，告别命令行
- 📋 **智能监控**：自动识别剪贴板中的AI对话链接
- ⚡ **异步处理**：后台并发爬取，实时进度显示
- 🔗 **一键导入**：支持ChatGPT、Claude、DeepSeek等主流平台
- 🤖 **智能分析**：自动生成摘要、分类和标签（可选）
- 🔍 **强大搜索**：全文检索+上下文定位，快速找到信息
- 📊 **数据安全**：本地SQLite存储，完全掌控你的数据

---

## ✨ 功能特性

### 🎯 v1.3.0 重大更新

| 功能 | 说明 | 状态 |
|------|------|------|
| **现代化GUI** | PyQt6图形界面，清爽简洁 | ✅ 已完成 |
| **系统托盘** | 后台运行，自动监控 | ✅ 已完成 |
| **异步队列** | 并发爬取+实时进度 | ✅ 已完成 |
| **剪贴板监控** | 自动识别AI链接 | ✅ 已完成 |
| **错误日志** | 完善的错误追踪 | ✅ 已完成 |
| **DeepSeek支持** | 新增平台支持 | ✅ 已完成 |

### 📦 支持的平台

| 平台 | 状态 | 说明 |
|------|------|------|
| **ChatGPT** | ✅ | 支持分享链接 |
| **Claude** | ✅ | 支持分享链接 |
| **DeepSeek** | ✅ | v1.3.0新增 |
| **Gemini** | 🚧 | 计划支持 |

### 🔍 搜索功能

- **上下文显示**：搜索结果显示匹配片段的前后文
- **精确定位**：标注匹配位置（第几条消息）
- **关键词高亮**：用【】包裹关键词
- **角色区分**：区分用户👤和助手🤖的消息
- **多处匹配**：支持一个对话中的多处匹配展示

---

## 🚀 快速开始

### 前置要求

- **Python 3.9+**
- **操作系统**: Windows / macOS / Linux

### 一键安装

```bash
# Windows
install.bat

# Linux/macOS
bash install.sh
```

### 手动安装

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ChatCompass.git
cd ChatCompass

# 2. 安装依赖
pip install -r requirements-gui.txt  # GUI完整版(推荐)
# 或
pip install -r requirements.txt      # 仅CLI版

# 3. 安装浏览器驱动
playwright install chromium

# 4. 配置（可选）
cp .env.example .env
# 编辑.env配置AI功能（可选，不配置也能正常使用）
```

### 启动应用

```bash
# GUI模式（推荐）
python main_gui.py

# 启用系统托盘监控
python main_gui.py --enable-tray

# 命令行模式
python main.py
```

---

## 💡 使用示例

### 🖥️ GUI模式

**快捷操作流程**：
1. 复制AI对话链接（如ChatGPT分享链接）
2. 自动弹窗询问是否添加
3. 点击"添加"按钮
4. 后台自动爬取，实时显示进度
5. 完成后自动刷新列表

**主要功能**：
- ✅ 对话列表查看与搜索
- ✅ 详情面板展示完整对话
- ✅ 系统托盘后台运行
- ✅ 剪贴板智能监控
- ✅ 异步队列管理

### 🖥️ 命令行模式

```bash
# 添加对话
python main.py add "https://chatgpt.com/share/xxxxx"

# 搜索对话
python main.py search "Python教程"

# 查看详情
python main.py show 1

# 查看统计
python main.py stats

# 交互模式
python main.py
ChatCompass> help
ChatCompass> search Python
ChatCompass> show 1
```

---

## 📁 项目结构

```
ChatCompass/
├── 📄 README.md                 # 项目主文档
├── 📄 CHANGELOG.md              # 版本更新日志
├── 📄 CONTRIBUTING.md           # 贡献指南
├── 📄 LICENSE                   # MIT许可证
│
├── 🎯 main.py                   # CLI命令行入口
├── 🖥️ main_gui.py               # GUI图形界面入口
├── ⚙️ config.py                 # 配置管理
│
├── 📦 requirements.txt          # 基础依赖
├── 📦 requirements-gui.txt      # GUI依赖
├── 🔧 .env.example              # 配置示例
│
├── 🛠️ install.bat / .sh          # 一键安装脚本
├── 🚀 run.bat / .sh              # 快速启动脚本
│
├── 🖥️ gui/                      # GUI模块
│   ├── main_window.py           # 主窗口
│   ├── conversation_list.py     # 对话列表
│   ├── detail_panel.py          # 详情面板
│   ├── clipboard_monitor.py     # 剪贴板监控
│   ├── system_tray.py           # 系统托盘
│   ├── task_queue.py            # 任务队列
│   ├── error_handler.py         # 错误处理
│   ├── modern/                  # 现代化组件(v1.4.0)
│   │   ├── layouts/             # 布局组件
│   │   ├── widgets/             # UI组件
│   │   └── styles/              # 样式系统
│   ├── widgets/                 # 标准组件
│   └── dialogs/                 # 对话框
│
├── 💾 database/                 # 数据库模块
│   ├── db_manager.py            # 数据库管理器
│   └── schema.sql               # 表结构定义
│
├── 🕷️ scrapers/                 # 网页爬虫模块
│   ├── base_scraper.py          # 爬虫基类
│   ├── chatgpt_scraper.py       # ChatGPT爬虫
│   ├── claude_scraper.py        # Claude爬虫
│   ├── deepseek_scraper.py      # DeepSeek爬虫
│   └── scraper_factory.py       # 爬虫工厂
│
├── 🤖 ai/                       # AI分析模块
│   ├── ollama_client.py         # Ollama本地模型
│   └── openai_client.py         # OpenAI/DeepSeek API
│
├── 🧪 tests/                    # 测试套件
│   ├── gui/                     # GUI测试 (76个)
│   ├── e2e/                     # E2E测试 (31个)
│   ├── unit/                    # 单元测试 (19个)
│   ├── integration/             # 集成测试 (10个)
│   └── manual/                  # 手动测试工具
│
└── 📚 docs/                     # 文档目录
    ├── INDEX.md                 # 文档索引
    ├── GUI_GUIDE.md             # GUI使用指南
    ├── TESTING_GUIDE.md         # 测试指南
    ├── v1.4.0/                  # v1.4.0文档
    └── legacy/                  # 历史文档归档
```

---

## 🧪 测试

项目包含**136个测试用例**，确保代码质量。

### 测试覆盖

| 类别 | 数量 | 说明 |
|------|------|------|
| GUI单元测试 | 76 | 主窗口、对话列表、详情面板等 |
| E2E测试 | 31 | GUI工作流、剪贴板监控 |
| 单元测试 | 19 | 数据库、爬虫、AI客户端 |
| 集成测试 | 10 | 完整流程测试 |
| **总计** | **136** | **100%通过率** |

### 运行测试

```bash
# 所有测试
pytest tests/ -v

# 特定类别
pytest tests/gui/ -v      # GUI测试
pytest tests/e2e/ -v      # E2E测试

# 渐进式测试（推荐）
python run_tests_interactive.py

# 覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

---

## 🔧 配置说明

### AI功能（可选）

> **注意**: 核心功能（添加、搜索、查看）无需配置AI即可使用。AI功能仅用于自动生成摘要和标签。

#### 方案1: 本地模式（推荐，免费）

```env
AI_MODE=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

**安装Ollama**：
1. 访问 https://ollama.ai 下载
2. 运行 `ollama pull qwen2.5:7b`
3. 启动 `ollama serve`

#### 方案2: 在线模式

```env
AI_MODE=online

# DeepSeek（推荐，性价比高）
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-chat

# 或使用OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

#### 禁用AI

```env
# 留空或不配置
AI_MODE=
```

---

## 📚 文档

### 核心文档
- **[文档索引](docs/INDEX.md)** - 所有文档导航
- **[GUI使用指南](docs/GUI_GUIDE.md)** - GUI功能详解
- **[测试指南](docs/TESTING_GUIDE.md)** - 测试说明
- **[贡献指南](CONTRIBUTING.md)** - 如何贡献代码
- **[更新日志](CHANGELOG.md)** - 版本历史

### 版本文档
- **[V1.4.0计划](docs/v1.4.0/README.md)** - 现代化UI改造
- **[V1.3.0文档](docs/)** - GUI图形界面版本
- **[V1.2.2文档](docs/)** - 搜索增强版本

### 技术文档
- **[项目总结](docs/PROJECT_SUMMARY.md)** - 技术架构
- **[搜索实现](docs/search_implementation.md)** - 搜索功能详解
- **[错误处理](docs/ERROR_HANDLING_GUIDE.md)** - 错误处理机制
- **[Docker指南](docs/DOCKER_BUILD_GUIDE.md)** - Docker部署

---

## 📝 更新日志

### v1.3.0 (2026-01-15) - GUI图形界面

**重大更新**：
- ✨ 全新GUI图形界面（PyQt6）
- ✨ 系统托盘监控
- ✨ 异步爬取队列
- ✨ 剪贴板自动识别
- ✨ 完善错误日志系统
- ✨ 新增DeepSeek平台支持
- 🧪 新增76个GUI测试+31个E2E测试

### v1.2.2 (2026-01-13) - 搜索增强

- ✨ 搜索结果显示上下文
- ✨ 精确标注匹配位置
- ✨ 关键词高亮显示
- ✨ 支持多处匹配展示

### v1.0.0 (2026-01-12) - 初始版本

- ✅ 基础功能完成
- ✅ ChatGPT和Claude支持
- ✅ 命令行界面
- ✅ 全文搜索功能

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)

---

## 🛠️ 技术栈

- **语言**: Python 3.9+
- **GUI**: PyQt6
- **数据库**: SQLite3 + FTS5（全文搜索）
- **爬虫**: Playwright + BeautifulSoup4
- **AI**: Ollama（本地）/ OpenAI API（在线）
- **测试**: Pytest + Coverage

---

## 🤝 贡献指南

我们欢迎并感谢任何形式的贡献！

### 快速开始

1. **Fork项目** 并克隆到本地
2. **创建分支**: `git checkout -b feature/your-feature`
3. **开发并测试**: 确保所有测试通过
4. **提交代码**: 遵循Commit规范
5. **创建PR**: 提交Pull Request

### 重要规范

- 📖 **完整指南**: [CONTRIBUTING.md](CONTRIBUTING.md)
- 🌳 **分支管理**: [docs/BRANCH_MANAGEMENT.md](docs/BRANCH_MANAGEMENT.md)
- 📝 **Commit规范**: Conventional Commits
- 🧪 **测试要求**: 所有测试必须通过
- 🔒 **安全规则**: SQL必须使用参数化查询

### 禁止操作

- ❌ 直接推送到main/develop分支
- ❌ 提交未经测试的代码
- ❌ SQL字符串拼接（SQL注入风险）
- ❌ 提交敏感信息（密码、密钥等）

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## ⚠️ 免责声明

本工具仅供个人学习和研究使用。使用本工具抓取第三方网站内容时，请遵守相关网站的服务条款和robots.txt规则。用户需自行承担使用本工具的法律责任。

---

## 💬 支持与反馈

- 📮 **提交Issue**: [GitHub Issues](https://github.com/yourusername/ChatCompass/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/yourusername/ChatCompass/discussions)
- 📧 **邮箱联系**: your.email@example.com
- 📖 **文档中心**: [docs/INDEX.md](docs/INDEX.md)

---

## 🙏 致谢

感谢以下开源项目：

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Ollama](https://ollama.ai/) - 本地大模型平台
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - 全文搜索引擎
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML解析

---

## ⭐ Star历史

如果这个项目对你有帮助，请给个⭐️吧！

---

<div align="center">

Made with ❤️ by ChatCompass Team

[⬆ 返回顶部](#chatcompass---ai对话知识库管理系统)

</div>
