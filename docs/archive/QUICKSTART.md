# ChatCompass 快速启动指南

## 🚀 5分钟快速体验

### 步骤1: 运行演示
```bash
python demo.py
```

这将展示:
- ✅ 添加3条示例对话
- ✅ 查询所有对话
- ✅ 统计信息
- ✅ URL识别

### 步骤2: 启动交互模式
```bash
python main.py
```

可用命令:
```
ChatCompass> help          # 查看帮助
ChatCompass> list          # 列出最近对话
ChatCompass> stats         # 显示统计
ChatCompass> search Python # 搜索对话
ChatCompass> exit          # 退出
```

### 步骤3: 添加真实对话（可选）

如果你有ChatGPT或Claude的分享链接:
```bash
python main.py add "https://chatgpt.com/share/你的链接"
```

## 📁 查看数据

数据库文件:
- `demo.db` - 演示数据
- `data/chatcompass.db` - 实际数据

使用SQLite查看器（如DB Browser for SQLite）或:
```bash
sqlite3 demo.db "SELECT title, platform, category FROM conversations"
```

## 🔧 配置AI（可选）

### 本地模式（推荐）

1. 安装Ollama:
   - 访问 https://ollama.ai
   - 下载安装

2. 拉取模型:
```bash
ollama pull qwen2.5:7b
```

3. 启动服务:
```bash
ollama serve
```

4. 测试AI功能:
```python
from ai.ollama_client import OllamaClient

client = OllamaClient()
print(client.list_models())

result = client.analyze_conversation("测试对话内容...")
print(result.summary)
```

### 在线模式

编辑`.env`文件:
```env
AI_MODE=online
DEEPSEEK_API_KEY=your-api-key
```

获取API密钥:
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/

## 🐛 常见问题

### Q: 中文搜索没结果？
A: 这是已知问题。临时方案:
- 使用英文关键词
- 使用标签筛选
- 或参考`TEST_RESULTS.md`中的修复方案

### Q: 爬虫抓取失败？
A: 可能原因:
- 链接已过期
- 网络问题
- 需要更新Playwright: `playwright install chromium`

### Q: 数据库文件在哪？
A: 默认位置`data/chatcompass.db`

## 📚 更多帮助

- 完整文档: `README.md`
- 测试报告: `TEST_RESULTS.md`
- 搜索实现: `docs/search_implementation.md`
- 项目总结: `docs/PROJECT_SUMMARY.md`

## 🎯 下一步

1. 尝试添加真实的对话链接
2. 体验搜索功能
3. 查看统计信息
4. （可选）配置AI分析

祝使用愉快！ 🎉
