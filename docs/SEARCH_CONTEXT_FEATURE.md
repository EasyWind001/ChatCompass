# 搜索功能增强 - 上下文定位

## 功能概述

增强了搜索功能，现在可以：
- ✅ 显示匹配片段的上下文（前后文）
- ✅ 精确定位匹配位置（第几条消息）
- ✅ 高亮显示搜索关键词
- ✅ 区分用户和助手的消息
- ✅ 支持一个对话中的多处匹配

## 功能演示

### 1. 基本搜索
```bash
python main.py search "规则"
```

**输出示例：**
```
🔍 搜索: 规则
  找到 1 条结果:

  [1] 📄 Vibe Coding规则解析
      💬 平台: chatgpt | 📁 分类: None
      📍 找到 1 处匹配:

         🤖 助手 (第 2/2 条消息)
         ...非核心但复杂的 glue code
快速试错型产品探索
二、Vibe Coding 的核心 Rules（不是规范，是协作原则）
可以总结为
6 条非显性的"潜【规则】"
。
Rule 1：人给「意图」，模型给「实现」...

      💡 输入 'show 4' 查看完整对话
```

### 2. 多处匹配
```bash
python main.py search "模型"
```

**输出示例：**
```
🔍 搜索: 模型
  找到 1 条结果:

  [1] 📄 Vibe Coding规则解析
      💬 平台: chatgpt | 📁 分类: None
      📍 找到 3 处匹配:

         🤖 助手 (第 2/2 条消息)
         ChatGPT said:
"Vibe Coding"并不是一个严格定义的工程方法论，更像是一种在
大【模型】辅助编程
场景下逐渐形成的...

         🤖 助手 (第 2/2 条消息)
         ...工作风格（coding style / workflow）
。它的核心不是代码规范本身，而是
人如何与【模型】协作完成软件构建...

         🤖 助手 (第 2/2 条消息)
         ...一句话定义：
Vibe Coding 是一种
以意图和感觉驱动、由大【模型】负责"落地细节"、人类只做方向与判断...

      💡 输入 'show 4' 查看完整对话
```

## 技术实现

### 1. 数据库层 (`database/db_manager.py`)

新增方法：`_extract_context_matches()`

```python
def _extract_context_matches(self, 
                             raw_content: str, 
                             keyword: str, 
                             context_size: int = 100) -> List[Dict]:
    """
    从对话内容中提取匹配片段及其上下文
    
    Returns:
        匹配片段列表，每个片段包含：
        - role: 消息角色（user/assistant）
        - message_index: 消息序号
        - match_text: 匹配的文本（高亮）
        - before_context: 前文
        - after_context: 后文
        - position: 在对话中的位置
    """
```

**核心特性：**
- 遍历所有消息，查找关键词
- 提取匹配位置前后的上下文（默认100字符）
- 自动添加省略号（...）标识截断
- 限制每条消息最多3个匹配（避免输出过多）
- 保留完整消息文本以便后续查看

### 2. 主程序层 (`main.py`)

增强方法：`search()`

```python
def search(self, keyword: str):
    """搜索对话（增强版：显示上下文定位）"""
    results = self.db.search_conversations(keyword, limit=10, context_size=80)
    
    # 显示匹配片段（带上下文）
    for match in matches:
        role_icon = "👤" if match['role'] == 'user' else "🤖"
        role_name = "用户" if match['role'] == 'user' else "助手"
        
        context = (
            match['before_context'] + 
            f"【{match['match_text']}】" + 
            match['after_context']
        )
```

**显示格式：**
- 使用Emoji图标区分角色（👤用户 / 🤖助手）
- 显示消息位置（第几条/共几条）
- 用【】高亮关键词
- 格式化输出上下文
- 最多显示前3个匹配，超过则提示

## 配置参数

### `search_conversations()` 方法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `keyword` | str | - | 搜索关键词 |
| `limit` | int | 50 | 最多返回结果数 |
| `context_size` | int | 100 | 上下文字符数 |

### 调整上下文长度

如果觉得上下文太长或太短，可以修改调用参数：

```python
# 更长的上下文（150字符）
results = self.db.search_conversations(keyword, limit=10, context_size=150)

# 更短的上下文（50字符）
results = self.db.search_conversations(keyword, limit=10, context_size=50)
```

## 使用场景

### 场景1：快速定位关键信息
当你记得某个对话讨论了某个话题，但不记得具体在哪里：
```bash
python main.py search "数据库设计"
```
搜索结果会直接显示相关片段的上下文，帮你快速判断是否是要找的内容。

### 场景2：追溯讨论过程
查看某个关键词在对话中的所有出现位置：
```bash
python main.py search "优化"
```
如果一个对话中多次提到"优化"，会显示所有匹配位置，帮你了解讨论的演进过程。

### 场景3：精确定位后查看详情
搜索找到目标后，使用 `show` 命令查看完整对话：
```bash
# 先搜索
python main.py search "API设计"

# 根据搜索结果，查看详情
python main.py show 5
```

## 交互模式示例

```
ChatCompass> search 模型

🔍 搜索: 模型
  找到 1 条结果:

  [1] 📄 Vibe Coding规则解析
      💬 平台: chatgpt | 📁 分类: None
      📍 找到 3 处匹配:
      
      ...（显示匹配片段）...
      
      💡 输入 'show 4' 查看完整对话

ChatCompass> show 4

（显示完整对话内容）
```

## 技术优势

### 1. **智能上下文提取**
- 自动计算合适的上下文范围
- 处理边界情况（开头/结尾）
- 添加省略号标识

### 2. **多层级搜索**
- 优先使用FTS5全文搜索（性能最优）
- 回退到LIKE模糊搜索（兼容性最好）
- 统一的上下文提取逻辑

### 3. **用户友好显示**
- Emoji图标直观区分角色
- 清晰的位置标识（第几条消息）
- 高亮关键词便于快速定位
- 限制显示数量避免信息过载

### 4. **无缝集成**
- 保持原有API兼容性
- 仅新增可选参数
- 不影响现有代码

## 限制和注意事项

1. **每条消息最多显示3个匹配**
   - 避免单条消息占用过多输出空间
   - 如需查看所有匹配，使用 `show` 命令

2. **上下文字符数限制**
   - 默认前后各100字符
   - 可通过参数调整

3. **中文字符支持**
   - 已完美支持UTF-8编码
   - Windows控制台已设置正确编码

## 未来优化方向

- [ ] 支持正则表达式搜索
- [ ] 支持多关键词组合搜索（AND/OR）
- [ ] 支持按消息角色过滤搜索
- [ ] 支持导出搜索结果
- [ ] 支持搜索结果排序（相关度/时间）

## 测试验证

运行演示脚本：
```bash
python demo_search_context.py
```

运行单元测试：
```bash
pytest tests/ -v -k search
```

## 版本信息

- **版本**: v1.2.0
- **更新日期**: 2026-01-13
- **作者**: ChatCompass团队
- **相关文件**:
  - `database/db_manager.py`
  - `main.py`
  - `demo_search_context.py`
