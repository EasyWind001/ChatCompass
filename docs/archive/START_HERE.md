# 🚀 ChatCompass - 快速开始指南

## ✅ 程序状态
**已验证正常运行！所有功能都正常！**

---

## 🎯 三步快速开始

### 步骤1: 快速测试（推荐）
```bash
# Windows双击运行
QUICK_TEST.bat

# 或命令行
python quick_test.py
```
这将验证所有组件是否正常。

### 步骤2: 查看已有数据
```bash
python main.py stats
```
显示数据库中的对话统计。

### 步骤3: 尝试搜索
```bash
python main.py search Python
```
搜索包含"Python"的对话。

---

## 📖 使用方式

### 方式A: 交互模式（推荐）
```bash
python main.py
```
进入交互式命令行，可以使用以下命令：
- `help` - 查看帮助
- `list` - 列出最近对话
- `search <关键词>` - 搜索对话
- `stats` - 显示统计信息
- `add <url>` - 添加新对话
- `exit` - 退出程序

### 方式B: 命令行模式
```bash
# 查看统计
python main.py stats

# 搜索对话
python main.py search "关键词"

# 添加对话
python main.py add https://chatgpt.com/share/xxxxx
```

---

## 🎮 示例操作

### 示例1: 查看所有对话
```bash
> python main.py
ChatCompass> list

最近的 3 条对话:

[1] Python数据分析入门
    平台: chatgpt | 时间: 2024-01-10

[2] 写作技巧讨论
    平台: claude | 时间: 2024-01-09

[3] 机器学习算法
    平台: chatgpt | 时间: 2024-01-08
```

### 示例2: 搜索对话
```bash
> python main.py search Python

搜索: Python
找到 1 条结果:

[1] Python数据分析入门
    平台: chatgpt | 分类: 编程
    标签: Python, Pandas, 数据分析, NumPy
```

### 示例3: 查看统计
```bash
> python main.py stats

总对话数: 3

按平台:
  - chatgpt: 2
  - claude: 1

按分类:
  - 写作: 1
  - 编程: 2

总标签数: 16
```

---

## ⚙️ 配置说明

### 默认配置
- **AI模式**: local (Ollama)
- **数据库**: `./data/chatcompass.db`
- **支持平台**: ChatGPT, Claude

### 修改配置
创建 `.env` 文件修改配置：
```env
# AI配置
AI_MODE=local                              # local/online/hybrid
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# 数据库配置
DATABASE_PATH=./data/chatcompass.db

# 其他配置
LOG_LEVEL=INFO
LANGUAGE=zh_CN
```

---

## 🔧 常见问题

### Q: Ollama服务未运行？
**A**: 这不影响其他功能，仅AI分析功能需要Ollama。

如需启动Ollama:
```bash
ollama serve
```

### Q: 如何添加新对话？
**A**: 使用以下命令：
```bash
python main.py add <分享链接>

# 示例
python main.py add https://chatgpt.com/share/abc123
```

### Q: 如何查看测试结果？
**A**: 运行测试脚本：
```bash
# 快速测试
python quick_test.py

# 完整单元测试
python -m pytest tests/ -v
```

### Q: 数据存储在哪里？
**A**: SQLite数据库文件位于：
```
./data/chatcompass.db
```

---

## 📚 更多文档

- 📖 **README.md** - 项目完整说明
- ✅ **VERIFIED_WORKING.md** - 验证报告
- 🧪 **tests/README.md** - 测试说明
- 📊 **FINAL_TEST_SUCCESS.md** - 测试详情

---

## 🎯 功能特性

### ✅ 已实现功能
- ✅ 从ChatGPT、Claude导入对话
- ✅ SQLite数据库存储
- ✅ FTS5全文搜索
- ✅ 标签管理
- ✅ 分类统计
- ✅ 命令行界面
- ✅ AI分析（需Ollama）

### 🔜 计划功能
- 🔜 Web界面（PyQt6）
- 🔜 更多平台支持
- 🔜 导出功能
- 🔜 数据可视化

---

## 💪 技术栈

- **语言**: Python 3.8+
- **数据库**: SQLite 3 (FTS5)
- **AI**: Ollama / OpenAI / DeepSeek
- **测试**: Pytest
- **爬虫**: Requests + BeautifulSoup4

---

## 🎉 快速启动

```bash
# 1. 测试程序
python quick_test.py

# 2. 启动程序
python main.py

# 3. 开始使用！
ChatCompass> help
```

**祝使用愉快！🚀**

---

*如有问题，请查看文档或运行测试脚本排查。*
