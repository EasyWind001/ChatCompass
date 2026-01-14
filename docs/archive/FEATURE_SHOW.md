# ✨ 新功能: show命令 - 查看对话详细内容

## 📋 功能概述

`show` 命令允许您查看单个对话的完整详细内容，包括：
- 基本信息（标题、链接、平台、时间）
- 统计数据（消息数、字数、分类、标签）
- 摘要和备注
- 完整对话内容

---

## 🚀 使用方法

### 方式1: 命令行模式

```bash
# 通过ID查看
python main.py show 1
python main.py show 4

# 通过URL查看
python main.py show "https://chatgpt.com/share/xxxxx"
```

### 方式2: 交互模式

```bash
python main.py

ChatCompass> show 1
ChatCompass> show 4
ChatCompass> show https://chatgpt.com/share/xxxxx
```

---

## 💡 功能特性

### ✅ 支持双重查询
- **通过ID查询**: `show 1`, `show 4`
- **通过URL查询**: `show https://chatgpt.com/...`

### ✅ 完整信息展示
```
======================================================================
对话详情 (ID: 4)
======================================================================

📝 标题: Vibe Coding规则解析
🔗 链接: https://chatgpt.com/share/6964e4ba-8264-8010-99ad-ab2399bb1dca
💬 平台: chatgpt
📅 时间: 2026-01-12 13:10:32

📊 统计:
  - 消息数: 2 条
  - 字数: 2416 字
  - 分类: 编程
  - 标签: Python, AI, 编程

📄 摘要:
  这是AI生成的对话摘要...

💬 对话内容:
----------------------------------------------------------------------

👤 用户 (消息 1/2):
您好，我想了解...

----------------------------------------------------------------------

🤖 助手 (消息 2/2):
根据您的问题...

======================================================================
```

### ✅ 智能图标
- 👤 用户消息
- 🤖 助手消息
- ⭐ 收藏标记
- 📝 标题
- 🔗 链接
- 💬 平台
- 📅 时间
- 📊 统计
- 📄 摘要
- 📌 备注

---

## 📖 使用示例

### 示例1: 快速查看对话
```bash
> python main.py show 1

📝 标题: Python数据分析入门
💬 平台: chatgpt
📊 统计:
  - 消息数: 2 条
  - 字数: 234 字
```

### 示例2: 结合list使用
```bash
> python main.py

ChatCompass> list

最近的 4 条对话:

  [1] Python数据分析入门
      平台: chatgpt | 时间: 2026-01-12 12:25:16
      提示: 输入 'show 1' 查看详情

  [4] Vibe Coding规则解析
      平台: chatgpt | 时间: 2026-01-12 13:10:32
      提示: 输入 'show 4' 查看详情

ChatCompass> show 4
（显示详细内容...）
```

### 示例3: 通过URL查看
```bash
ChatCompass> show https://chatgpt.com/share/6964e4ba-8264-8010-99ad-ab2399bb1dca

对话详情 (ID: 4)
标题: Vibe Coding规则解析
...
```

---

## 🎯 典型工作流

### 工作流1: 浏览和查看
```bash
1. python main.py               # 进入交互模式
2. ChatCompass> list            # 查看所有对话
3. ChatCompass> show 4          # 查看感兴趣的对话
4. ChatCompass> search "Python" # 搜索相关内容
5. ChatCompass> show 1          # 查看搜索结果
```

### 工作流2: 添加和验证
```bash
1. python main.py add <URL>     # 添加新对话
2. python main.py show <URL>    # 验证添加结果
```

### 工作流3: 命令行快速查看
```bash
# 一条命令直接查看
python main.py show 4
```

---

## 🔍 技术细节

### 查询逻辑
1. 首先尝试作为ID查询（如果是数字）
2. 如果失败，尝试作为URL查询
3. 都失败则提示未找到

### 数据来源
- 基本信息: `conversations` 表
- 标签信息: `conversation_tags` 和 `tags` 表
- 对话内容: `raw_content` 字段（JSON格式）

### 兼容性
- 支持字符串和字典两种 `raw_content` 格式
- 自动处理JSON解析
- 友好的错误提示

---

## 📊 对比其他命令

| 命令 | 用途 | 信息量 |
|------|------|--------|
| `list` | 列出所有对话 | 标题、平台、时间 |
| `search` | 搜索对话 | 标题、片段、标签 |
| `show` | 查看详情 | **完整内容** ⭐ |
| `stats` | 统计信息 | 数量、分布 |

---

## 💪 高级用法

### 用法1: 结合搜索精确定位
```bash
ChatCompass> search "Vibe Coding"
找到 1 条结果:
[1] Vibe Coding规则解析 (ID: 4)

ChatCompass> show 4
（查看完整内容）
```

### 用法2: 验证对话质量
```bash
# 添加对话后立即查看
ChatCompass> add https://chatgpt.com/share/xxxxx
  [OK] 保存成功 (ID: 5)

ChatCompass> show 5
（验证内容是否正确抓取）
```

### 用法3: 复习和学习
```bash
# 查看之前保存的优质对话
ChatCompass> show 1
（完整阅读对话内容）
```

---

## 🎨 输出格式

### 分段显示
1. **对话详情** - 70个等号分隔线
2. **基本信息** - 标题、链接、平台、时间
3. **统计信息** - 消息数、字数、分类、标签
4. **摘要备注** - AI生成的摘要和用户备注
5. **对话内容** - 完整的用户-助手对话
6. **结束标记** - 70个等号分隔线

### 颜色和图标
- 使用Emoji增强可读性
- 清晰的视觉层次
- 分隔线明确区分内容

---

## ⚠️ 注意事项

### 1. ID vs URL
```bash
# ID查询（推荐，速度快）
show 1
show 4

# URL查询（适合外部链接）
show https://chatgpt.com/share/xxxxx
```

### 2. 长对话显示
对于消息数很多的对话，内容会很长。建议：
- 使用管道: `python main.py show 4 | less`
- 或在交互模式中逐步查看

### 3. 查询失败
```bash
ChatCompass> show 999

未找到对话: 999
提示: 使用 'list' 命令查看所有对话
```

---

## 🔄 更新历史

### v1.0 (2026-01-12)
- ✅ 实现基本show命令
- ✅ 支持ID和URL双重查询
- ✅ 完整信息展示
- ✅ 美化输出格式
- ✅ 命令行和交互模式支持

---

## 📚 相关命令

- `list` - 列出所有对话
- `search` - 搜索对话
- `add` - 添加新对话
- `stats` - 查看统计
- `help` - 查看帮助

---

## 🎉 总结

`show` 命令是ChatCompass的**核心功能**之一，让您能够：
- 🔍 快速定位和查看对话
- 📖 完整阅读对话内容
- ✅ 验证对话质量
- 💡 复习和学习优质对话

**立即尝试**: `python main.py show 1` 🚀

---

**功能开发**: 2026-01-12  
**当前版本**: v1.0  
**状态**: ✅ 完全可用
