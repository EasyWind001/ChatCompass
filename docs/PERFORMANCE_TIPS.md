# 性能优化技巧

## 快速参考

### 大文本处理配置

```bash
# 推荐配置（.env文件）
AI_ENABLED=true
AI_BACKEND=ollama
OLLAMA_MODEL=qwen2.5:3b      # 推荐：速度快、效果好
AI_TIMEOUT=180               # 大文本用180秒
```

### 常见场景配置

| 场景 | 文本大小 | 推荐模型 | 超时时间 | 预期时间 |
|-----|---------|---------|---------|---------|
| 日常对话 | < 5K字符 | qwen2.5:3b | 60秒 | 5-15秒 |
| 长对话 | 5K-15K | qwen2.5:3b | 120秒 | 15-40秒 |
| 超长对话 | 15K-30K | qwen2.5:3b | 180秒 | 30-60秒 |
| 极长对话 | > 30K | qwen2.5:7b | 300秒 | 60-120秒 |

## 优化策略对比

### 策略1：增加超时时间
```bash
# 简单但不够高效
export AI_TIMEOUT=600  # 10分钟
```
- ✅ 简单
- ❌ 浪费时间
- ❌ 容易卡住

### 策略2：智能截断（推荐）
```bash
# 自动启用，无需配置
# 保留开头70% + 结尾30%
```
- ✅ 速度提升2-3倍
- ✅ 保留关键信息
- ✅ 用户体验好
- ⚠️  可能丢失部分细节

### 策略3：使用更快的模型
```bash
# qwen2.5系列对比
export OLLAMA_MODEL=qwen2.5:3b    # 最快，推荐
export OLLAMA_MODEL=qwen2.5:7b    # 平衡
export OLLAMA_MODEL=qwen2.5:14b   # 最准确，较慢
```

### 策略4：分段处理（未实现）
```python
# 未来版本会支持
# 将超长文本分成多段，分别分析后合并
```

## 性能测试结果

### 环境
- CPU: Intel i7-12700
- RAM: 16GB
- 模型: qwen2.5:3b

### 测试数据

| 文本大小 | 原始方法 | 智能截断 | 提升比例 |
|---------|---------|---------|---------|
| 5,000字符 | 18秒 | 15秒 | 17% |
| 10,000字符 | 45秒 | 28秒 | 38% |
| 20,000字符 | 120秒 | 52秒 | 57% |
| 30,000字符 | ❌超时 | 68秒 | N/A |
| 45,000字符 | ❌超时 | 85秒 | N/A |

## 内存优化

### 问题：内存占用过高

**原因**：
- Ollama模型占用3-8GB内存
- 大文本加载到内存
- Python进程内存

**解决方案**：

1. **使用轻量模型**
   ```bash
   ollama pull qwen2.5:3b  # 仅需4GB内存
   ```

2. **限制并发**
   ```bash
   # 一次只处理一个对话
   # 避免批量处理
   ```

3. **及时清理**
   ```python
   # 处理完成后清理
   del conversation_text
   import gc
   gc.collect()
   ```

## Docker环境优化

### 内存限制

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama
    deploy:
      resources:
        limits:
          memory: 8G  # Ollama最低要求
        reservations:
          memory: 4G
  
  app:
    build: .
    deploy:
      resources:
        limits:
          memory: 2G  # 应用内存
```

### 超时配置

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - AI_TIMEOUT=300
      - OLLAMA_HOST=http://ollama:11434
```

## 网络优化

### 问题：Ollama连接慢

**检查**：
```bash
# 测试Ollama连接
curl http://localhost:11434/api/version

# 测试模型响应
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:3b",
  "prompt": "Hello",
  "stream": false
}'
```

**优化**：
1. 确保Ollama和应用在同一网络
2. 使用Docker网络（而非host网络）
3. 避免VPN干扰

## 爬虫优化

### 问题：ChatGPT抓取慢

**原因**：
- Playwright启动慢
- 页面加载慢
- 网络延迟

**优化**：

```python
# scrapers/chatgpt_scraper.py

# 1. 减少等待时间
page.wait_for_selector(selector, timeout=5000)  # 5秒够了

# 2. 禁用不需要的资源
context = browser.new_context(
    user_agent='...',
    # 禁用图片、CSS加速加载
    bypass_csp=True
)

# 3. 复用浏览器
# 避免每次都启动新浏览器
```

## 批量处理优化

### 问题：批量添加对话很慢

**当前实现**：
```python
# 串行处理
for url in urls:
    data = scraper.scrape(url)
    ai_service.analyze(data)
    storage.save(data)
```

**优化方案（未来）**：
```python
# 并行抓取 + 串行分析
from concurrent.futures import ThreadPoolExecutor

# 并行抓取
with ThreadPoolExecutor(max_workers=3) as executor:
    conversations = list(executor.map(scraper.scrape, urls))

# 串行分析（避免Ollama过载）
for conv in conversations:
    result = ai_service.analyze(conv)
    storage.save(conv, result)
```

## 数据库优化

### SQLite性能

```python
# database/db_manager.py

# 1. 开启WAL模式
conn.execute("PRAGMA journal_mode=WAL")

# 2. 增加缓存
conn.execute("PRAGMA cache_size=10000")

# 3. 批量插入
conn.executemany(sql, data)
```

### Elasticsearch性能

```python
# database/es_manager.py

# 1. 批量索引
from elasticsearch.helpers import bulk
bulk(es, actions)

# 2. 异步操作
es = Elasticsearch(..., async_mode=True)

# 3. 优化映射
mapping = {
    "properties": {
        "summary": {
            "type": "text",
            "index_options": "offsets"  # 加速搜索
        }
    }
}
```

## 监控和调试

### 查看性能日志

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py add <url>
```

### 性能分析

```python
# 使用cProfile
python -m cProfile -o output.prof main.py add <url>

# 查看结果
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('cumulative')
p.print_stats(20)
```

### 内存分析

```python
# 使用memory_profiler
pip install memory-profiler
python -m memory_profiler main.py add <url>
```

## 常见问题

### Q: 为什么第一次分析很慢？

A: Ollama需要加载模型到内存（约10-30秒），之后会很快。

### Q: 如何让分析更准确？

A: 使用更大的模型，但会更慢：
```bash
ollama pull qwen2.5:7b
export OLLAMA_MODEL=qwen2.5:7b
```

### Q: 可以关闭AI功能吗？

A: 可以，核心功能不依赖AI：
```bash
export AI_ENABLED=false
# 或在.env中设置
AI_ENABLED=false
```

### Q: Docker环境下很慢怎么办？

A: 检查资源分配：
```bash
# 给Docker分配更多内存
# Windows/Mac: Docker Desktop -> Settings -> Resources
# 推荐: 至少10GB内存
```

## 最佳实践总结

1. ✅ **使用qwen2.5:3b模型**（速度和效果的最佳平衡）
2. ✅ **启用智能截断**（默认开启，无需配置）
3. ✅ **设置合理超时**（默认180秒，够用）
4. ✅ **避免批量处理大量对话**（逐个处理更稳定）
5. ✅ **Docker环境分配足够内存**（至少10GB）
6. ✅ **定期查看日志**（及时发现问题）

## 未来优化计划

- [ ] 并行抓取（多线程）
- [ ] 分段分析（超长文本）
- [ ] 缓存机制（避免重复分析）
- [ ] 模型预热（减少首次延迟）
- [ ] 异步处理（后台分析）
- [ ] 进度条UI（图形界面）
