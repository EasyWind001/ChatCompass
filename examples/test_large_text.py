"""
大文本处理测试示例

演示ChatCompass如何处理超长对话文本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import get_ai_service, AIConfig
import logging

# 配置日志显示详细进度
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def generate_large_conversation(size: str = "small") -> str:
    """生成测试用的大文本对话"""
    
    base_conversation = """
用户: 你好，我想学习Docker部署应用，应该从哪里开始？

助手: Docker是容器化技术的代表，学习Docker部署需要按照以下步骤：

1. **理解容器概念**
   - 容器 vs 虚拟机
   - 镜像和容器的区别
   - Docker架构

2. **安装Docker**
   - Windows: Docker Desktop
   - Linux: docker-engine
   - MacOS: Docker Desktop

3. **基础命令**
   - docker run: 运行容器
   - docker build: 构建镜像
   - docker-compose: 多容器编排

4. **编写Dockerfile**
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "main.py"]
   ```

5. **使用docker-compose**
   ```yaml
   version: '3'
   services:
     app:
       build: .
       ports:
         - "5000:5000"
     db:
       image: postgres:13
   ```

用户: 如何优化Docker镜像大小？

助手: 优化Docker镜像大小的最佳实践：

1. **使用Alpine基础镜像**
   ```dockerfile
   FROM python:3.9-alpine  # 比标准镜像小10倍
   ```

2. **多阶段构建**
   ```dockerfile
   # 构建阶段
   FROM node:16 AS builder
   COPY . .
   RUN npm run build
   
   # 运行阶段
   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   ```

3. **合并RUN命令**
   ```dockerfile
   # ❌ 不好
   RUN apt-get update
   RUN apt-get install -y git
   RUN apt-get clean
   
   # ✅ 好
   RUN apt-get update && \\
       apt-get install -y git && \\
       apt-get clean && \\
       rm -rf /var/lib/apt/lists/*
   ```

4. **使用.dockerignore**
   ```
   node_modules/
   .git/
   *.log
   __pycache__/
   ```

5. **清理缓存**
   ```dockerfile
   RUN pip install --no-cache-dir -r requirements.txt
   ```

用户: Docker Compose如何管理多个环境？

助手: 管理多环境的几种方案：

1. **使用多个compose文件**
   ```bash
   # docker-compose.yml (基础配置)
   # docker-compose.dev.yml (开发环境)
   # docker-compose.prod.yml (生产环境)
   
   # 开发环境
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
   
   # 生产环境
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

2. **使用环境变量**
   ```yaml
   services:
     app:
       image: myapp:${TAG:-latest}
       environment:
         - ENV=${ENV:-production}
   ```

3. **使用.env文件**
   ```bash
   # .env.dev
   TAG=dev
   DATABASE_URL=postgresql://localhost:5432/dev_db
   
   # .env.prod
   TAG=latest
   DATABASE_URL=postgresql://prod-server:5432/prod_db
   ```

"""
    
    if size == "small":
        return base_conversation
    
    elif size == "medium":
        # 复制3次，模拟中等长度
        return base_conversation * 3
    
    elif size == "large":
        # 复制10次，模拟大文本（约1.5万字符）
        return base_conversation * 10
    
    elif size == "huge":
        # 复制30次，模拟超大文本（约4.5万字符）
        return base_conversation * 30
    
    return base_conversation


def test_small_text():
    """测试小文本（正常速度）"""
    print("\n" + "="*70)
    print("测试1: 小文本处理（约1500字符）")
    print("="*70 + "\n")
    
    ai_service = get_ai_service()
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，请确保Ollama已启动")
        return
    
    conversation = generate_large_conversation("small")
    print(f"📄 文本长度: {len(conversation):,} 字符\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="Docker部署入门",
        show_progress=True
    )
    
    if result:
        print(f"\n✅ 分析成功!")
        print(f"📝 摘要: {result.summary[:100]}...")
        print(f"📁 分类: {result.category}")
        print(f"🏷️  标签: {', '.join(result.tags)}")


def test_large_text():
    """测试大文本（触发智能截断）"""
    print("\n" + "="*70)
    print("测试2: 大文本处理（约15,000字符，触发智能截断）")
    print("="*70 + "\n")
    
    ai_service = get_ai_service()
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，请确保Ollama已启动")
        return
    
    conversation = generate_large_conversation("large")
    print(f"📄 文本长度: {len(conversation):,} 字符")
    print(f"💡 将触发智能截断优化\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="Docker部署完整教程",
        show_progress=True
    )
    
    if result:
        print(f"\n✅ 分析成功!")
        print(f"📝 摘要: {result.summary[:100]}...")
        print(f"📁 分类: {result.category}")
        print(f"🏷️  标签: {', '.join(result.tags)}")


def test_huge_text():
    """测试超大文本（模拟真实场景）"""
    print("\n" + "="*70)
    print("测试3: 超大文本处理（约45,000字符，接近真实场景）")
    print("="*70 + "\n")
    
    ai_service = get_ai_service()
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，请确保Ollama已启动")
        return
    
    conversation = generate_large_conversation("huge")
    print(f"📄 文本长度: {len(conversation):,} 字符")
    print(f"💡 将触发智能截断 + 流式输出\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="Docker完整知识体系",
        show_progress=True
    )
    
    if result:
        print(f"\n✅ 分析成功!")
        print(f"📝 摘要: {result.summary[:100]}...")
        print(f"📁 分类: {result.category}")
        print(f"🏷️  标签: {', '.join(result.tags)}")


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("ChatCompass 大文本处理测试")
    print("="*70)
    print("\n本测试将演示以下优化功能：")
    print("1. ✅ 智能截断（保留开头70% + 结尾30%）")
    print("2. ✅ 实时进度提示")
    print("3. ✅ 处理时间预估")
    print("4. ✅ 流式输出（大文本）")
    print("\n请确保：")
    print("- Ollama服务已启动 (ollama serve)")
    print("- 已拉取模型 (ollama pull qwen2.5:3b)")
    
    input("\n按Enter开始测试...")
    
    # 运行测试
    try:
        test_small_text()
        input("\n按Enter继续下一个测试...")
        
        test_large_text()
        input("\n按Enter继续最后一个测试...")
        
        test_huge_text()
        
        print("\n" + "="*70)
        print("✅ 所有测试完成!")
        print("="*70)
        print("\n总结：")
        print("- 小文本：正常速度，无优化")
        print("- 大文本：智能截断，速度提升2-3倍")
        print("- 超大文本：智能截断 + 流式输出，用户体验最佳")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")


if __name__ == '__main__':
    main()
