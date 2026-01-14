# 全文搜索与高亮显示实现方案

## 一、技术架构

### 1.1 核心技术
- **SQLite FTS5**：全文搜索引擎
- **snippet()函数**：自动生成带高亮的摘要片段
- **rank排序**：按相关度排序搜索结果

### 1.2 数据流程
```
用户输入关键词
    ↓
前端GUI捕获输入
    ↓
调用DatabaseManager.search_conversations()
    ↓
执行FTS5 MATCH查询
    ↓
使用snippet()生成高亮片段
    ↓
按rank排序返回结果
    ↓
GUI展示结果列表（高亮显示）
```

## 二、数据库层实现

### 2.1 FTS5虚拟表配置

```sql
-- 创建全文搜索虚拟表
CREATE VIRTUAL TABLE conversations_fts USING fts5(
    title,                    -- 标题字段
    summary,                  -- 摘要字段
    raw_content,              -- 完整对话内容
    content='conversations',  -- 关联到主表
    content_rowid='id',       -- 使用id作为rowid
    tokenize='porter unicode61 remove_diacritics 1'  -- 分词器
);
```

**分词器说明**：
- `porter`：英文词干提取（searching → search）
- `unicode61`：支持Unicode字符（中文、日文等）
- `remove_diacritics 1`：移除变音符号

### 2.2 自动同步触发器

```sql
-- 插入时同步
CREATE TRIGGER conversations_ai AFTER INSERT ON conversations BEGIN
    INSERT INTO conversations_fts(rowid, title, summary, raw_content)
    VALUES (new.id, new.title, new.summary, new.raw_content);
END;

-- 更新时同步
CREATE TRIGGER conversations_au AFTER UPDATE ON conversations BEGIN
    UPDATE conversations_fts 
    SET title = new.title, 
        summary = new.summary, 
        raw_content = new.raw_content
    WHERE rowid = new.id;
END;

-- 删除时同步
CREATE TRIGGER conversations_ad AFTER DELETE ON conversations BEGIN
    DELETE FROM conversations_fts WHERE rowid = old.id;
END;
```

### 2.3 搜索查询实现

```python
def search_conversations(self, keyword: str, limit: int = 50) -> List[Dict]:
    """全文搜索对话"""
    cursor = self.conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id, 
            c.title, 
            c.summary, 
            c.source_url, 
            c.platform, 
            c.category, 
            c.created_at,
            snippet(conversations_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
        FROM conversations_fts
        JOIN conversations c ON conversations_fts.rowid = c.id
        WHERE conversations_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (keyword, limit))
    
    return [dict(row) for row in cursor.fetchall()]
```

**snippet()函数参数说明**：
- 参数1：虚拟表名
- 参数2：列索引（2=raw_content）
- 参数3：高亮开始标记（`<mark>`）
- 参数4：高亮结束标记（`</mark>`）
- 参数5：省略符号（`...`）
- 参数6：最大token数（32）

## 三、搜索功能特性

### 3.1 支持的搜索语法

| 语法 | 说明 | 示例 |
|------|------|------|
| 单词搜索 | 搜索包含该词的文档 | `Python` |
| 短语搜索 | 精确匹配短语 | `"机器学习"` |
| AND操作 | 同时包含多个词 | `Python AND 数据分析` |
| OR操作 | 包含任一词 | `Python OR Java` |
| NOT操作 | 排除某词 | `Python NOT 入门` |
| 前缀搜索 | 词前缀匹配 | `prog*` (匹配program, programming) |
| 列搜索 | 指定列搜索 | `title:Python` |

### 3.2 搜索示例

```python
# 示例1：简单关键词搜索
results = db.search_conversations("Python")

# 示例2：短语搜索
results = db.search_conversations('"机器学习算法"')

# 示例3：组合搜索
results = db.search_conversations("Python AND (数据分析 OR 机器学习)")

# 示例4：只搜索标题
results = db.search_conversations("title:教程")

# 示例5：前缀搜索
results = db.search_conversations("prog*")
```

## 四、GUI层实现

### 4.1 搜索界面组件

```python
from PyQt6.QtWidgets import QLineEdit, QListWidget, QTextBrowser

class SearchWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索对话内容...")
        self.search_input.textChanged.connect(self.on_search)
        
        # 结果列表
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.on_result_clicked)
        
        # 详情展示
        self.detail_view = QTextBrowser()
        self.detail_view.setOpenExternalLinks(False)
    
    def on_search(self, text):
        """实时搜索"""
        if len(text) < 2:  # 至少2个字符才搜索
            return
        
        # 执行搜索
        results = self.db.search_conversations(text, limit=50)
        
        # 更新结果列表
        self.result_list.clear()
        for result in results:
            item_text = f"{result['title']} - {result['platform']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.result_list.addItem(item)
    
    def on_result_clicked(self, item):
        """点击结果项"""
        result = item.data(Qt.ItemDataRole.UserRole)
        
        # 显示详情（带高亮）
        html = self.format_result_html(result)
        self.detail_view.setHtml(html)
    
    def format_result_html(self, result) -> str:
        """格式化结果为HTML（保留高亮）"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h2 {{ color: #2563EB; }}
                .meta {{ color: #6B7280; font-size: 14px; }}
                .snippet {{ 
                    background: #F3F4F6; 
                    padding: 15px; 
                    border-radius: 8px;
                    margin: 15px 0;
                }}
                mark {{ 
                    background: #FEF08A; 
                    color: #000;
                    font-weight: bold;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                .tags {{ margin-top: 10px; }}
                .tag {{ 
                    display: inline-block;
                    background: #DBEAFE;
                    color: #1E40AF;
                    padding: 4px 12px;
                    border-radius: 12px;
                    margin-right: 8px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <h2>{result['title']}</h2>
            <div class="meta">
                平台: {result['platform']} | 
                分类: {result.get('category', '未分类')} | 
                时间: {result['created_at']}
            </div>
            
            <div class="snippet">
                {result['snippet']}
            </div>
            
            <div class="tags">
                {''.join(f'<span class="tag">{tag}</span>' for tag in result.get('tags', []))}
            </div>
            
            <p><a href="{result['source_url']}">查看原始链接</a></p>
        </body>
        </html>
        """
        return html
```

### 4.2 高亮显示效果

搜索关键词"Python数据分析"时的显示效果：

```
标题: Python数据分析入门教程
平台: chatgpt | 分类: 编程 | 时间: 2026-01-12

内容片段:
...学习<mark>Python</mark>进行<mark>数据分析</mark>，首先需要掌握NumPy和Pandas库。
这两个库是<mark>Python</mark><mark>数据分析</mark>的基础工具...

标签: [Python] [数据分析] [pandas] [教程]
```

## 五、性能优化

### 5.1 索引优化

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_conversations_platform ON conversations(platform);
CREATE INDEX idx_conversations_category ON conversations(category);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

### 5.2 搜索优化策略

1. **防抖动**：用户输入时延迟300ms再搜索
```python
from PyQt6.QtCore import QTimer

class SearchWidget:
    def __init__(self):
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.do_search)
    
    def on_search_input(self, text):
        # 重置定时器（防抖）
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms后执行
    
    def do_search(self):
        # 实际执行搜索
        pass
```

2. **分页加载**：大量结果时分页显示
```python
def search_with_pagination(keyword, page=1, page_size=20):
    offset = (page - 1) * page_size
    return db.search_conversations(keyword, limit=page_size, offset=offset)
```

3. **缓存结果**：相同搜索词缓存结果
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(keyword):
    return db.search_conversations(keyword)
```

### 5.3 大数据量处理

当对话数量超过10000条时：

1. **优化FTS5配置**
```sql
-- 使用更高效的分词器
CREATE VIRTUAL TABLE conversations_fts USING fts5(
    title, summary, raw_content,
    content='conversations',
    content_rowid='id',
    tokenize='trigram'  -- 三元组分词（适合中文）
);
```

2. **定期优化索引**
```python
def optimize_fts_index():
    """优化FTS索引（定期执行）"""
    cursor = db.conn.cursor()
    cursor.execute("INSERT INTO conversations_fts(conversations_fts) VALUES('optimize')")
    db.conn.commit()
```

## 六、用户体验增强

### 6.1 搜索建议

```python
def get_search_suggestions(prefix: str, limit=5) -> List[str]:
    """根据输入前缀提供搜索建议"""
    cursor = db.conn.cursor()
    
    # 从标签中获取建议
    cursor.execute("""
        SELECT DISTINCT name FROM tags 
        WHERE name LIKE ? 
        ORDER BY usage_count DESC 
        LIMIT ?
    """, (f"{prefix}%", limit))
    
    return [row[0] for row in cursor.fetchall()]
```

### 6.2 搜索历史

```python
class SearchHistory:
    def __init__(self, max_size=20):
        self.history = []
        self.max_size = max_size
    
    def add(self, keyword):
        if keyword in self.history:
            self.history.remove(keyword)
        self.history.insert(0, keyword)
        self.history = self.history[:self.max_size]
    
    def get_recent(self, limit=10):
        return self.history[:limit]
```

### 6.3 高级搜索面板

```python
class AdvancedSearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        # 关键词
        self.keyword_input = QLineEdit()
        
        # 平台筛选
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['全部', 'ChatGPT', 'Claude', 'Gemini'])
        
        # 分类筛选
        self.category_combo = QComboBox()
        self.category_combo.addItems(['全部', '编程', '写作', '学习', '策划'])
        
        # 日期范围
        self.date_from = QDateEdit()
        self.date_to = QDateEdit()
        
        # 标签筛选
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("输入标签，用逗号分隔")
    
    def build_query(self) -> str:
        """构建高级搜索查询"""
        parts = []
        
        keyword = self.keyword_input.text()
        if keyword:
            parts.append(keyword)
        
        # 可以构建更复杂的FTS5查询
        return ' AND '.join(parts)
```

## 七、测试用例

```python
def test_search():
    db = DatabaseManager("test.db")
    
    # 测试1：简单搜索
    results = db.search_conversations("Python")
    assert len(results) > 0
    assert '<mark>Python</mark>' in results[0]['snippet']
    
    # 测试2：短语搜索
    results = db.search_conversations('"机器学习"')
    assert all('<mark>机器学习</mark>' in r['snippet'] for r in results)
    
    # 测试3：组合搜索
    results = db.search_conversations("Python AND 数据分析")
    assert len(results) > 0
    
    # 测试4：空结果
    results = db.search_conversations("不存在的关键词xyz123")
    assert len(results) == 0
    
    print("所有测试通过！")
```

## 八、总结

### 核心优势
1. ✅ **高性能**：FTS5原生支持，速度快
2. ✅ **自动高亮**：snippet()函数自动生成高亮片段
3. ✅ **智能排序**：按相关度(rank)排序
4. ✅ **多语言支持**：中英文混合搜索
5. ✅ **实时同步**：触发器自动维护索引

### 实现要点
- 使用FTS5虚拟表而非LIKE查询
- 利用snippet()函数自动生成摘要和高亮
- 通过触发器保持索引同步
- GUI层使用HTML渲染高亮效果
- 添加防抖、缓存等性能优化

### 扩展方向
- 支持拼音搜索（中文）
- 模糊搜索（容错）
- 语义搜索（向量数据库）
- 搜索结果导出
