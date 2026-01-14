# 🐳 ChatCompass Docker 部署指南

> 一键启动完整环境，无需手动配置

---

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [服务说明](#服务说明)
- [常用命令](#常用命令)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [性能优化](#性能优化)

---

## 💻 系统要求

### 最低配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **硬盘**: 20GB可用空间
- **系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+

### 推荐配置
- **CPU**: 8核心
- **内存**: 16GB RAM
- **硬盘**: 50GB SSD
- **GPU**: 可选（加速AI推理）

### 软件依赖
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

---

## 🚀 快速开始

### 1. 安装Docker

#### Windows/Mac
1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 安装并启动Docker Desktop
3. 验证安装：
   ```bash
   docker --version
   docker-compose --version
   ```

#### Linux
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 一键启动

#### Windows
```bash
# 双击运行
docker-start.bat

# 或在命令行中
.\docker-start.bat
```

#### Linux/Mac
```bash
# 添加执行权限
chmod +x docker-start.sh

# 运行
./docker-start.sh
```

### 3. 等待服务就绪

首次启动需要：
- ⏬ 下载镜像（~2GB）
- ⏬ 下载Ollama模型（~3GB）
- ⚙️ 初始化Elasticsearch索引

**总耗时**: 10-20分钟（取决于网速）

### 4. 验证服务

```bash
# 查看服务状态
docker-compose ps

# 应该看到3个服务都是running状态
# - chatcompass-elasticsearch
# - chatcompass-ollama
# - chatcompass-app
```

---

## 🔧 服务说明

### 1. Elasticsearch（数据存储）
- **端口**: 9200, 9300
- **内存**: 1-2GB
- **数据持久化**: `es_data` volume
- **健康检查**: `http://localhost:9200/_cluster/health`

**访问测试**:
```bash
curl http://localhost:9200

# 应该返回ES版本信息
```

### 2. Ollama（本地AI）
- **端口**: 11434
- **模型**: qwen2.5:3b (~3GB)
- **数据持久化**: `ollama_data` volume
- **健康检查**: `ollama list`

**访问测试**:
```bash
curl http://localhost:11434/api/version

# 查看已下载的模型
docker exec chatcompass-ollama ollama list
```

### 3. ChatCompass（应用）
- **端口**: 8000（预留）
- **数据持久化**: `./data` 目录
- **日志**: `./logs` 目录

---

## 📝 常用命令

### 启动和停止

```bash
# 启动所有服务（后台）
docker-compose up -d

# 启动并查看日志
docker-compose up

# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会删除所有数据）
docker-compose down -v
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs chatcompass
docker-compose logs elasticsearch
docker-compose logs ollama

# 实时跟踪日志
docker-compose logs -f chatcompass

# 查看最近100行
docker-compose logs --tail=100 chatcompass
```

### 进入容器

```bash
# 进入ChatCompass容器
docker exec -it chatcompass-app bash

# 运行CLI命令
docker exec -it chatcompass-app python main.py

# 运行特定命令
docker exec -it chatcompass-app python main.py stats
docker exec -it chatcompass-app python main.py search "关键词"
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart chatcompass

# 重新构建并重启
docker-compose up -d --build
```

---

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑配置：
```bash
# 存储类型（Docker环境默认使用elasticsearch）
STORAGE_TYPE=elasticsearch

# Elasticsearch配置
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# Ollama配置
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:3b

# AI功能
AI_MODE=local
```

### 资源限制调整

编辑 `docker-compose.yml`：

```yaml
services:
  elasticsearch:
    environment:
      # 调整ES内存（默认1GB）
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    
  ollama:
    # 添加GPU支持
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 更换Ollama模型

编辑 `docker-compose.yml` 中的 `OLLAMA_MODEL`:

```yaml
environment:
  - OLLAMA_MODEL=llama3.2:3b  # 或其他模型
```

支持的轻量级模型：
- `qwen2.5:3b` - 阿里巴巴Qwen，中文能力强（推荐）
- `llama3.2:3b` - Meta Llama3.2
- `gemma2:2b` - Google Gemma2，最轻量
- `phi3:3.8b` - Microsoft Phi3

---

## 🐛 故障排除

### 问题1: Docker服务未启动

**症状**:
```
Cannot connect to the Docker daemon
```

**解决**:
- Windows/Mac: 启动Docker Desktop
- Linux: `sudo systemctl start docker`

### 问题2: 端口被占用

**症状**:
```
bind: address already in use
```

**解决**:
```bash
# 查看端口占用
netstat -ano | findstr 9200  # Windows
lsof -i :9200                # Linux/Mac

# 修改docker-compose.yml中的端口映射
ports:
  - "19200:9200"  # 改用19200端口
```

### 问题3: Elasticsearch启动失败

**症状**:
```
max virtual memory areas vm.max_map_count [65530] is too low
```

**解决**:
```bash
# Linux
sudo sysctl -w vm.max_map_count=262144

# 永久生效
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# Windows (Docker Desktop)
# 在Docker Desktop设置中增加内存限制
```

### 问题4: Ollama模型下载失败

**症状**:
模型下载超时或失败

**解决**:
```bash
# 手动下载模型
docker exec -it chatcompass-ollama ollama pull qwen2.5:3b

# 使用国内镜像（如果有）
# 或者使用更小的模型
docker exec -it chatcompass-ollama ollama pull gemma2:2b
```

### 问题5: 内存不足

**症状**:
服务启动后系统变卡

**解决**:
```yaml
# 减少ES内存
- "ES_JAVA_OPTS=-Xms512m -Xmx512m"

# 或使用更小的模型
- OLLAMA_MODEL=gemma2:2b
```

---

## ⚡ 性能优化

### 1. Elasticsearch优化

```yaml
# docker-compose.yml
elasticsearch:
  environment:
    # 禁用swap
    - bootstrap.memory_lock=true
    
    # 调整线程池
    - thread_pool.write.queue_size=1000
    
    # 增加刷新间隔（减少IO）
    - index.refresh_interval=30s
```

### 2. Ollama优化

```bash
# 启用GPU加速（需要nvidia-docker）
docker-compose --profile gpu up -d

# 使用量化模型（更小更快）
docker exec -it chatcompass-ollama ollama pull qwen2.5:3b-q4_0
```

### 3. Docker优化

```bash
# 清理未使用的资源
docker system prune -a

# 限制日志大小
# 在docker-compose.yml中添加
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📊 监控和维护

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 查看ES索引状态
curl http://localhost:9200/_cat/indices?v
```

### 数据备份

```bash
# 备份Elasticsearch数据
docker run --rm -v chatcompass_es_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/es_backup_$(date +%Y%m%d).tar.gz /data

# 备份Ollama模型
docker run --rm -v chatcompass_ollama_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/ollama_backup_$(date +%Y%m%d).tar.gz /data
```

### 数据恢复

```bash
# 恢复Elasticsearch数据
docker run --rm -v chatcompass_es_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/es_backup_20260113.tar.gz -C /
```

---

## 🔗 相关链接

- [Elasticsearch文档](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/index.html)
- [Ollama文档](https://github.com/ollama/ollama)
- [Docker文档](https://docs.docker.com/)
- [项目GitHub](https://github.com/EasyWind001/ChatCompass)

---

## 💡 最佳实践

1. **定期备份数据**
2. **监控资源使用**
3. **及时更新镜像**
4. **查看日志排查问题**
5. **根据需求调整资源限制**

---

**祝你使用愉快！** 🎉

如有问题，请提交 [Issue](https://github.com/EasyWind001/ChatCompass/issues)
