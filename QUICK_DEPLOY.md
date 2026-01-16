# ChatCompass v1.2.5 快速部署指南

## 🚨 Playwright安装失败？选择合适的方案

---

## 方案A: 运行时安装（推荐 ⭐）

**适用于**: Playwright构建失败、网络不稳定

### 1️⃣ 修改Dockerfile

编辑 `Dockerfile` 第36行：

```dockerfile
# 注释掉构建时安装
# RUN playwright install chromium --with-deps || echo "⚠️  Playwright安装失败，将在运行时安装"

# 改为
RUN echo "跳过构建时安装Playwright浏览器"
```

### 2️⃣ 快速构建

```bash
# 停止旧服务
docker-compose down

# 快速构建（2-3分钟，不含浏览器）
docker-compose build --no-cache chatcompass_app

# 启动服务
docker-compose up -d
```

### 3️⃣ 运行时安装

```bash
# 等待容器启动
sleep 30

# 进入容器
docker exec -it chatcompass_app bash

# 安装浏览器（约2-5分钟）
playwright install chromium
playwright install-deps chromium

# 验证安装
ls -la /root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome
# 应该看到浏览器文件 ✅

# 退出
exit
```

### 4️⃣ 测试

```bash
docker exec -it chatcompass_app python main.py

> import https://chatgpt.com/share/696795a6-f574-8010-8aea-f1a88716b29f
# 应该成功抓取 ✅
```

---

## 方案B: 使用国内镜像（中国用户）

**适用于**: 在中国大陆，Playwright下载慢或超时

### 1️⃣ 进入容器

```bash
docker-compose up -d
docker exec -it chatcompass_app bash
```

### 2️⃣ 使用镜像源安装

```bash
# 设置镜像源
export PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright

# 增加超时时间（10分钟）
export PLAYWRIGHT_BROWSERS_DOWNLOAD_TIMEOUT=600000

# 安装浏览器
playwright install chromium
playwright install-deps chromium
```

### 3️⃣ 验证

```bash
ls -la /root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome
exit
```

---

## 方案C: 轻量级部署（无Playwright）

**适用于**: 只使用本地文件、不需要抓取网页

### 1️⃣ 使用轻量级Dockerfile

```bash
# 修改docker-compose.yml
services:
  chatcompass_app:
    build:
      context: .
      dockerfile: Dockerfile.lite  # 使用轻量版

# 或者直接构建
docker build -f Dockerfile.lite -t chatcompass:lite .
```

### 2️⃣ 启动

```bash
docker-compose up -d
```

**注意**: 此版本无法使用 `import <url>` 命令抓取网页

---

## 方案D: 完全手动安装（最可靠）

**适用于**: 所有自动安装都失败

### 1️⃣ 基础构建

```bash
# 修改Dockerfile，完全移除Playwright安装
# 第36行改为：
RUN echo "跳过Playwright"

# 构建基础镜像
docker-compose build chatcompass_app
docker-compose up -d
```

### 2️⃣ 手动下载浏览器

```bash
# 进入容器
docker exec -it chatcompass_app bash

# 创建目录
mkdir -p /root/.cache/ms-playwright

# 手动下载（选择合适的源）
# 方式1: 官方源
cd /tmp
wget https://playwright.azureedge.net/builds/chromium/1097/chromium-linux.zip

# 方式2: 国内镜像
wget https://registry.npmmirror.com/-/binary/playwright/chromium-1097/chromium-linux.zip

# 解压
apt-get update && apt-get install -y unzip
unzip chromium-linux.zip -d /root/.cache/ms-playwright/chromium-1097/

# 安装依赖
playwright install-deps chromium

# 验证
/root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome --version
```

---

## ⚡ 一键脚本（推荐方案A）

创建 `quick_deploy.sh`:

```bash
#!/bin/bash
echo "ChatCompass v1.2.5 快速部署"
echo "=============================="

# 1. 停止旧服务
echo "[1/5] 停止旧服务..."
docker-compose down

# 2. 修改Dockerfile（跳过构建时安装）
echo "[2/5] 优化Dockerfile..."
sed -i 's/RUN playwright install chromium/# RUN playwright install chromium/' Dockerfile

# 3. 快速构建
echo "[3/5] 构建镜像（约2-3分钟）..."
docker-compose build --no-cache chatcompass_app

# 4. 启动服务
echo "[4/5] 启动服务..."
docker-compose up -d

# 5. 等待并安装浏览器
echo "[5/5] 安装Playwright浏览器（约2-5分钟）..."
sleep 30
docker exec chatcompass_app playwright install chromium
docker exec chatcompass_app playwright install-deps chromium

echo ""
echo "=============================="
echo "✅ 部署完成！"
echo "=============================="
echo ""
echo "测试命令："
echo "  docker exec -it chatcompass_app python main.py"
```

使用：

```bash
chmod +x quick_deploy.sh
./quick_deploy.sh
```

---

## 🆘 仍然失败？

### 检查日志

```bash
# 查看构建日志
docker-compose build chatcompass_app 2>&1 | tee build.log

# 查看运行日志
docker logs chatcompass_app

# 查看Playwright日志
docker exec chatcompass_app playwright install chromium 2>&1
```

### 常见错误

| 错误 | 原因 | 解决方案 |
|-----|------|---------|
| `Download timeout` | 网络慢 | 使用方案B（国内镜像） |
| `No space left` | 磁盘满 | `docker system prune -a` |
| `Permission denied` | 权限问题 | `chmod 755` 相关目录 |
| `Host system missing dependencies` | 依赖缺失 | `playwright install-deps` |

### 获取帮助

1. 查看 `DOCKER_BUILD_GUIDE.md` - 完整部署指南
2. 查看 `PLAYWRIGHT_FIX.md` - Playwright问题详解
3. 提交Issue附上日志

---

## ✅ 验证部署

```bash
# 1. 检查容器状态
docker ps | grep chatcompass

# 2. 检查浏览器
docker exec chatcompass_app ls -la /root/.cache/ms-playwright/chromium-1097/chrome-linux/chrome

# 3. 完整测试
docker exec -it chatcompass_app python main.py
> import https://chatgpt.com/share/696795a6-f574-8010-8aea-f1a88716b29f
> list
> show <ID>
> exit

# 全部成功 = 部署完成 ✅
```

---

**推荐方案**: 方案A（运行时安装）- 快速、可靠、易排查

**最后更新**: 2026-01-15
