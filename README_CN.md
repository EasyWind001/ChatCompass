# ChatCompass - AI对话知识库管理系统

<div align="center">

**🧭 一站式管理你的AI对话，让知识不再流失**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20通过-brightgreen.svg)](tests/)
[![Version](https://img.shields.io/badge/Version-v1.2.6-orange.svg)](CHANGELOG.md)

[English](README.md) | 简体中文

</div>

## 📖 项目简介

ChatCompass 是一款专为管理AI对话而设计的本地知识库系统。无论是ChatGPT、Claude还是其他AI平台的对话，一键保存，永久管理。

### 为什么需要ChatCompass？

- 💡 **AI对话易丢失**：平台对话可能被删除或过期
- 🔍 **难以检索**：想找之前的对话却找不到
- 📝 **价值流失**：宝贵的AI对话内容没有归档
- 🔒 **隐私担忧**：对话存储在第三方平台

### ChatCompass能做什么？

- ✅ **一键导入**：粘贴分享链接，自动抓取对话
- ✅ **智能搜索**：全文检索+上下文定位，秒找想要的内容
- ✅ **永久保存**：本地SQLite数据库，完全掌控数据
- ✅ **AI辅助**：自动生成摘要、分类和标签（可选）
- ✅ **完全免费**：开源项目，本地运行，无需联网

## ✨ 核心功能

### 🔍 智能搜索（v1.2最新）

**上下文定位搜索** - 不只是找到关键词，还能看到前后文！

```
🔍 搜索: Python

  [1] 📄 Python数据分析教程
      💬 平台: chatgpt | 📁 分类: 编程
      📍 找到 2 处匹配:

         🤖 助手 (第 2/5 条消息)
         ...学习【Python】数据分析，建议从Pandas和NumPy开始...

         🤖 助手 (第 4/5 条消息)  
         ...【Python】在数据科学领域非常流行，因为...

      💡 输入 'show 1' 查看完整对话
```

**功能特点**：
- 显示匹配片段的前后80字符
- 精确标注位置（第几条消息）
- 关键词高亮显示【】
- 区分用户👤和助手🤖
- 支持多处匹配

### 📄 对话详情（v1.1）

```bash
$ python main.py show 1

======================================================================
对话详情 (ID: 1)
======================================================================

📝 标题: Python数据分析教程
🔗 链接: https://chatgpt.com/share/xxxxx
💬 平台: chatgpt
📅 时间: 2026-01-12

📊 统计:
  - 消息数: 5 条
  - 字数: 1234 字
  - 分类: 编程
  - 标签: Python, Pandas, 数据分析

💬 对话内容:
----------------------------------------------------------------------
👤 用户 (消息 1/5):
我想学习Python数据分析...

🤖 助手 (消息 2/5):
学习Python数据分析，建议从以下几个方面入手...
```

### 🤖 AI智能分析（可选）

- **自动摘要**：提取对话核心内容（100-150字）
- **智能分类**：编程、写作、学习、策划等
- **标签提取**：自动生成3-5个关键词

支持两种AI模式：
1. **本地模式**（推荐）：使用Ollama，完全免费
2. **在线模式**：使用OpenAI/DeepSeek API

### 📦 多平台支持

| 平台 | 状态 | 链接格式 |
|------|------|----------|
| ChatGPT | ✅ | `https://chatgpt.com/share/xxx` |
| Claude | ✅ | `https://claude.ai/share/xxx` |
| Gemini | 🚧 | 计划中 |
| DeepSeek | 🚧 | 计划中 |

## 🚀 快速开始

### 安装（3步完成）

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/ChatCompass.git
cd ChatCompass
```

#### 2. 一键安装（推荐）
```bash
# Windows用户
install.bat

# Mac/Linux用户  
bash install.sh
```

或手动安装：
```bash
pip install -r requirements.txt
playwright install chromium
```

#### 3. 开始使用
```bash
python main.py
```

就这么简单！🎉

### 基本使用

#### 添加对话
```bash
# 方式1：命令行
python main.py add "https://chatgpt.com/share/xxxxx"

# 方式2：交互模式
python main.py
ChatCompass> add https://chatgpt.com/share/xxxxx
```

#### 搜索对话
```bash
# 搜索关键词
python main.py search "Python教程"

# 交互模式
ChatCompass> search Python教程
```

#### 查看详情
```bash
# 查看ID为1的对话
python main.py show 1

# 交互模式
ChatCompass> show 1
```

#### 删除对话（v1.2.6新增）
```bash
# 通过ID删除
python main.py delete 1

# 通过URL删除
python main.py delete "https://chatgpt.com/share/xxxxx"

# 交互模式（需要确认）
ChatCompass> delete 1
⚠️  确认删除对话
ID: 1
标题: Python编程基础
...
确定删除吗？(yes/no): yes
✅ 删除成功
```

#### 查看统计
```bash
python main.py stats
```

### 完整示例

```bash
# 1. 启动程序
python main.py

# 2. 添加对话
ChatCompass> add https://chatgpt.com/share/6964e4ba-8264-8010-99ad-ab2399bb1dca
  [1/3] 抓取对话内容...
  [OK] 抓取成功: Vibe Coding规则解析
      - 消息数: 2
      - 字数: 1993

# 3. 搜索
ChatCompass> search 规则
  找到 1 条结果:
  [1] 📄 Vibe Coding规则解析
      📍 找到 1 处匹配...

# 4. 查看详情  
ChatCompass> show 1
  （显示完整对话）

# 5. 退出
ChatCompass> exit
```

## ⚙️ 配置说明

### 基础使用（无需配置）

ChatCompass的核心功能**无需任何配置**即可使用：
- ✅ 添加对话
- ✅ 搜索对话  
- ✅ 查看详情
- ✅ 统计信息

### AI功能配置（可选）

如果想要**自动摘要**和**智能标签**，可以配置AI：

#### 方式1：本地AI（推荐，免费）

```bash
# 1. 安装Ollama
# 访问 https://ollama.ai 下载安装

# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 启动服务
ollama serve

# 4. 配置.env
cp .env.example .env
# 编辑.env，设置AI_MODE=local
```

**优点**：
- ✅ 完全免费
- ✅ 完全离线
- ✅ 隐私保护

**缺点**：
- ❌ 需要8GB+内存
- ❌ 效果略逊于GPT-4

#### 方式2：在线AI

```env
# .env文件
AI_MODE=online

# 使用DeepSeek（推荐，性价比高）
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-chat

# 或使用OpenAI
OPENAI_API_KEY=your-api-key  
OPENAI_MODEL=gpt-4o-mini
```

**优点**：
- ✅ 效果好
- ✅ 无需本地算力

**缺点**：
- ❌ 需要联网
- ❌ 有使用成本（约$0.15/1M tokens）

#### 方式3：不使用AI（默认）

```env
# 留空或不配置
AI_MODE=
```

程序会跳过AI分析，其他功能正常使用。

## 📁 项目结构

```
ChatCompass/
├── main.py                   # 🎯 主程序入口
├── config.py                 # ⚙️ 配置管理
├── requirements.txt          # 📦 依赖列表
│
├── database/                 # 💾 数据库模块
│   ├── db_manager.py         # 数据库管理器
│   └── schema.sql            # 表结构定义
│
├── scrapers/                 # 🕷️ 爬虫模块
│   ├── chatgpt_scraper.py    # ChatGPT爬虫
│   ├── claude_scraper.py     # Claude爬虫
│   └── scraper_factory.py    # 爬虫工厂
│
├── ai/                       # 🤖 AI模块
│   ├── ollama_client.py      # Ollama客户端
│   └── openai_client.py      # OpenAI/DeepSeek客户端
│
├── tests/                    # 🧪 测试套件（52个测试）
│   ├── unit/                 # 单元测试
│   └── integration/          # 集成测试
│
└── docs/                     # 📚 文档
    ├── README.md             # 文档索引
    ├── *.md                  # 功能文档
    └── archive/              # 开发过程文档
```

详见：[README.md](README.md#-项目结构)

## 🎯 使用场景

### 场景1：学习笔记管理
> 和ChatGPT学习了Python，对话很有价值，想要保存下来

```bash
# 保存对话
python main.py add https://chatgpt.com/share/xxxxx

# 需要时搜索
python main.py search "Python列表"

# 查看完整内容
python main.py show 1
```

### 场景2：工作资料归档
> 用Claude帮忙写文案，想整理归档这些对话

```bash
# 批量添加
python main.py
ChatCompass> add https://claude.ai/share/aaa
ChatCompass> add https://claude.ai/share/bbb
ChatCompass> add https://claude.ai/share/ccc

# 按分类查看
ChatCompass> list --category 写作
```

### 场景3：知识库建设
> 积累了大量AI对话，想建立个人知识库

```bash
# 配置AI分析
# 启用自动摘要和标签

# 添加对话（自动分析）
python main.py add <URL>

# 查看统计
python main.py stats

# 按标签检索
python main.py search tag:Python
```

## 📊 大文本处理优化

ChatCompass对大文本对话（如3万+字符）进行了专门优化：

### 优化策略

1. **🔀 分段摘要合并**（核心策略）：超长对话按轮次智能分段，每段生成摘要后合并，保留100%关键信息
2. **⚡ 智能截断**：中等长度文本保留开头70% + 结尾30%，提升速度2-3倍
3. **📊 实时进度**：显示分段数、当前进度、预估时间
4. **⏱️ 超时保护**：默认180秒超时，可根据文本大小调整
5. **🌊 流式输出**：大文本显示生成进度，避免"假死"
6. **🛡️ 降级方案**：极端情况下使用基于规则的分析兜底

### 使用示例

```bash
# 自动应用所有优化
$ python main.py add "https://chatgpt.com/share/xxx"

[ChatGPT] 🌐 使用Playwright抓取
[ChatGPT] ✅ 成功提取 45 条消息（共 28,500 字符）
📊 开始分析对话（28,500 字符）...
💡 检测到超长文本，启用分段摘要策略...
📦 已分为 5 段（每段约 5,700 字符）

🔍 正在分析第 1/5 段...
  ✅ 第 1 段摘要: 用户询问Docker部署问题...
🔍 正在分析第 2/5 段...
  ✅ 第 2 段摘要: 讨论了多阶段构建优化...
[...]
🔗 合并 5 个分段摘要...
🎯 生成最终分析结果...
✅ 分段分析完成

✅ 对话已保存（ID: 123）
   📝 摘要: 用户系统学习Docker优化，从镜像构建到部署实践...
   📁 分类: 编程
   🏷️  标签: docker, 部署, 优化, devops
   ⭐ 置信度: 0.89
```

### 配置优化

```bash
# .env 文件
# 调整超时时间（秒）
AI_TIMEOUT=300  # 超大文本用300秒

# 或使用环境变量
export AI_TIMEOUT=300
```

详见：
- [分段摘要策略](docs/SEGMENT_SUMMARY_STRATEGY.md) ⭐ 推荐
- [大文本处理指南](docs/LARGE_TEXT_HANDLING.md)

### 超时保护 & 降级方案

**智能容错机制**：即使AI超时或失败，对话依然能保存！

```bash
# 场景：AI分析超时
❌ 分析超时: Ollama请求超时（180秒）
🔄 启动降级方案：生成基础摘要（基于规则）...
✅ 降级分析完成: 编程 | 标签: docker, python

✅ 对话已保存（ID: 123）
   📝 摘要: 用户询问Docker部署问题...（降级）
   📁 分类: 编程
   🏷️  标签: docker, python, 部署
   ⚠️  置信度: 0.3（基于规则）
```

**配置**：
```bash
# .env
AI_TIMEOUT=180              # 超时时间
AI_ENABLE_FALLBACK=true     # 启用降级方案（推荐）
```

详见：[AI降级方案](docs/FALLBACK_STRATEGY.md)

## 🧪 测试

项目包含完整的测试套件，确保代码质量。

### 运行测试

```bash
# Windows
run_tests.bat

# Mac/Linux
python run_tests.py

# 或使用pytest
pytest tests/ -v
```

### 测试结果

```
======================== 52 passed, 2 skipped =========================
执行时间: 4.8秒
通过率: 96.3%
```

**测试覆盖**：
- ✅ 数据库操作（13个）
- ✅ 爬虫功能（16个）  
- ✅ AI客户端（19个）
- ✅ 完整流程（4个）

## 📝 开发计划

### v1.3（计划中）
- [ ] GUI桌面界面
- [ ] 更多平台支持（Gemini、DeepSeek、Kimi）
- [ ] 导出功能（Markdown、PDF）
- [ ] 搜索语法增强（正则、高级过滤）

### v2.0（未来）
- [ ] 浏览器扩展（一键保存）
- [ ] 云端同步（可选）
- [ ] 协作分享
- [ ] 可视化统计

## 🤝 参与贡献

欢迎提交Issue和Pull Request！

### 如何贡献

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发指南

```bash
# 1. 克隆开发分支
git clone https://github.com/yourusername/ChatCompass.git
cd ChatCompass

# 2. 安装依赖
pip install -r requirements.txt
pip install pytest pytest-cov

# 3. 运行测试
pytest tests/ -v

# 4. 提交前检查
pytest tests/ --cov=. --cov-report=html
```

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)

## ⚠️ 免责声明

- 本工具仅供个人学习和研究使用
- 使用本工具抓取第三方网站内容时，请遵守相关网站的服务条款
- 用户需自行承担使用本工具的法律责任

## 💬 联系方式

- 📮 提交Issue: [GitHub Issues](https://github.com/yourusername/ChatCompass/issues)
- 📧 邮箱: your.email@example.com
- 💬 讨论区: [GitHub Discussions](https://github.com/yourusername/ChatCompass/discussions)

## 🙏 致谢

感谢以下开源项目：

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Ollama](https://ollama.ai/) - 本地大模型平台
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - 全文搜索引擎
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [Pytest](https://pytest.org/) - 测试框架

## ⭐ Star历史

如果这个项目对你有帮助，请给个⭐️吧！

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ChatCompass&type=Date)](https://star-history.com/#yourusername/ChatCompass&Date)

---

<div align="center">

**让AI对话成为永久的知识资产** 💎

Made with ❤️ by ChatCompass Team

[⬆ 返回顶部](#chatcompass---ai对话知识库管理系统)

</div>
