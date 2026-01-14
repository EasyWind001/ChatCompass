# Legacy测试文件

本目录包含项目早期的测试文件，已被新的测试套件替代。

## 说明

这些文件仅作为历史参考保留，不会在运行`pytest`时自动执行。

如果需要运行这些测试，请直接使用Python执行:

```bash
python tests/legacy/test_fts3.py
```

## 新测试套件

请使用位于`tests/unit/`和`tests/integration/`的新测试套件，它们提供:

- ✅ 更好的组织结构
- ✅ 完整的测试覆盖
- ✅ 使用pytest框架
- ✅ 共享fixture和配置
- ✅ 自动化测试运行

详见: [tests/README.md](../README.md)
