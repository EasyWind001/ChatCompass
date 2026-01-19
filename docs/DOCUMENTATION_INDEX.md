# 📚 ChatCompass v1.2.6 文档索引

**版本**: v1.2.6  
**最后更新**: 2026-01-17

---

## 📖 核心文档（必读）

### 用户文档
1. **README.md** - 项目介绍和快速开始（英文）
2. **README_CN.md** - 项目介绍和快速开始（中文）⭐推荐
3. **CHANGELOG.md** - 完整版本变更记录
4. **QUICK_REFERENCE.md** - 快速参考指南

### 开发文档
1. **CONTRIBUTING.md** - 贡献指南
2. **TESTING_GUIDE.md** - 测试指南
3. **tests/README.md** - 测试详细说明

### 部署文档
1. **QUICK_DEPLOY.md** - 快速部署指南
2. **DOCKER_BUILD_GUIDE.md** - Docker构建指南
3. **docker-compose.yml** - Docker编排配置

---

## 🔧 技术文档

### 数据库和存储
- `docs/FALLBACK_STRATEGY.md` - 存储后端降级策略
- `docs/LARGE_TEXT_HANDLING.md` - 大文本处理方案
- `docs/SEGMENT_SUMMARY_STRATEGY.md` - 分段摘要策略

### 搜索功能
- `docs/SEARCH_CONTEXT_FEATURE.md` - 搜索上下文功能
- `docs/search_implementation.md` - 搜索实现详解
- `docs/SEARCH_ENHANCEMENT_SUMMARY.md` - 搜索增强总结

### 性能和优化
- `docs/PERFORMANCE_TIPS.md` - 性能优化建议

### 项目管理
- `docs/PROJECT_SUMMARY.md` - 项目架构和总结
- `docs/BRANCH_MANAGEMENT.md` - 分支管理策略

---

## 🐳 Docker文档

1. **DOCKER_BUILD_GUIDE.md** - Docker构建完整指南
2. **docs/DOCKER_GUIDE.md** - Docker使用指南
3. **docs/DOCKER_QUICKSTART.md** - Docker快速启动
4. **docker-compose.yml** - 编排配置文件
5. **Dockerfile** - 完整镜像构建
6. **Dockerfile.lite** - 轻量级镜像（SQLite only）
7. **docker_entrypoint.sh** - 容器入口脚本

---

## 🧪 测试文档

### 测试指南
1. **TESTING_GUIDE.md** - 测试使用指南
2. **tests/README.md** - 测试详细说明
3. **TESTING_SUMMARY_v1.2.6.md** - v1.2.6测试总结
4. **TEST_READY_REPORT.md** - 测试就绪报告
5. **TEST_RESULTS.md** - 测试结果详情

### 测试脚本
- `run_all_tests.py` - 统一测试运行脚本
- `run_tests.py` - 基础测试脚本
- `pytest.ini` - pytest配置

---

## 📦 发布文档

### v1.2.6版本（当前版本）
- **RELEASE_READY_v1.2.6.md** - v1.2.6发布就绪报告
- **PUSH_GUIDE.md** - GitHub推送指南
- **PRE_PUSH_CHECKLIST.md** - 推送前检查清单
- **COMMIT_MESSAGE.txt** - 提交信息模板

### v1.2.2版本
- `docs/V1.2.2_RELEASE_NOTES.md` - v1.2.2发布说明
- `docs/V1.2.2_PLAN.md` - v1.2.2开发计划
- `docs/V1.2.2_PHASE1_COMPLETE.md` - Phase 1完成报告
- `docs/V1.2.2_PHASE2_COMPLETE.md` - Phase 2完成报告
- `docs/V1.2.2_PHASE3_COMPLETE.md` - Phase 3完成报告
- `docs/V1.2.2_PHASE4_COMPLETE.md` - Phase 4完成报告
- `docs/V1.2.2_DOCUMENTATION_COMPLETE.md` - 文档完成报告
- `V1.2.2_KICKOFF.md` - v1.2.2开发启动

### v1.2.4版本
- `FINAL_SUMMARY_v1.2.4.md` - v1.2.4最终总结
- `RELEASE_CHECKLIST_v1.2.4.md` - v1.2.4发布检查清单
- `FINAL_BUGFIX_REPORT.md` - Bug修复报告
- `FINAL_E2E_VERIFICATION.md` - E2E验证报告

### 其他发布文档
- `GITHUB_READY.md` - GitHub就绪报告
- `GITHUB_RELEASE_v1.2.2.md` - GitHub v1.2.2发布
- `PROJECT_READY_SUMMARY.md` - 项目就绪总结

---

## 🗂️ 归档文档（历史参考）

位置: `docs/archive/`

### 功能开发总结
- `DELETE_FEATURE_SUMMARY.md` - Delete功能开发总结
- `SHOW_FEATURE_SUMMARY.md` - Show功能总结
- `FEATURE_SHOW.md` / `NEW_FEATURE_SHOW.md` - Show功能开发

### Bug修复记录
- `BUGFIX_SUMMARY.md` - Bug修复总结
- `CRITICAL_FIX_v1.2.5.md` - v1.2.5关键修复
- `FIELD_MAPPING_FIX.md` - 字段映射修复
- `RAW_CONTENT_FIX.md` - Raw content修复
- `SOURCE_URL_FIX.md` - Source URL修复
- `PLAYWRIGHT_FIX.md` - Playwright修复

### 性能优化
- `LARGE_TEXT_OPTIMIZATION_SUMMARY.md` - 大文本优化总结
- `SEGMENT_STRATEGY_SUMMARY.md` - 分段策略总结
- `TIMEOUT_HANDLING_SUMMARY.md` - 超时处理总结
- `STRATEGY_COMPARISON.md` - 策略对比

### 测试报告
- `TEST_REPORT.md` - 测试报告
- `TEST_RESULTS.md` - 测试结果
- `TESTING_COMPLETE.md` - 测试完成报告
- `FINAL_TEST_SUCCESS.md` - 最终测试成功

### 快速指南（历史版本）
- `QUICK_START_SEGMENT.md` - 分段功能快速开始
- `QUICK_TIMEOUT_GUIDE.md` - 超时处理快速指南
- `QUICKSTART.md` - 旧版快速开始

### 其他历史文档
- `START_HERE.md` - 旧版入门指南
- `FINAL_REPORT.md` - 最终报告
- `BUGFIX_REPORT.md` - Bug修复报告
- `ISSUE_RESOLVED.md` - 问题解决
- `RUNNING_SUCCESS.md` - 运行成功
- `VERIFIED_WORKING.md` - 验证工作
- `使用说明.txt` - 中文使用说明（旧版）
- `搜索功能增强说明.txt` - 搜索增强说明（旧版）

---

## 🎯 按场景查找文档

### 我想快速开始使用
1. 阅读 `README_CN.md`
2. 按照 `QUICK_DEPLOY.md` 部署
3. 参考 `QUICK_REFERENCE.md` 使用

### 我想开发和贡献代码
1. 阅读 `CONTRIBUTING.md`
2. 查看 `docs/PROJECT_SUMMARY.md` 了解架构
3. 阅读 `TESTING_GUIDE.md` 学习测试

### 我想使用Docker部署
1. 阅读 `DOCKER_BUILD_GUIDE.md`
2. 查看 `docs/DOCKER_QUICKSTART.md`
3. 使用 `docker-compose.yml` 启动

### 我想了解测试
1. 阅读 `TESTING_GUIDE.md`
2. 查看 `tests/README.md`
3. 查看 `TESTING_SUMMARY_v1.2.6.md`

### 我想了解版本历史
1. 查看 `CHANGELOG.md`（完整记录）
2. 阅读 `docs/V1.2.2_RELEASE_NOTES.md`（v1.2.2详情）
3. 查看 `RELEASE_READY_v1.2.6.md`（当前版本）

### 我遇到了问题
1. 查看 `README_CN.md` 的故障排除章节
2. 搜索 `docs/archive/` 中的修复记录
3. 查看 `CHANGELOG.md` 的已知问题

---

## 📝 文档维护

### 活跃文档（经常更新）
- README.md / README_CN.md
- CHANGELOG.md
- tests/README.md
- TESTING_GUIDE.md

### 版本文档（随版本更新）
- RELEASE_READY_*.md
- TESTING_SUMMARY_*.md
- setup.py (version字段)

### 稳定文档（很少变动）
- CONTRIBUTING.md
- LICENSE
- docs/PROJECT_SUMMARY.md
- docs/BRANCH_MANAGEMENT.md

### 归档文档（只读）
- docs/archive/ 下的所有文档
- 旧版本的发布文档

---

## 🔍 快速搜索

| 关键词 | 相关文档 |
|--------|----------|
| 快速开始 | README_CN.md, QUICK_DEPLOY.md |
| 测试 | TESTING_GUIDE.md, tests/README.md |
| Docker | DOCKER_BUILD_GUIDE.md, docs/DOCKER_GUIDE.md |
| 搜索 | docs/SEARCH_CONTEXT_FEATURE.md |
| 性能 | docs/PERFORMANCE_TIPS.md |
| 大文本 | docs/LARGE_TEXT_HANDLING.md |
| Delete功能 | docs/archive/DELETE_FEATURE_SUMMARY.md |
| 贡献 | CONTRIBUTING.md |
| 版本历史 | CHANGELOG.md |
| 发布 | RELEASE_READY_v1.2.6.md |

---

## 📊 文档统计

### 总文档数
- **核心文档**: 11个
- **技术文档**: 9个
- **Docker文档**: 7个
- **测试文档**: 8个
- **发布文档**: 16个
- **归档文档**: 30+个

### 文档规模
- **总行数**: 15,000+ 行
- **总大小**: 800+ KB
- **最大文档**: CHANGELOG.md (41.5 KB)

---

## 🆕 最新更新（v1.2.6）

1. ✅ 添加Delete功能文档
2. ✅ 更新测试文档（66个测试）
3. ✅ 创建v1.2.6发布文档
4. ✅ 更新README版本号和功能说明
5. ✅ 创建文档索引（本文档）

---

## 📮 联系和反馈

- **GitHub Issues**: 报告bug或建议
- **GitHub Discussions**: 技术讨论
- **CONTRIBUTING.md**: 贡献指南

---

**文档版本**: v1.2.6  
**维护者**: ChatCompass Team  
**最后更新**: 2026-01-17
