# ChatCompass 测试套件

本目录包含ChatCompass项目的所有测试代码。

## 📁 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # Pytest配置和共享fixture
├── README.md                # 本文件
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_database.py     # 数据库管理器测试
│   ├── test_scrapers.py     # 爬虫模块测试
│   └── test_ai_clients.py   # AI客户端测试
├── integration/             # 集成测试
│   ├── __init__.py
│   └── test_full_workflow.py # 完整工作流测试
└── legacy/                  # 旧测试文件归档
    └── test_*.py            # 历史测试文件
```

## 🚀 快速开始

### 运行所有测试

```bash
# Windows
run_tests.bat

# 或使用Python
python run_tests.py
```

### 运行特定类型的测试

```bash
# 仅运行单元测试
python run_tests.py unit

# 仅运行集成测试
python run_tests.py integration
```

### 运行特定测试文件

```bash
python run_tests.py file tests/unit/test_database.py
```

### 生成覆盖率报告

```bash
python run_tests.py coverage
```

## 📝 测试说明

### 单元测试 (Unit Tests)

测试单个模块或类的功能，不依赖外部服务。

- **test_database.py**: 测试数据库管理器的所有功能
  - CRUD操作
  - 搜索功能
  - 标签管理
  - 统计信息

- **test_scrapers.py**: 测试爬虫模块
  - URL识别
  - 数据结构
  - 工厂模式

- **test_ai_clients.py**: 测试AI客户端
  - Ollama客户端
  - OpenAI客户端
  - 数据解析

### 集成测试 (Integration Tests)

测试多个模块协同工作的场景。

- **test_full_workflow.py**: 测试完整业务流程
  - 爬取→存储→搜索
  - 数据更新流程
  - 多对话管理

## 🔧 Fixture说明

在`conftest.py`中定义了以下共享fixture:

- `temp_db`: 临时数据库，测试后自动清理
- `temp_dir`: 临时目录，测试后自动清理
- `sample_conversation_data`: 示例对话数据
- `sample_messages`: 示例消息列表

使用示例:

```python
def test_something(temp_db, sample_conversation_data):
    db = DatabaseManager(temp_db)
    # 使用temp_db和sample_conversation_data进行测试
```

## 📊 测试覆盖率

运行覆盖率测试后，查看报告:

```bash
# 生成HTML报告
python run_tests.py coverage

# 打开报告
start htmlcov/index.html  # Windows
```

## ✅ 测试最佳实践

1. **测试命名**: 使用`test_`前缀，描述性命名
   - ✅ `test_add_conversation_success`
   - ❌ `test1`

2. **每个测试只测一件事**: 保持测试简单专注

3. **使用fixture**: 避免重复的设置代码

4. **清理资源**: 使用fixture自动清理临时文件和数据库

5. **Mock外部依赖**: 单元测试中使用mock避免网络请求

## 🐛 调试测试

### 运行单个测试

```bash
pytest tests/unit/test_database.py::TestDatabaseManager::test_add_conversation -v
```

### 显示print输出

```bash
pytest tests/ -v -s
```

### 进入调试器

在测试代码中添加:
```python
import pdb; pdb.set_trace()
```

或使用pytest的调试选项:
```bash
pytest tests/ --pdb
```

## 📚 更多信息

- [Pytest官方文档](https://docs.pytest.org/)
- [项目README](../README.md)

## 🗂️ Legacy测试文件

旧的测试文件已移至`legacy/`目录，仅作参考，不会自动运行。如需运行:

```bash
python tests/legacy/test_fts3.py
```
