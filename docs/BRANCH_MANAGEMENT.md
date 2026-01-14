# Git 分支管理规范

> 快速参考指南 - 适用于所有开发者和AI助手

## 📊 分支结构一览

```
main (生产环境)
  ├── v1.0.0
  ├── v1.1.0
  └── v1.2.0 ← 当前版本

develop (开发主线)
  ├── feature/search-enhancement
  ├── feature/gemini-support
  ├── bugfix/encoding-error
  └── release/v1.3.0

hotfix/v1.2.1-critical-fix (紧急修复)
```

---

## 🎯 分支类型速查表

| 分支 | 命名规则 | 基于 | 合并到 | 用途 | 生命周期 |
|------|----------|------|--------|------|----------|
| **main** | `main` | - | - | 生产代码 | 永久 |
| **develop** | `develop` | `main` | - | 开发集成 | 永久 |
| **feature** | `feature/<name>` | `develop` | `develop` | 新功能 | 临时 |
| **bugfix** | `bugfix/<name>` | `develop` | `develop` | Bug修复 | 临时 |
| **hotfix** | `hotfix/v<version>-<name>` | `main` | `main` + `develop` | 紧急修复 | 临时 |
| **release** | `release/v<version>` | `develop` | `main` + `develop` | 发布准备 | 临时 |

---

## 🚀 常用操作流程

### 1️⃣ 开发新功能

```bash
# 步骤1: 更新develop分支
git checkout develop
git pull origin develop

# 步骤2: 创建功能分支
git checkout -b feature/add-gemini-support

# 步骤3: 开发功能
# ... 编写代码 ...

# 步骤4: 提交代码
git add .
git commit -m "feat(scraper): add Gemini scraper support"

# 步骤5: 推送分支
git push origin feature/add-gemini-support

# 步骤6: 创建Pull Request (在GitHub网页上操作)
# 从 feature/add-gemini-support → develop

# 步骤7: 审查通过后，删除本地分支
git checkout develop
git pull origin develop
git branch -d feature/add-gemini-support
```

### 2️⃣ 修复Bug

```bash
# 步骤1: 从develop创建修复分支
git checkout develop
git pull origin develop
git checkout -b bugfix/fix-encoding-error

# 步骤2: 修复并测试
# ... 修复代码 ...
python -m pytest tests/ -v

# 步骤3: 提交
git add .
git commit -m "fix(search): resolve Unicode encoding error"

# 步骤4: 推送并创建PR
git push origin bugfix/fix-encoding-error
# PR: bugfix/fix-encoding-error → develop
```

### 3️⃣ 紧急修复（生产环境）

```bash
# 步骤1: 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.1-critical-fix

# 步骤2: 修复问题
# ... 修复代码 ...
python -m pytest tests/ -v

# 步骤3: 提交
git add .
git commit -m "fix: critical security vulnerability"

# 步骤4: 合并到main（创建PR）
# PR: hotfix/v1.2.1-critical-fix → main

# 步骤5: 打标签
git checkout main
git pull origin main
git tag -a v1.2.1 -m "Hotfix: critical security fix"
git push origin v1.2.1

# 步骤6: 合并到develop（保持同步）
# PR: hotfix/v1.2.1-critical-fix → develop
```

### 4️⃣ 发布新版本

```bash
# 步骤1: 从develop创建release分支
git checkout develop
git pull origin develop
git checkout -b release/v1.3.0

# 步骤2: 准备发布（更新版本号、文档）
# 修改 setup.py, CHANGELOG.md 等
git add .
git commit -m "chore: prepare release v1.3.0"

# 步骤3: 测试
python -m pytest tests/ -v

# 步骤4: 合并到main
# PR: release/v1.3.0 → main

# 步骤5: 打标签
git checkout main
git pull origin main
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# 步骤6: 合并回develop
# PR: release/v1.3.0 → develop

# 步骤7: 删除release分支
git branch -d release/v1.3.0
```

---

## 📝 Commit Message 规范

### 格式

```
<type>(<scope>): <subject>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(scraper): add Gemini support` |
| `fix` | Bug修复 | `fix(search): resolve encoding error` |
| `docs` | 文档 | `docs(readme): update installation guide` |
| `style` | 格式 | `style: format code with black` |
| `refactor` | 重构 | `refactor(db): simplify query logic` |
| `perf` | 性能 | `perf(search): improve FTS performance` |
| `test` | 测试 | `test(scraper): add unit tests` |
| `chore` | 构建 | `chore: update dependencies` |

### 示例

```bash
# ✅ 好的提交消息
git commit -m "feat(scraper): add Gemini conversation scraper"
git commit -m "fix(search): resolve Unicode encoding error"
git commit -m "docs(contributing): add branch guidelines"

# ❌ 不好的提交消息
git commit -m "fix bug"           # 太简短
git commit -m "update code"       # 不清晰
git commit -m "Added feature."    # 格式错误（大写、句号）
```

---

## 🔄 处理冲突

### 同步develop分支

```bash
# 方法1: Rebase（推荐）
git checkout feature/your-feature
git fetch origin
git rebase origin/develop

# 如果有冲突
# 1. 手动解决冲突
# 2. 标记已解决
git add <resolved-files>
git rebase --continue

# 3. 推送（需要force）
git push origin feature/your-feature --force-with-lease
```

```bash
# 方法2: Merge
git checkout feature/your-feature
git fetch origin
git merge origin/develop

# 解决冲突后
git add <resolved-files>
git commit -m "merge: resolve conflicts with develop"
git push origin feature/your-feature
```

---

## 🤖 AI助手开发规范

如果你是AI开发助手，请严格遵循以下规范：

### ✅ 必须遵守

1. **分支检查**
   ```bash
   # 开始工作前，检查当前分支
   git branch --show-current
   
   # 确保在正确的分支上
   # 新功能 → feature/*
   # Bug修复 → bugfix/*
   # 绝不在 main 或 develop 上直接工作
   ```

2. **提交规范**
   - 使用标准的commit message格式
   - 每次提交只做一件事
   - 提交前必须运行测试

3. **测试要求**
   ```bash
   # 提交前必须执行
   python -m pytest tests/ -v
   
   # 所有测试必须通过
   # 新功能必须添加测试
   ```

4. **代码安全**
   - 使用参数化查询（防止SQL注入）
   - 验证所有用户输入
   - 不提交敏感信息

5. **文档同步**
   - 更新相关的README/文档
   - 更新CHANGELOG.md
   - 提供清晰的PR描述

### ❌ 禁止操作

- ❌ 直接推送到 main 或 develop
- ❌ 跳过测试
- ❌ 忽略测试失败
- ❌ 提交临时文件（*.db, __pycache__等）
- ❌ 使用字符串拼接构造SQL
- ❌ 提交未经审查的大量代码

### 🔍 检查清单

每次提交前，AI助手应自动检查：

```bash
# 1. 分支检查
[ ] 在正确的feature/bugfix分支上
[ ] 分支名称符合规范

# 2. 代码质量
[ ] 代码符合Python规范（PEP 8）
[ ] 添加了必要的注释
[ ] 没有调试代码（print等）

# 3. 安全检查
[ ] SQL使用参数化查询
[ ] 用户输入已验证
[ ] 没有硬编码的密码/密钥

# 4. 测试
[ ] 添加了单元测试
[ ] 所有测试通过
[ ] 测试覆盖主要功能

# 5. 文档
[ ] 更新了相关文档
[ ] 提交消息清晰规范
[ ] 准备好PR描述
```

---

## 📌 快速命令参考

```bash
# 查看所有分支
git branch -a

# 查看当前分支
git branch --show-current

# 切换分支
git checkout <branch-name>

# 创建并切换到新分支
git checkout -b feature/new-feature

# 查看修改状态
git status

# 查看提交历史
git log --oneline --graph --all

# 同步远程分支
git fetch origin
git pull origin develop

# 删除本地分支
git branch -d feature/old-feature

# 删除远程分支
git push origin --delete feature/old-feature

# 查看远程仓库
git remote -v
```

---

## 🎯 分支保护规则

### main 分支

- 🔒 **受保护**
- ✅ 需要PR审查
- ✅ 需要测试通过
- ✅ 需要至少1位维护者批准
- ❌ 禁止直接推送
- ❌ 禁止force push

### develop 分支

- 🔒 **受保护**
- ✅ 需要PR审查
- ✅ 需要测试通过
- ❌ 禁止直接推送
- ⚠️ 允许维护者force push（谨慎使用）

---

## 🔄 完整工作流示例

### 场景：添加Gemini平台支持

```bash
# 1. 创建Issue（在GitHub上）
# Issue #89: 添加Gemini平台对话导入支持

# 2. 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/89-gemini-support

# 3. 开发功能
# 创建 scrapers/gemini_scraper.py
# 修改 scrapers/scraper_factory.py
# 添加测试 tests/unit/test_gemini_scraper.py

# 4. 运行测试
python -m pytest tests/ -v

# 5. 提交代码
git add scrapers/gemini_scraper.py
git commit -m "feat(scraper): add Gemini scraper class"

git add scrapers/scraper_factory.py
git commit -m "feat(scraper): register Gemini in factory"

git add tests/unit/test_gemini_scraper.py
git commit -m "test(scraper): add Gemini scraper tests"

git add docs/
git commit -m "docs: update README with Gemini support"

# 6. 推送分支
git push origin feature/89-gemini-support

# 7. 创建Pull Request（在GitHub上）
# 标题: feat: Add Gemini platform support
# 描述: 使用PR模板填写
# 关联Issue: Closes #89

# 8. 等待审查，处理反馈意见

# 9. 审查通过，合并后清理
git checkout develop
git pull origin develop
git branch -d feature/89-gemini-support
git push origin --delete feature/89-gemini-support
```

---

## 📞 帮助和资源

- 📖 完整指南: [CONTRIBUTING.md](../CONTRIBUTING.md)
- 🐛 报告问题: [GitHub Issues](https://github.com/EasyWind001/ChatCompass/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/EasyWind001/ChatCompass/discussions)

---

**记住：清晰的分支管理 = 高效的团队协作！** 🚀
