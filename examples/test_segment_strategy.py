#!/usr/bin/env python3
"""
分段摘要策略测试脚本
演示如何处理超长对话
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ollama_client import OllamaClient
from ai.ai_service import AIConfig


def generate_long_conversation(num_turns: int = 20) -> str:
    """生成模拟的长对话"""
    conversation = []
    
    topics = [
        ("Docker镜像优化", "多阶段构建的最佳实践是什么？", "可以使用多阶段构建..."),
        ("基础镜像选择", "Alpine和Ubuntu哪个更好？", "这取决于你的需求..."),
        ("依赖管理", "如何优化Python依赖安装？", "可以使用requirements.txt分层..."),
        ("缓存策略", "如何利用Docker层缓存？", "合理安排Dockerfile指令顺序..."),
        ("安全扫描", "如何扫描镜像漏洞？", "可以使用Trivy或Snyk..."),
    ]
    
    for i in range(num_turns):
        topic, question, answer = topics[i % len(topics)]
        
        # 用户问题
        conversation.append(f"User: 关于{topic}，{question}")
        
        # AI回答（模拟长回答）
        full_answer = f"""Assistant: {answer}

让我详细解释一下：

1. 首先，{topic}的核心原理是...
   - 这样做可以...
   - 需要注意的是...

2. 其次，在实际应用中：
   ```dockerfile
   # 示例代码
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   ```

3. 最后，一些最佳实践：
   - 优化点1：...
   - 优化点2：...
   - 优化点3：...

这样可以显著提升性能和安全性。还有什么想了解的吗？
"""
        conversation.append(full_answer)
        
        # 用户追问
        if i % 3 == 0:
            conversation.append(f"User: 能否给个完整的例子？")
            conversation.append(f"Assistant: 当然！这里有个完整的{topic}实例...")
    
    return "\n\n".join(conversation)


def test_short_text():
    """测试1：短文本（直接分析）"""
    print("="*60)
    print("测试1: 短文本（5000字符）")
    print("="*60)
    
    # 生成短对话
    conversation = generate_long_conversation(3)  # 约5000字符
    print(f"文本长度: {len(conversation):,} 字符")
    
    # 分析
    config = AIConfig.from_env()
    client = OllamaClient(
        base_url=config.ollama_host,
        model=config.ollama_model,
        timeout=config.timeout
    )
    
    try:
        result = client.analyze_conversation(conversation)
        print(f"\n✅ 分析结果:")
        print(f"   摘要: {result.summary}")
        print(f"   分类: {result.category}")
        print(f"   标签: {', '.join(result.tags)}")
        print(f"   置信度: {result.confidence}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def test_medium_text():
    """测试2：中长文本（分段分析 2-3段）"""
    print("\n" + "="*60)
    print("测试2: 中长文本（15000字符）")
    print("="*60)
    
    # 生成中等对话
    conversation = generate_long_conversation(10)  # 约15000字符
    print(f"文本长度: {len(conversation):,} 字符")
    print(f"预期分段: 2-3段")
    
    # 分析
    config = AIConfig.from_env()
    client = OllamaClient(
        base_url=config.ollama_host,
        model=config.ollama_model,
        timeout=config.timeout
    )
    
    try:
        result = client.analyze_conversation(conversation)
        print(f"\n✅ 分析结果:")
        print(f"   摘要: {result.summary}")
        print(f"   分类: {result.category}")
        print(f"   标签: {', '.join(result.tags)}")
        print(f"   置信度: {result.confidence}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def test_long_text():
    """测试3：超长文本（分段分析 5-6段）"""
    print("\n" + "="*60)
    print("测试3: 超长文本（30000字符）")
    print("="*60)
    
    # 生成超长对话
    conversation = generate_long_conversation(20)  # 约30000字符
    print(f"文本长度: {len(conversation):,} 字符")
    print(f"预期分段: 5-6段")
    
    # 分析
    config = AIConfig.from_env()
    client = OllamaClient(
        base_url=config.ollama_host,
        model=config.ollama_model,
        timeout=config.timeout
    )
    
    try:
        result = client.analyze_conversation(conversation)
        print(f"\n✅ 分析结果:")
        print(f"   摘要: {result.summary}")
        print(f"   分类: {result.category}")
        print(f"   标签: {', '.join(result.tags)}")
        print(f"   置信度: {result.confidence}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def test_segment_algorithm():
    """测试4：分段算法"""
    print("\n" + "="*60)
    print("测试4: 智能分段算法")
    print("="*60)
    
    # 生成测试文本
    conversation = generate_long_conversation(15)  # 约22000字符
    print(f"原始文本长度: {len(conversation):,} 字符\n")
    
    # 测试分段
    config = AIConfig.from_env()
    client = OllamaClient(
        base_url=config.ollama_host,
        model=config.ollama_model,
        timeout=config.timeout
    )
    
    segments = client._split_into_segments(conversation)
    
    print(f"分段结果:")
    print(f"  总段数: {len(segments)}")
    for i, segment in enumerate(segments, 1):
        print(f"  第{i}段: {len(segment):>6,} 字符 | 预览: {segment[:50]}...")
    
    # 验证分段质量
    total_length = sum(len(s) for s in segments)
    print(f"\n分段质量检查:")
    print(f"  原始长度: {len(conversation):,} 字符")
    print(f"  分段总和: {total_length:,} 字符")
    print(f"  差异: {abs(len(conversation) - total_length)} 字符")
    
    # 检查是否在对话边界分割
    boundary_splits = 0
    for i, segment in enumerate(segments[:-1]):  # 除最后一段
        if any(segment.strip().endswith(sep.strip()) 
               for sep in ['User:', 'Assistant:', '用户:', '助手:']):
            boundary_splits += 1
    
    print(f"  边界分割: {boundary_splits}/{len(segments)-1} ({boundary_splits/(len(segments)-1)*100:.0f}%)")


def compare_strategies():
    """测试5：策略对比"""
    print("\n" + "="*60)
    print("测试5: 简单截断 vs 分段合并策略对比")
    print("="*60)
    
    # 生成测试对话
    conversation = generate_long_conversation(20)  # 约30000字符
    print(f"测试文本: {len(conversation):,} 字符\n")
    
    config = AIConfig.from_env()
    client = OllamaClient(
        base_url=config.ollama_host,
        model=config.ollama_model,
        timeout=config.timeout
    )
    
    # 策略1：简单截断（模拟旧方法）
    print("【策略1：简单截断】")
    max_length = 8000
    head_length = int(max_length * 0.7)
    tail_length = int(max_length * 0.3)
    truncated = (
        conversation[:head_length] + 
        "\n\n...[中间内容已省略]...\n\n" +
        conversation[-tail_length:]
    )
    print(f"  截断后长度: {len(truncated):,} 字符")
    print(f"  保留率: {len(truncated)/len(conversation)*100:.1f}%")
    print(f"  丢失内容: 约 {len(conversation) - len(truncated):,} 字符")
    
    # 策略2：分段合并（新方法）
    print("\n【策略2：分段合并】")
    segments = client._split_into_segments(conversation)
    print(f"  分段数: {len(segments)}")
    print(f"  每段长度: {[len(s) for s in segments]}")
    print(f"  保留率: 100%（通过摘要保留所有段落的关键信息）")
    print(f"  优势: 覆盖完整对话流程，不丢失中间讨论")


def main():
    """主测试函数"""
    print("🧪 分段摘要策略测试")
    print()
    
    # 检查AI服务
    config = AIConfig.from_env()
    if not config.enabled:
        print("❌ AI功能未启用，请设置 AI_ENABLED=true")
        return
    
    print("请选择测试:")
    print("1. 短文本（5000字符）- 直接分析")
    print("2. 中长文本（15000字符）- 分段分析")
    print("3. 超长文本（30000字符）- 分段分析")
    print("4. 分段算法测试")
    print("5. 策略对比")
    print("6. 运行所有测试")
    print()
    
    choice = input("请输入选择 [1-6]: ").strip()
    
    if choice == "1":
        test_short_text()
    elif choice == "2":
        test_medium_text()
    elif choice == "3":
        test_long_text()
    elif choice == "4":
        test_segment_algorithm()
    elif choice == "5":
        compare_strategies()
    elif choice == "6":
        test_short_text()
        test_medium_text()
        test_long_text()
        test_segment_algorithm()
        compare_strategies()
    else:
        print("❌ 无效选择")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()
