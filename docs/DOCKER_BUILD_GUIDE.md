# Docker构建和部署指南

## 🚀 快速开始

根据你的网络环境和需求，选择合适的构建方式：

---

## 方案1: 标准构建（推荐，包含Playwright）

适用于：
- ✅ 网络稳定的环境
- ✅ 需要抓取ChatGPT对话
- ✅ 完整功能

### 步骤

```bash
# 1. 停止旧服务
docker-compose down

# 2. 删除旧数据（可选）
docker volume rm chatcompass_es_data

# 3. 构建镜像（约5-10分钟）
docker-compose build --no-cache chatcompass_app

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker logs -f chatcompass_app

# 预期输出：
# [1/3] 等待Elasticsearch就绪...
#   ✅ Elasticsearch已就绪
# [2/3] 检查Playwright浏览器...
#   ✅ Chromium已安装
# 🎉 ChatCompass启动完成！
```

### 如果构建失败

**错误**: Playwright安装超时或失败

```bash
# 方案1A: 使用运行时安装
# 修改Dockerfile第36行，注释掉构建时安装：
# RUN playwright install chromium --with-deps || echo "⚠️  Playwright安装失败，将在运行时安装"
# 改为：
# RUN echo "跳过构建时安装，将在运行时安装"

# 然后重新构建
docker-compose build chatcompass_app
docker-compose up -d

# 等待容器启动后，手动安装
docker exec -it chatcompass_app playwright install chromium
docker exec -it chatcompass_app playwright install-deps chromium
```

---

## 方案2: 轻量级构建（网络受限）

适用于：
- ⚠️ 网络不稳定或受限
- ⚠️ 快速构建测试
- ⚠️ 只使用本地文件导入（不抓取网页）

### 步骤

```bash
# 1. 使用轻量级Dockerfile
docker-compose build --no-cache -f Dockerfile.lite chatcompass_app

# 或者修改docker-compose.yml:
# services:
#   chatcompass_app:
#     build:
#       context: .
#       dockerfile: Dockerfile.lite

# 2. 启动服务
docker-compose up -d

# 注意：此版本无法抓取ChatGPT对话，只能使用本地文件导入
```

---

## 方案3: 手动安装Playwright（推荐备用）

最可靠的方式：先构建基础镜像，然后运行时安装浏览器

### 步骤

```bash
# 1. 修改Dockerfile，注释掉Playwright安装
# 第36行改为：
# RUN echo "跳过Playwright构建时安装"

# 2. 构建基础镜像（快速）
docker-compose build chatcompass_app

# 3. 启动服务
docker-compose up -d

# 4. 等待服务启动（约30秒）
sleep 30

# 5. 检查容器状态
docker ps | grep chatcompass_app

# 6. 进入容器手动安装
docker exec -it chatcompass_app bash

# 7. 在容器内安装浏览器
playwright install chromium
playwright install-deps chromium

# 8. 验证安装
ls -la /root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome
# 应该看到浏览器可执行文件

# 9. 退出容器
exit

# 10. 测试导入
docker exec -it chatcompass_app python main.py
> import https://chatgpt.com/share/xxx
# 应该成功抓取 ✅
```

---

## 方案4: 使用预构建镜像（未来支持）

```bash
# TODO: 发布到Docker Hub后可用
docker pull chatcompass/chatcompass:v1.2.5
docker-compose up -d
```

---

## 🐛 常见问题排查

### 问题1: Playwright安装超时

**错误信息**:
```
Step 7/15 : RUN playwright install chromium
 ---> Running in abc123...
Downloading Chromium 1097 (106 MB)
ERROR: Download timeout
```

**解决方案**:

```bash
# 方案A: 使用国内镜像（如果在中国）
docker exec -it chatcompass_app bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright
playwright install chromium

# 方案B: 增加超时时间
docker exec -it chatcompass_app bash
export PLAYWRIGHT_BROWSERS_DOWNLOAD_TIMEOUT=600000
playwright install chromium

# 方案C: 手动下载浏览器
# 1. 从GitHub Release下载Chromium
# 2. 解压到 /root/.cache/ms-playwright/chromium-1097/
# 3. 重启容器
```

---

### 问题2: 系统依赖缺失

**错误信息**:
```
Error: Host system is missing dependencies
```

**解决方案**:

```bash
# 在容器内安装依赖
docker exec -it chatcompass_app bash
playwright install-deps chromium

# 或者修改Dockerfile，添加更多系统依赖（已在新版Dockerfile中）
```

---

### 问题3: 权限问题

**错误信息**:
```
Permission denied: /root/.cache/ms-playwright
```

**解决方案**:

```bash
docker exec -it chatcompass_app bash
mkdir -p /root/.cache/ms-playwright
chmod 755 /root/.cache/ms-playwright
playwright install chromium
```

---

### 问题4: 磁盘空间不足

**错误信息**:
```
No space left on device
```

**解决方案**:

```bash
# 检查磁盘空间
docker system df

# 清理未使用的镜像和容器
docker system prune -a

# 清理构建缓存
docker builder prune -a

# 重新构建
docker-compose build chatcompass_app
```

---

## 📊 镜像大小对比

| 版本 | 大小 | 构建时间 | 功能 |
|-----|------|---------|------|
| **标准版** | ~1.2GB | 5-10分钟 | 完整功能，包含Playwright |
| **轻量版** | ~500MB | 2-3分钟 | 基础功能，无Playwright |
| **运行时安装** | ~1.2GB | 2-3分钟构建 + 2-5分钟安装 | 完整功能，分两步安装 |

---

## ✅ 验证清单

部署完成后，逐项验证：

```bash
# 1. 检查容器状态
docker ps | grep chatcompass
# 应该显示 Up 状态

# 2. 检查Elasticsearch
docker exec -it chatcompass_app curl -s http://elasticsearch:9200/_cluster/health
# 应该返回 "status":"green" 或 "yellow"

# 3. 检查Playwright
docker exec -it chatcompass_app ls -la /root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome
# 应该显示浏览器文件

# 4. 测试CLI
docker exec -it chatcompass_app python main.py
> help
> list
> exit
# 应该正常运行

# 5. 测试导入（完整验证）
docker exec -it chatcompass_app python main.py
> import https://chatgpt.com/share/696795a6-f574-8010-8aea-f1a88716b29f
# 应该成功抓取并导入

# 6. 验证数据存储
docker exec -it chatcompass_app python main.py
> list
> show <ID>
# 应该显示完整对话内容
```

---

## 🔧 高级配置

### 使用代理

如果需要通过代理下载：

```bash
# 修改docker-compose.yml
services:
  chatcompass_app:
    build:
      context: .
      args:
        - HTTP_PROXY=http://proxy.example.com:8080
        - HTTPS_PROXY=http://proxy.example.com:8080
    environment:
      - HTTP_PROXY=http://proxy.example.com:8080
      - HTTPS_PROXY=http://proxy.example.com:8080
```

### 持久化Playwright缓存

```yaml
# docker-compose.yml
services:
  chatcompass_app:
    volumes:
      - playwright_cache:/root/.cache/ms-playwright

volumes:
  playwright_cache:
```

---

## 📚 相关文档

- `PLAYWRIGHT_FIX.md` - Playwright问题详细分析
- `Dockerfile` - 标准版Dockerfile
- `Dockerfile.lite` - 轻量版Dockerfile
- `docker_entrypoint.sh` - 启动脚本
- `docker-compose.yml` - Docker Compose配置

---

## 🆘 获取帮助

如果以上方案都无法解决，请提供以下信息：

```bash
# 1. Docker版本
docker --version
docker-compose --version

# 2. 系统信息
uname -a

# 3. 构建日志
docker-compose build chatcompass_app 2>&1 | tee build.log

# 4. 运行日志
docker logs chatcompass_app > runtime.log

# 5. 网络测试
curl -I https://playwright.azureedge.net/
```

然后在GitHub Issues中提交，附上上述信息。

---

**最后更新**: 2026-01-15  
**版本**: v1.2.5
