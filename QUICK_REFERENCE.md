# 🚀 ChatCompass 快速参考

> 开发者和AI助手必读的快速参考卡

---

## 📋 文档导航

| 角色 | 必读文档 | 用途 |
|------|---------|------|
| **新贡献者** | [CONTRIBUTING.md](CONTRIBUTING.md) | 完整开发指南 ⭐ |
| **日常开发** | [docs/BRANCH_MANAGEMENT.md](docs/BRANCH_MANAGEMENT.md) | 分支管理速查 ⭐ |
| **AI助手** | [.cursorrules](.cursorrules) | 快速规则 🤖 |
| **AI助手** | [.ai-assistant-rules.md](.ai-assistant-rules.md) | 详细规范 🤖 |

---

## 🌳 分支规则

### 分支命名

```bash
feature/add-gemini-support       # ✅ 新功能
bugfix/fix-encoding-error        # ✅ Bug修复
hotfix/v1.2.1-critical-fix       # ✅ 紧急修复
release/v1.3.0                   # ✅ 发布准备
```

### ❌ 禁止操作

```bash
git checkout main                # ❌ 不要在main上开发
git push origin main             # ❌ 不要直接推送到main
git push origin develop          # ❌ 不要直接推送到develop
```

---

## 📝 提交格式

### 标准格式

```
<type>(<scope>): <subject>
```

### 示例

```bash
git commit -m "feat(scraper): add Gemini support"
git commit -m "fix(search): resolve encoding error"
git commit -m "docs(readme): update installation guide"
git commit -m "test(db): add validation tests"
```

### Type类型

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug修复 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 重构 |
| `perf` | 性能 |
| `style` | 格式 |
| `chore` | 构建 |

---

## 🔒 安全规则（强制）

### SQL注入防护

```python
# ✅ 正确
cursor.execute(
    "SELECT * FROM conversations WHERE title = ?",
    (user_input,)
)

# ❌ 危险
cursor.execute(f"SELECT * FROM conversations WHERE title = '{user_input}'")
```

### 输入验证

```python
# ✅ 正确
if not title or len(title) > 500:
    raise ValueError("Invalid title")
```

### 敏感信息

```python
# ❌ 禁止
API_KEY = "sk-abc123..."

# ✅ 正确
API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## 🧪 测试要求

### 提交前必须执行

```bash
python -m pytest tests/ -v
```

### 要求

- ✅ 所有测试必须通过
- ✅ 新功能必须有测试
- ✅ 覆盖率 > 80%

---

## 🔄 标准工作流

### 功能开发

```bash
# 1. 更新develop
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/your-feature

# 3. 开发功能
# ... 编写代码 ...

# 4. 运行测试
python -m pytest tests/ -v

# 5. 提交代码
git add <files>
git commit -m "feat(scope): description"

# 6. 推送分支
git push origin feature/your-feature

# 7. 在GitHub上创建PR
# feature/your-feature → develop
```

### Bug修复

```bash
# 1. 从develop创建
git checkout develop
git pull origin develop
git checkout -b bugfix/fix-issue

# 2. 修复并测试
# ... 修复代码 ...
python -m pytest tests/ -v

# 3. 提交并推送
git commit -m "fix(scope): description"
git push origin bugfix/fix-issue

# 4. 创建PR
# bugfix/fix-issue → develop
```

---

## ✅ 提交前检查清单

### 必须检查

- [ ] 不在 main/develop 分支
- [ ] 分支名称符合规范
- [ ] 所有测试通过
- [ ] SQL使用参数化查询
- [ ] 没有敏感信息
- [ ] Commit message符合格式
- [ ] 文档已更新
- [ ] 没有临时文件

---

## 🚫 常见错误

### ❌ 错误提交消息

```bash
git commit -m "fix bug"              # 太简短
git commit -m "update code"          # 不清晰
git commit -m "Added feature."       # 格式错误
```

### ✅ 正确提交消息

```bash
git commit -m "fix(search): resolve Unicode encoding error"
git commit -m "feat(scraper): add Gemini conversation scraper"
git commit -m "docs(readme): update installation instructions"
```

---

## 🤖 AI助手特别注意

### 强制要求

1. ✅ 每次工作前检查分支
2. ✅ 使用参数化SQL查询
3. ✅ 提交前运行测试
4. ✅ 遵循commit规范
5. ✅ 不提交临时文件
6. ✅ 不提交敏感信息

### 检查命令

```bash
# 检查当前分支
git branch --show-current

# 运行测试
python -m pytest tests/ -v

# 检查状态
git status
```

---

## 📞 获取帮助

- 📖 完整指南: [CONTRIBUTING.md](CONTRIBUTING.md)
- 🌳 分支管理: [docs/BRANCH_MANAGEMENT.md](docs/BRANCH_MANAGEMENT.md)
- 🤖 AI规范: [.ai-assistant-rules.md](.ai-assistant-rules.md)
- 🐛 提Issue: [GitHub Issues](https://github.com/EasyWind001/ChatCompass/issues)

---

## 📊 项目状态

- **版本**: v1.2.0
- **测试**: 52 passed, 2 skipped
- **代码行数**: 8000+
- **文档**: 完善
- **许可证**: MIT

---

**快速开始，规范开发！** 🚀
