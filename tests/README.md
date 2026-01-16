# 🧪 ChatCompass 测试套件

## 📂 目录结构

```
tests/
├── README.md              # 本文档（测试指南）
├── conftest.py            # pytest配置和fixtures
├── pytest.ini             # pytest配置文件（应在项目根目录）
│
├── unit/                  # 单元测试目录
│   ├── test_delete_unit.py         # Delete功能单元测试
│   ├── test_all_fields.py          # 字段映射测试
│   ├── test_field_mapping.py       # 字段映射验证
│   ├── test_list_command.py        # List命令测试
│   ├── test_show_command.py        # Show命令测试
│   └── test_segment_quick.py       # 分段策略测试
│
├── e2e/                   # 端到端测试目录
│   ├── test_delete_e2e.py          # Delete功能E2E测试
│   ├── test_e2e_mock.py            # 模拟数据E2E测试
│   ├── test_e2e_real_data.py       # 真实数据E2E测试
│   └── test_basic_quick.py         # 快速E2E测试
│
├── integration/           # 集成测试目录
│   └── test_integration.py         # 系统集成测试
│
├── legacy/                # 历史测试（待清理）
│
├── test_ai_service.py     # AI服务测试
├── test_basic_functions.py # 基础功能测试
├── test_es_manager.py     # Elasticsearch管理器测试
├── test_segment_strategy.py # 分段策略测试
│
└── quick_test.py          # 快速测试脚本
```

---

## 🎯 测试分类说明

### 1. 单元测试（Unit Tests）
**位置**: `tests/unit/`  
**命名**: `test_<module>_unit.py` 或 `test_<feature>.py`

**特点**:
- 测试单个函数或类方法
- 隔离依赖（使用mock）
- 快速执行（<1秒）
- 不涉及外部系统（数据库、API）

**示例**:
```python
# tests/unit/test_delete_unit.py
def test_delete_by_id():
    """测试通过ID删除对话"""
    adapter = StorageAdapter('sqlite', db_path=':memory:')
    result = adapter.delete_conversation('1')
    assert result is True
```

**运行**:
```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定单元测试
pytest tests/unit/test_delete_unit.py -v
```

---

### 2. 端到端测试（E2E Tests）
**位置**: `tests/e2e/`  
**命名**: `test_<feature>_e2e.py` 或 `test_e2e_<scenario>.py`

**特点**:
- 测试完整用户流程
- 涉及真实依赖（数据库、文件系统）
- 较慢执行（数秒）
- 验证系统整体行为

**示例**:
```python
# tests/e2e/test_delete_e2e.py
def test_delete_workflow():
    """测试完整的删除工作流程"""
    # 1. 添加对话
    # 2. 验证存在
    # 3. 删除对话
    # 4. 验证已删除
    # 5. 检查统计信息
```

**运行**:
```bash
# 运行所有E2E测试
pytest tests/e2e/ -v

# 运行特定E2E测试
pytest tests/e2e/test_delete_e2e.py -v
```

---

### 3. 集成测试（Integration Tests）
**位置**: `tests/integration/`  
**命名**: `test_<system>_integration.py`

**特点**:
- 测试多个模块协作
- 涉及外部依赖（ES、Ollama）
- 中等执行时间
- 验证模块间接口

**示例**:
```python
# tests/integration/test_storage_integration.py
def test_sqlite_to_es_migration():
    """测试SQLite到Elasticsearch的迁移"""
    # 测试不同存储后端间的数据迁移
```

**运行**:
```bash
pytest tests/integration/ -v
```

---

## 🚀 运行测试

### 快速运行（推荐）
```bash
# 运行统一测试脚本
python run_all_tests.py

# 或使用pytest运行所有测试
pytest

# 运行并显示详细输出
pytest -v

# 运行并显示覆盖率
pytest --cov=. --cov-report=html
```

### 按目录运行
```bash
# 只运行单元测试（快速，推荐日常开发）
pytest tests/unit/ -v

# 运行特定单元测试文件
pytest tests/unit/test_delete_unit.py -v

# 运行E2E测试（需要真实环境）
python tests/e2e/test_delete_e2e.py

# 运行集成测试
pytest tests/integration/ -v
```

### 按标记运行
```bash
# 运行快速测试
pytest -m "not slow" -v

# 运行慢速测试
pytest -m slow -v

# 跳过需要真实数据的测试
pytest -m "not real_data" -v
```

### 按功能运行
```bash
# 运行所有delete相关测试
pytest -k delete -v

# 运行所有search相关测试
pytest -k search -v
```

---

## 📝 编写测试规范

### 1. 文件命名规范
- **单元测试**: `test_<module>_unit.py` 或 `test_<feature>.py`
- **E2E测试**: `test_<feature>_e2e.py` 或 `test_e2e_<scenario>.py`
- **集成测试**: `test_<system>_integration.py`

### 2. 测试函数命名
```python
# 好的命名（描述性强）
def test_delete_by_id_success():
    """测试通过有效ID成功删除对话"""

def test_delete_nonexistent_id_returns_false():
    """测试删除不存在的ID返回False"""

# 不好的命名（不清晰）
def test_delete():
    """测试删除"""

def test1():
    """测试"""
```

### 3. 测试结构（AAA模式）
```python
def test_example():
    """测试示例"""
    # Arrange（准备）
    adapter = StorageAdapter('sqlite', db_path=':memory:')
    conversation = {'title': 'Test', ...}
    conv_id = adapter.add_conversation(conversation)
    
    # Act（执行）
    result = adapter.delete_conversation(conv_id)
    
    # Assert（断言）
    assert result is True
    assert adapter.get_conversation(conv_id) is None
```

### 4. 使用Fixtures
```python
# conftest.py
@pytest.fixture
def temp_db():
    """提供临时数据库"""
    db_path = tempfile.mktemp('.db')
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

# 测试文件
def test_with_fixture(temp_db):
    """使用fixture的测试"""
    adapter = StorageAdapter('sqlite', db_path=temp_db)
    # 测试代码...
```

### 5. 测试标记
```python
import pytest

@pytest.mark.unit
def test_unit_example():
    """单元测试"""
    pass

@pytest.mark.e2e
def test_e2e_example():
    """E2E测试"""
    pass

@pytest.mark.slow
def test_slow_example():
    """慢速测试"""
    pass

@pytest.mark.skip(reason="待实现")
def test_todo():
    """未实现的测试"""
    pass
```

---

## 🎨 测试最佳实践

### 1. 测试覆盖原则
- ✅ **核心路径**: 必须100%覆盖
- ✅ **边界情况**: 空值、无效值、极端值
- ✅ **异常处理**: 错误分支必须测试
- ✅ **性能要求**: 关键操作需要性能测试

### 2. 独立性原则
- ✅ 每个测试独立运行
- ✅ 不依赖其他测试的执行顺序
- ✅ 使用临时数据库/文件
- ✅ 测试后清理资源

### 3. 可读性原则
```python
# 好的测试（清晰明确）
def test_delete_removes_conversation_from_database():
    """测试删除操作确实从数据库移除对话"""
    # Given: 数据库中有一个对话
    adapter = create_adapter()
    conv_id = add_test_conversation(adapter)
    
    # When: 删除该对话
    result = adapter.delete_conversation(conv_id)
    
    # Then: 对话不再存在
    assert result is True
    assert adapter.get_conversation(conv_id) is None
    assert adapter.get_statistics()['total_conversations'] == 0
```

### 4. 性能测试规范
```python
import time

def test_batch_delete_performance():
    """测试批量删除性能"""
    adapter = create_adapter()
    
    # 准备100个对话
    ids = [add_test_conversation(adapter) for _ in range(100)]
    
    # 测试批量删除
    start = time.time()
    for conv_id in ids:
        adapter.delete_conversation(conv_id)
    elapsed = time.time() - start
    
    # 性能要求：100个对话<1秒
    assert elapsed < 1.0, f"批量删除耗时{elapsed:.2f}s，超过1秒"
```

---

## 🔧 pytest配置

### pytest.ini（项目根目录）
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 标记定义
markers =
    unit: 单元测试
    e2e: 端到端测试
    integration: 集成测试
    slow: 慢速测试（>1秒）
    real_data: 需要真实数据的测试

# 输出配置
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings

# 覆盖率配置
[coverage:run]
source = .
omit = 
    tests/*
    venv/*
    .venv/*
```

---

## 📊 测试统计

### 当前测试覆盖（v1.2.6）
- **总测试数**: 66+
- **单元测试**: 66个测试（tests/unit/）
  * test_ai_clients.py: 19个测试
  * test_all_fields.py: 2个测试
  * test_database.py: 14个测试  
  * test_delete_unit.py: 13个测试 ✨新增
  * test_scrapers.py: 15个测试
  * test_show_command.py: 3个测试
- **E2E测试**: 4个测试文件（tests/e2e/）
- **集成测试**: 2个测试（tests/integration/）
- **通过率**: 98.5% (65 passed, 1 skipped)

### 最新新增（v1.2.6）
- ✅ test_delete_unit.py: 13个删除功能单元测试
- ✅ test_delete_e2e.py: 3个删除功能端到端测试
- ✅ test_all_fields.py: 转换为标准pytest格式
- ✅ test_show_command.py: 修复Windows文件锁问题

### 模块覆盖率
| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| main.py | 95% | ✅ |
| database/sqlite_manager.py | 92% | ✅ |
| database/storage_adapter.py | 90% | ✅ |
| database/es_manager.py | 85% | ✅ |
| scrapers/chatgpt_scraper.py | 80% | ✅ |
| ai/ai_service.py | 75% | 🟡 |

---

## 🐛 问题排查

### 测试失败常见原因

1. **数据库文件冲突**
   ```bash
   # 清理测试数据库
   rm -f test*.db
   pytest tests/unit/test_delete_unit.py -v
   ```

2. **Fixture未找到**
   ```python
   # 确保conftest.py在正确位置
   tests/conftest.py  # ✅ 正确
   tests/unit/conftest.py  # 也可以
   ```

3. **Import错误**
   ```bash
   # 确保项目根目录在PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

4. **临时文件清理失败**
   ```python
   # 使用上下文管理器
   with tempfile.NamedTemporaryFile(suffix='.db') as f:
       # 测试代码
       pass  # 自动清理
   ```

---

## 📚 参考资料

- [pytest官方文档](https://docs.pytest.org/)
- [测试覆盖率指南](https://coverage.readthedocs.io/)
- [项目测试指南](../TESTING_GUIDE.md)
- [贡献指南](../CONTRIBUTING.md)

---

## 🎯 下一步行动

### 待添加的测试
- [ ] AI服务的错误处理测试
- [ ] Elasticsearch的大数据量测试
- [ ] 并发操作的竞态条件测试
- [ ] 内存泄漏测试

### 待优化
- [ ] 减少测试执行时间（目标<10秒）
- [ ] 提高代码覆盖率到90%+
- [ ] 添加CI/CD自动测试
- [ ] 生成测试报告仪表板

---

**最后更新**: 2026-01-16  
**维护者**: ChatCompass Team  
**状态**: ✅ 活跃维护
