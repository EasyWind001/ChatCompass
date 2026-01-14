# 🚀 Docker 快速入门指南

> **5分钟快速上手ChatCompass Docker版**

---

## 📋 开始前检查

### 1. 确认Docker已安装

```bash
# 检查Docker版本
docker --version
# 期望输出：Docker version 20.10.x 或更高

# 检查Docker Compose版本
docker-compose --version
# 期望输出：Docker Compose version 2.x.x 或更高
```

**如果未安装**，请参考：[docs/DOCKER_GUIDE.md](DOCKER_GUIDE.md) 的安装说明

---

## 🎯 方式一：一键启动（推荐）

### Windows用户

```bash
# 双击运行
docker-start.bat

# 或在PowerShell/CMD中运行
.\docker-start.bat
```

### Linux/Mac用户

```bash
# 添加执行权限
chmod +x docker-start.sh

# 运行
./docker-start.sh
```

**脚本会自动**：
1. ✅ 检查Docker环境
2. ✅ 启动所有服务
3. ✅ 等待服务就绪
4. ✅ 下载Ollama模型
5. ✅ 显示访问地址

---

## 🎯 方式二：手动启动

### 步骤1：启动服务

```bash
# 进入项目目录
cd ChatCompass

# 启动所有服务（后台运行）
docker-compose up -d
```

**首次启动**会自动：
- 下载镜像（Elasticsearch + Ollama，约2GB）
- 创建数据卷
- 初始化配置

**预计耗时**：5-15分钟（取决于网速）

### 步骤2：查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 期望输出：
# NAME                        STATUS
# chatcompass-app             Up
# chatcompass-elasticsearch   Up (healthy)
# chatcompass-ollama          Up (healthy)
```

### 步骤3：等待初始化完成

```bash
# 查看应用日志（重要！）
docker-compose logs -f chatcompass

# 看到以下信息表示启动成功：
# ✅ "ChatCompass启动完成！"
# ✅ "Elasticsearch索引初始化完成"
# ✅ "Ollama模型下载完成"
```

**⚠️ 首次启动注意事项**：
- Ollama会自动下载`qwen2.5:3b`模型（约3GB）
- 下载时间取决于网速（国内5-10分钟）
- 可以按`Ctrl+C`退出日志查看，服务继续运行

---

## ✅ 验证服务

### 1. 测试Elasticsearch

```bash
# 方法1：浏览器访问
http://localhost:9200

# 方法2：命令行测试
curl http://localhost:9200

# 期望输出：ES版本信息JSON
{
  "name" : "...",
  "cluster_name" : "docker-cluster",
  "version" : {
    "number" : "7.17.18",
    ...
  }
}
```

### 2. 测试Ollama

```bash
# 检查Ollama服务
curl http://localhost:11434/api/version

# 查看已下载的模型
docker exec chatcompass-ollama ollama list

# 期望输出：
# NAME            ID              SIZE      MODIFIED
# qwen2.5:3b      abc123...       3.0 GB    2 minutes ago
```

### 3. 测试ChatCompass

```bash
# 进入应用容器
docker exec -it chatcompass-app bash

# 在容器内运行
python main.py stats

# 期望输出：数据库统计信息
```

---

## 🎮 使用ChatCompass

### 方式A：在容器内使用（推荐）

```bash
# 1. 进入容器
docker exec -it chatcompass-app bash

# 2. 使用交互模式
python main.py

# 3. 或直接运行命令
python main.py search "Python"
python main.py stats
```

### 方式B：本地使用（需要配置）

```bash
# 1. 配置环境变量
export STORAGE_TYPE=elasticsearch
export ELASTICSEARCH_HOST=localhost
export ELASTICSEARCH_PORT=9200
export OLLAMA_HOST=http://localhost:11434
export AI_MODE=local

# 2. 本地运行
python main.py
```

---

## 📝 常用操作

### 添加对话

```bash
# 方式1：在容器内
docker exec -it chatcompass-app python main.py add "https://chatgpt.com/share/..."

# 方式2：交互模式
docker exec -it chatcompass-app python main.py
ChatCompass> add https://chatgpt.com/share/...
```

### 搜索对话

```bash
# 搜索关键词
docker exec -it chatcompass-app python main.py search "Python教程"

# 在交互模式
ChatCompass> search Python教程
```

### 查看统计

```bash
# 查看数据库统计
docker exec -it chatcompass-app python main.py stats

# 输出示例：
# 总对话数: 10
# 总消息数: 156
# 数据库大小: 2.3 MB
```

### 查看对话详情

```bash
# 查看第1条对话
docker exec -it chatcompass-app python main.py show 1
```

---

## 🛠️ 管理服务

### 查看日志

```bash
# 所有服务日志
docker-compose logs

# 特定服务日志
docker-compose logs chatcompass
docker-compose logs elasticsearch
docker-compose logs ollama

# 实时查看日志
docker-compose logs -f chatcompass

# 查看最近100行
docker-compose logs --tail=100 chatcompass
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止但保留数据
docker-compose stop
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart chatcompass
```

### 完全清理（⚠️ 会删除所有数据）

```bash
# 停止并删除容器、网络、数据卷
docker-compose down -v

# 删除镜像（可选）
docker rmi elasticsearch:7.17.18 ollama/ollama:latest
```

---

## 🔍 故障排查

### 问题1：服务启动失败

**症状**：`docker-compose up -d` 失败

**检查步骤**：
```bash
# 1. 查看详细错误
docker-compose up

# 2. 检查端口占用
netstat -ano | findstr 9200    # Windows
lsof -i :9200                   # Linux/Mac

# 3. 查看Docker资源
docker system df
docker stats
```

**解决方案**：
- 修改端口（编辑docker-compose.yml）
- 增加Docker内存限制（Docker Desktop设置）
- 清理旧容器：`docker system prune -a`

### 问题2：Elasticsearch健康检查失败

**症状**：`elasticsearch (unhealthy)`

**解决方案**：
```bash
# 1. 查看ES日志
docker-compose logs elasticsearch

# 2. 检查ES健康状态
curl http://localhost:9200/_cluster/health

# 3. 如果内存不足，减少ES内存
# 编辑docker-compose.yml
- "ES_JAVA_OPTS=-Xms512m -Xmx512m"

# 4. 重启ES
docker-compose restart elasticsearch
```

### 问题3：Ollama模型下载慢或失败

**症状**：模型下载卡住或超时

**解决方案**：
```bash
# 方法1：手动下载模型
docker exec -it chatcompass-ollama ollama pull qwen2.5:3b

# 方法2：使用更小的模型
# 编辑docker-compose.yml，修改OLLAMA_MODEL
- OLLAMA_MODEL=gemma2:2b  # 只有2GB

# 方法3：查看下载进度
docker-compose logs -f ollama
```

### 问题4：容器启动但无法访问

**症状**：服务显示Running但无法访问

**检查步骤**：
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查网络
docker network ls
docker network inspect chatcompass_chatcompass-network

# 3. 测试容器内网络
docker exec -it chatcompass-app curl http://elasticsearch:9200
docker exec -it chatcompass-app curl http://ollama:11434/api/version
```

### 问题5：权限错误

**症状**：Permission denied

**解决方案**：
```bash
# Linux/Mac
# 修复data和logs目录权限
sudo chown -R $USER:$USER data/ logs/

# 或以root运行（不推荐）
sudo docker-compose up -d
```

---

## 📊 资源使用

### 预期资源占用

| 服务 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| Elasticsearch | 10-20% | 1-2GB | ~1GB |
| Ollama | 5-50% | 4-6GB | ~3GB |
| ChatCompass | <5% | <500MB | ~100MB |
| **总计** | ~30% | **6-8GB** | **~5GB** |

### 最低配置要求

- **CPU**: 4核心
- **内存**: 8GB RAM
- **磁盘**: 20GB可用空间

### 监控资源

```bash
# 实时监控
docker stats

# 查看磁盘使用
docker system df

# 查看容器详情
docker inspect chatcompass-app
```

---

## 🎯 下一步

### 导入现有数据

如果你已有SQLite数据库：

```bash
# 1. 复制数据库文件到data目录
cp chatcompass.db data/

# 2. 进入容器
docker exec -it chatcompass-app bash

# 3. 运行迁移
python -m database.migrate_to_es \
    --source /app/data/chatcompass.db \
    --validate
```

### 访问Kibana（可选）

如果需要可视化查看Elasticsearch数据，可以启动Kibana：

```yaml
# 在docker-compose.yml中添加
kibana:
  image: kibana:7.17.18
  ports:
    - "5601:5601"
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

访问：http://localhost:5601

---

## 🔗 相关文档

- [完整Docker指南](DOCKER_GUIDE.md) - 详细配置和优化
- [主README](../README.md) - 项目介绍
- [发布说明](V1.2.2_RELEASE_NOTES.md) - v1.2.2新功能

---

## 💡 最佳实践

1. **首次启动**：耐心等待模型下载（5-10分钟）
2. **日志查看**：遇到问题先看日志 `docker-compose logs`
3. **数据备份**：定期备份data目录和Docker volumes
4. **资源监控**：用`docker stats`监控资源使用
5. **及时更新**：定期执行`docker-compose pull`更新镜像

---

**快速命令速查表**：

```bash
# 启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f chatcompass

# 进入容器
docker exec -it chatcompass-app bash

# 使用应用
docker exec -it chatcompass-app python main.py

# 停止
docker-compose down
```

---

**🎉 祝你使用愉快！如有问题，请查看故障排查章节或提交Issue。**
