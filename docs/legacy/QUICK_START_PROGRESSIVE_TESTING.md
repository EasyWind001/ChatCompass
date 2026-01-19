# 🚀 渐进式测试 - 快速开始

## 📋 30秒快速开始

```bash
# 1. 进入项目目录
cd ChatCompass

# 2. 运行交互式测试
python run_tests_interactive.py --quick

# Windows用户也可以双击:
run_tests_interactive.bat
```

## 🎯 典型场景

### 场景1: 开发新功能后测试

```bash
# 只测试你修改的模块
python run_tests_interactive.py tests/unit/test_my_module.py
```

**工作流**:
1. 编写代码
2. 运行测试
3. 如果出错 → 查看详情 → 修复 → 重试 `[r]`
4. 通过后继续 `[c]`
5. 全部通过 → 提交代码✅

### 场景2: 修复bug后验证

```bash
# 测试相关功能模块
python run_tests_interactive.py tests/unit tests/integration
```

**工作流**:
1. 修复bug
2. 运行相关测试
3. 遇错暂停 → 检查是否引入新问题
4. 继续修复直到全部通过

### 场景3: 提交代码前完整检查

```bash
# 运行所有测试
python run_tests_interactive.py
```

**工作流**:
1. 代码准备提交
2. 运行完整测试套件
3. 逐个解决所有问题
4. 100%通过后提交

## 🎮 交互选项速查

遇到错误时的操作:

| 按键 | 操作 | 说明 |
|------|------|------|
| `c` | Continue | 继续下一个测试 |
| `r` | Retry | 重新运行当前测试 |
| `s` | Skip | 跳过剩余测试 |
| `v` | View | 查看错误历史摘要 |
| `e` | Export | 导出错误日志到文件 |
| `q` | Quit | 退出测试运行器 |

## 💡 最佳实践

### DO ✅

1. **小步快跑**
   ```bash
   # 优先测试核心模块
   python run_tests_interactive.py tests/unit --quick
   ```

2. **遇错即修**
   - 不要跳过错误
   - 立即查看详情
   - 修复后重试验证

3. **保存复杂错误**
   ```bash
   # 遇到复杂错误,按 [e] 导出
   # 日志保存在 logs/test_errors_*.log
   ```

### DON'T ❌

1. **不要一次跑完再改**
   ```bash
   # ❌ 不推荐
   python run_tests_interactive.py --no-stop
   
   # ✅ 推荐
   python run_tests_interactive.py  # 遇错即停
   ```

2. **不要盲目跳过**
   - 每个错误都有原因
   - 跳过只会累积问题

3. **不要忽略警告**
   - 应用层错误也要关注
   - 可能是潜在bug

## 📈 效率对比

### 传统模式
```
跑10分钟 → 发现15个错误 → 批量修复 → 再跑10分钟 → 发现遗漏
总耗时: ~40分钟
```

### 渐进式模式
```
跑测试 → 发现错误 → 立即修复 → 继续跑 → 逐个击破
总耗时: ~25分钟 (节省37.5%)
```

## 🔗 相关资源

- 📖 完整指南: [`docs/PROGRESSIVE_TESTING_GUIDE.md`](docs/PROGRESSIVE_TESTING_GUIDE.md)
- 📊 实施报告: [`docs/PROGRESSIVE_TESTING_SUMMARY.md`](docs/PROGRESSIVE_TESTING_SUMMARY.md)
- 🐛 错误处理: [`docs/ERROR_HANDLING_GUIDE.md`](docs/ERROR_HANDLING_GUIDE.md)

## 🆘 常见问题

### Q: 测试卡住不动?
**A**: 按 `Ctrl+C` 中断,使用 `--quick` 跳过GUI测试

### Q: 想要查看所有错误?
**A**: 按 `[v]` 查看摘要,按 `[e]` 导出详细日志

### Q: 如何只测试特定功能?
**A**: 指定测试文件路径
```bash
python run_tests_interactive.py tests/unit/test_db_manager.py::test_specific
```

### Q: 能否恢复传统模式?
**A**: 可以,使用 `--no-stop` 参数
```bash
python run_tests_interactive.py --no-stop
```

## 🎉 立即开始

```bash
# 方式1: Python脚本
python run_tests_interactive.py --quick

# 方式2: Windows批处理
run_tests_interactive.bat

# 方式3: 传统pytest
pytest tests/ -v
```

---

**记住**: 渐进式测试让你更快发现问题,更快解决问题,更有信心提交代码! 🚀
