# 贡献指南 (Contributing Guide)

欢迎为 ChatCompass 项目做出贡献！本文档将指导你如何参与项目开发。

## 📋 目录

- [开发环境设置](#开发环境设置)
- [分支管理规范](#分支管理规范)
- [代码提交规范](#代码提交规范)
- [Pull Request 流程](#pull-request-流程)
- [代码审查标准](#代码审查标准)
- [测试要求](#测试要求)
- [文档更新](#文档更新)

---

## 🛠️ 开发环境设置

### 1. Fork 并克隆仓库

```bash
# Fork仓库到你的账号
# 然后克隆你的fork
git clone https://github.com/YOUR_USERNAME/ChatCompass.git
cd ChatCompass

# 添加上游仓库
git remote add upstream https://github.com/EasyWind001/ChatCompass.git
```

### 2. 安装依赖

```bash
# Windows
install.bat

# Linux/Mac
./install.sh
```

### 3. 运行测试

```bash
python -m pytest tests/ -v
```

---

## 🌳 分支管理规范

### 分支模型

我们采用 **Git Flow** 简化版本的分支管理策略：

```
main (稳定发布分支)
  ↑
develop (开发主分支)
  ↑
feature/* (功能分支)
bugfix/* (修复分支)
hotfix/* (紧急修复分支)
release/* (发布准备分支)
```

### 分支类型说明

#### 1. **main** 分支
- **用途**: 稳定的生产代码，每个提交都是一个发布版本
- **保护**: 🔒 受保护，不允许直接推送
- **来源**: 只接受来自 `release/*` 和 `hotfix/*` 的合并
- **标签**: 每次合并都应打上版本标签（如 `v1.2.0`）

#### 2. **develop** 分支
- **用途**: 开发主分支，集成所有新功能
- **保护**: 🔒 受保护，不允许直接推送
- **来源**: 接受来自 `feature/*` 和 `bugfix/*` 的合并
- **状态**: 应保持可运行状态，所有测试必须通过

#### 3. **feature/** 分支（功能开发）
- **命名规则**: `feature/<issue-id>-<short-description>`
  - 示例: `feature/23-add-gemini-support`
  - 示例: `feature/search-enhancement`
- **基于**: `develop` 分支创建
- **合并到**: `develop` 分支
- **生命周期**: 功能开发完成后删除

**创建流程：**
```bash
# 1. 更新develop分支
git checkout develop
git pull upstream develop

# 2. 创建功能分支
git checkout -b feature/23-add-gemini-support

# 3. 开发并提交
git add .
git commit -m "feat: add Gemini scraper support"

# 4. 推送到你的fork
git push origin feature/23-add-gemini-support

# 5. 创建Pull Request到upstream的develop分支
```

#### 4. **bugfix/** 分支（Bug修复）
- **命名规则**: `bugfix/<issue-id>-<short-description>`
  - 示例: `bugfix/45-fix-encoding-error`
  - 示例: `bugfix/search-crash`
- **基于**: `develop` 分支创建
- **合并到**: `develop` 分支
- **生命周期**: 修复完成后删除

#### 5. **hotfix/** 分支（紧急修复）
- **命名规则**: `hotfix/<version>-<short-description>`
  - 示例: `hotfix/v1.2.1-critical-security-fix`
- **基于**: `main` 分支创建
- **合并到**: `main` 和 `develop` 分支（双向合并）
- **用途**: 修复生产环境的紧急问题
- **生命周期**: 修复完成后删除

**创建流程：**
```bash
# 1. 从main创建
git checkout main
git pull upstream main
git checkout -b hotfix/v1.2.1-critical-fix

# 2. 修复并提交
git add .
git commit -m "fix: critical security vulnerability"

# 3. 合并到main（需要PR审核）
# 4. 合并到develop（保持同步）
# 5. 打上新版本标签
git tag -a v1.2.1 -m "Hotfix: critical security fix"
```

#### 6. **release/** 分支（发布准备）
- **命名规则**: `release/v<version>`
  - 示例: `release/v1.3.0`
- **基于**: `develop` 分支创建
- **合并到**: `main` 和 `develop` 分支
- **用途**: 发布前的最后调整（版本号、文档、小bug修复）
- **生命周期**: 发布完成后删除

**创建流程：**
```bash
# 1. 从develop创建
git checkout develop
git pull upstream develop
git checkout -b release/v1.3.0

# 2. 更新版本号和文档
# 修改 setup.py, CHANGELOG.md 等

# 3. 测试并修复小问题
python -m pytest tests/ -v

# 4. 提交变更
git add .
git commit -m "chore: prepare release v1.3.0"

# 5. 合并到main并打标签
# 6. 合并回develop
```

---

## 📝 代码提交规范

### Commit Message 格式

我们采用 **Conventional Commits** 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(scraper): add Gemini support` |
| `fix` | Bug修复 | `fix(search): resolve encoding error` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式（不影响功能） | `style: format code with black` |
| `refactor` | 重构（不改变功能） | `refactor(db): simplify query logic` |
| `perf` | 性能优化 | `perf(search): improve FTS query speed` |
| `test` | 测试相关 | `test(scraper): add unit tests` |
| `chore` | 构建/工具变更 | `chore: update dependencies` |
| `ci` | CI配置变更 | `ci: add GitHub Actions workflow` |
| `revert` | 回滚提交 | `revert: revert commit abc123` |

### Scope（可选）

模块或组件名称：
- `scraper` - 爬虫模块
- `db` - 数据库模块
- `search` - 搜索功能
- `ai` - AI模块
- `cli` - 命令行界面
- `test` - 测试

### Subject（必需）

- 使用动词开头（add, fix, update, remove）
- 不超过50个字符
- 首字母小写
- 结尾不加句号

### 示例

```bash
# 好的提交消息
git commit -m "feat(scraper): add Gemini conversation scraper"
git commit -m "fix(search): resolve Unicode encoding error in snippet"
git commit -m "docs(contributing): add branch management guidelines"

# 多行提交消息
git commit -m "feat(search): add context highlighting feature

- Extract match context (before/after)
- Highlight keywords with markers
- Display message position and role
- Support multiple matches per conversation

Closes #42"
```

### ❌ 不好的示例

```bash
# 太简短
git commit -m "fix bug"

# 不清晰
git commit -m "update code"

# 格式错误
git commit -m "Added new feature for searching"  # 应该用小写
git commit -m "fix: Fixed the bug."  # 不要加句号
```

---

## 🔄 Pull Request 流程

### 1. 创建 PR 前的检查清单

- [ ] 代码基于最新的 `develop` 分支
- [ ] 所有测试通过（`pytest tests/ -v`）
- [ ] 代码风格符合规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交消息符合规范
- [ ] 没有合并冲突

### 2. 同步上游代码

```bash
# 在创建PR前，确保代码是最新的
git checkout develop
git fetch upstream
git merge upstream/develop
git checkout your-feature-branch
git rebase develop
```

### 3. 创建 Pull Request

#### PR 标题格式
```
<type>: <short description>
```

示例：
- `feat: Add Gemini conversation scraper`
- `fix: Resolve search encoding error`
- `docs: Update installation guide`

#### PR 描述模板

```markdown
## 🎯 变更类型
- [ ] 新功能 (feature)
- [ ] Bug修复 (bugfix)
- [ ] 文档更新 (docs)
- [ ] 性能优化 (perf)
- [ ] 代码重构 (refactor)

## 📝 变更描述
简要描述这个PR的目的和实现方式

## 🔗 相关 Issue
Closes #<issue-number>

## 📸 截图/演示
（如果有UI变更，添加截图或GIF）

## ✅ 测试
- [ ] 添加了单元测试
- [ ] 添加了集成测试
- [ ] 手动测试通过
- [ ] 所有测试通过

## 📋 检查清单
- [ ] 代码符合项目规范
- [ ] 更新了相关文档
- [ ] 更新了CHANGELOG.md
- [ ] 没有遗留的调试代码
- [ ] 没有合并冲突

## 💡 额外说明
（其他需要说明的内容）
```

### 4. PR 审查流程

1. **自动检查**
   - CI测试是否通过
   - 代码覆盖率是否达标

2. **人工审查**
   - 至少1位维护者审查
   - 代码质量和规范
   - 功能实现正确性
   - 测试完整性

3. **修改反馈**
   - 及时响应审查意见
   - 推送修改到同一分支
   - 不要force push（除非必要）

4. **合并策略**
   - **feature/bugfix → develop**: Squash and merge（合并为单个提交）
   - **release/hotfix → main**: Merge commit（保留历史）

---

## 🔍 代码审查标准

### 代码质量

- ✅ 代码可读性强，变量命名清晰
- ✅ 适当的注释（复杂逻辑必须注释）
- ✅ 没有重复代码（DRY原则）
- ✅ 函数职责单一，长度合理（<50行）
- ✅ 错误处理完善

### 安全性

- ✅ **SQL注入防护**: 必须使用参数化查询
- ✅ **输入验证**: 所有用户输入都需验证
- ✅ **敏感信息**: 不能包含密码、密钥等
- ✅ **依赖安全**: 使用最新的安全版本

### 性能

- ✅ 避免N+1查询
- ✅ 合理使用缓存
- ✅ 大数据集使用分页
- ✅ 避免不必要的计算

### 测试

- ✅ 核心功能必须有测试
- ✅ 边界条件测试
- ✅ 错误处理测试
- ✅ 测试覆盖率 > 80%

---

## 🧪 测试要求

### 测试类型

1. **单元测试** (`tests/unit/`)
   - 测试单个函数/方法
   - 使用mock隔离依赖
   - 快速执行

2. **集成测试** (`tests/integration/`)
   - 测试模块间交互
   - 使用测试数据库
   - 测试完整流程

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/unit/test_scraper.py -v

# 查看覆盖率
python -m pytest tests/ --cov=. --cov-report=html

# 快速测试（跳过慢速测试）
python -m pytest tests/ -m "not slow"
```

### 测试规范

```python
# 好的测试示例
def test_search_with_keyword_should_return_matches():
    """测试：搜索关键词应该返回匹配结果"""
    # Arrange
    db = DatabaseManager(':memory:')
    db.add_conversation(...)
    
    # Act
    results = db.search_conversations('Python')
    
    # Assert
    assert len(results) > 0
    assert 'Python' in results[0]['snippet']
```

### 新功能测试要求

- **必须**: 添加单元测试
- **必须**: 所有测试通过
- **建议**: 添加集成测试
- **建议**: 覆盖率 > 80%

---

## 📚 文档更新

### 需要更新文档的情况

1. **新功能**: 更新 README.md 和相关文档
2. **API变更**: 更新代码注释和文档
3. **配置变更**: 更新 .env.example 和配置说明
4. **依赖变更**: 更新 requirements.txt 和安装说明
5. **重要修复**: 更新 CHANGELOG.md

### CHANGELOG.md 更新规范

```markdown
## [v1.3.0] - 2026-01-15

### ✨ 新增功能
- feat(scraper): 新增Gemini对话导入支持 (#23)

### 🐛 Bug修复
- fix(search): 修复中文编码错误 (#45)

### 🔧 优化改进
- perf(db): 优化全文搜索性能 (#56)

### 📚 文档
- docs: 完善贡献指南 (#67)
```

---

## 🚀 快速开发工作流

### 日常开发流程

```bash
# 1. 同步最新代码
git checkout develop
git pull upstream develop

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发和测试
# ... 编写代码 ...
python -m pytest tests/ -v

# 4. 提交代码
git add .
git commit -m "feat(scope): your changes"

# 5. 推送到你的fork
git push origin feature/your-feature-name

# 6. 在GitHub上创建Pull Request
# 从 your-fork/feature/your-feature-name 到 upstream/develop

# 7. 等待审查和合并
# 8. 合并后删除分支
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### 处理冲突

```bash
# 如果develop分支有更新，需要rebase
git checkout feature/your-feature
git fetch upstream
git rebase upstream/develop

# 如果有冲突
# 1. 解决冲突
# 2. 标记已解决
git add <conflicted-files>
git rebase --continue

# 3. 强制推送（因为改变了历史）
git push origin feature/your-feature --force-with-lease
```

---

## 🏆 最佳实践

### DO ✅

- ✅ 小而频繁的提交
- ✅ 清晰的提交消息
- ✅ 功能开发前先创建Issue讨论
- ✅ 及时响应PR审查意见
- ✅ 保持分支更新
- ✅ 编写测试
- ✅ 更新文档

### DON'T ❌

- ❌ 直接向main或develop推送
- ❌ 提交大量未经测试的代码
- ❌ 忽略测试失败
- ❌ 提交临时文件或生成文件
- ❌ 使用force push（除非必要）
- ❌ 提交包含密码或密钥的代码
- ❌ 忽略代码审查意见

---

## 🤖 智能体协作指南

### 对于AI开发助手

如果你是AI助手（如GitHub Copilot、Cursor、Windsurf等），在协助开发时请遵循：

1. **分支操作**
   - 始终在正确的分支上工作
   - 功能开发在 `feature/*` 分支
   - Bug修复在 `bugfix/*` 分支
   - 不要直接操作 main 或 develop

2. **代码提交**
   - 使用规范的commit message格式
   - 每个提交只做一件事
   - 提交前运行测试

3. **测试要求**
   - 为新功能编写测试
   - 确保所有测试通过
   - 不提交失败的测试

4. **代码质量**
   - 遵循项目代码规范
   - 使用参数化查询防止SQL注入
   - 适当添加注释
   - 保持代码简洁

5. **文档同步**
   - 更新相关文档
   - 更新CHANGELOG.md
   - 提供清晰的PR描述

---

## 📞 获取帮助

- 📖 查看 [README.md](README.md) 了解项目概述
- 🐛 提交 Issue 报告问题或提出建议
- 💬 在 Discussion 中讨论想法
- 📧 联系维护者

---

## 📄 许可证

通过贡献代码，你同意你的代码将在 [MIT License](LICENSE) 下发布。

---

**感谢你的贡献！🎉**
