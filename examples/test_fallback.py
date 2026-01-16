"""
AI降级方案测试示例

演示当AI超时或失败时，自动使用基于规则的降级方案
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import AIService, AIConfig
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def test_normal_analysis():
    """测试1: 正常AI分析"""
    print("\n" + "="*70)
    print("测试1: 正常AI分析（Ollama服务可用）")
    print("="*70 + "\n")
    
    # 使用正常配置
    config = AIConfig(
        enabled=True,
        timeout=180,
        enable_fallback=True
    )
    ai_service = AIService(config)
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，跳过此测试")
        return
    
    conversation = """
用户: 你好，我想学习Python数据分析，应该从哪里开始？

助手: 学习Python数据分析，建议按照以下步骤：
1. 掌握Python基础语法
2. 学习NumPy和Pandas库
3. 了解数据可视化（Matplotlib、Seaborn）
4. 实践项目

用户: Pandas有哪些常用操作？

助手: Pandas常用操作包括：
- 数据读取: read_csv(), read_excel()
- 数据筛选: loc[], iloc[]
- 数据清洗: dropna(), fillna()
- 数据聚合: groupby(), agg()
"""
    
    print("📄 对话内容（约600字符）\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="Python数据分析学习"
    )
    
    if result:
        print(f"\n✅ 分析成功!")
        print(f"📝 摘要: {result.summary[:100]}...")
        print(f"📁 分类: {result.category}")
        print(f"🏷️  标签: {', '.join(result.tags)}")
        print(f"📊 置信度: {result.confidence}")
        
        if result.confidence < 0.5:
            print(f"⚠️  这是降级方案的结果")
        else:
            print(f"✅ 这是AI模型的结果")


def test_timeout_with_fallback():
    """测试2: 超时后使用降级方案"""
    print("\n" + "="*70)
    print("测试2: 超时后自动降级（超时设置为1秒）")
    print("="*70 + "\n")
    
    # 设置极短的超时时间，强制触发超时
    config = AIConfig(
        enabled=True,
        timeout=1,  # 1秒必然超时
        enable_fallback=True  # 启用降级
    )
    ai_service = AIService(config)
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，跳过此测试")
        return
    
    conversation = """
用户: 介绍一下Docker容器化技术的优势和应用场景。

助手: Docker是一个开源的容器化平台，主要优势包括：
1. 轻量级：相比虚拟机更节省资源
2. 可移植性：一次构建，到处运行
3. 快速部署：秒级启动容器
4. 环境一致：开发、测试、生产环境完全一致
5. 易于扩展：支持水平扩展

常见应用场景：
- 微服务架构
- CI/CD流水线
- 开发环境标准化
- 应用快速部署
"""
    
    print("📄 对话内容（约500字符）")
    print("⏰ 超时设置：1秒（强制触发超时）\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="Docker容器化技术"
    )
    
    if result:
        print(f"\n✅ 降级方案生成结果!")
        print(f"📝 摘要: {result.summary}")
        print(f"📁 分类: {result.category}")
        print(f"🏷️  标签: {', '.join(result.tags)}")
        print(f"📊 置信度: {result.confidence}")
        
        if result.confidence < 0.5:
            print(f"\n⚠️  这是降级方案的结果（基于规则，非AI）")
        else:
            print(f"\n❓ 意外：没有触发降级方案")
    else:
        print(f"\n❌ 未能生成结果（可能降级方案也失败了）")


def test_timeout_without_fallback():
    """测试3: 超时且禁用降级方案"""
    print("\n" + "="*70)
    print("测试3: 超时且禁用降级方案（返回None）")
    print("="*70 + "\n")
    
    # 禁用降级方案
    config = AIConfig(
        enabled=True,
        timeout=1,  # 1秒必然超时
        enable_fallback=False  # 禁用降级
    )
    ai_service = AIService(config)
    
    if not ai_service.is_available():
        print("❌ AI服务不可用，跳过此测试")
        return
    
    conversation = """
用户: 什么是机器学习？

助手: 机器学习是人工智能的一个分支，通过算法让计算机从数据中学习规律，
无需明确编程即可完成特定任务。主要包括监督学习、无监督学习和强化学习。
"""
    
    print("📄 对话内容（约200字符）")
    print("⏰ 超时设置：1秒")
    print("🚫 降级方案：禁用\n")
    
    result = ai_service.analyze_conversation(
        conversation,
        title="机器学习概念"
    )
    
    if result:
        print(f"\n❓ 意外：居然有结果")
        print(f"结果: {result}")
    else:
        print(f"\n✅ 符合预期：返回None")
        print(f"💡 对话仍会被保存，但没有摘要、分类和标签")


def test_fallback_quality():
    """测试4: 降级方案质量评估"""
    print("\n" + "="*70)
    print("测试4: 降级方案质量评估（与AI结果对比）")
    print("="*70 + "\n")
    
    # 首先获取AI结果
    config_ai = AIConfig(enabled=True, timeout=180, enable_fallback=False)
    ai_service_ai = AIService(config_ai)
    
    # 然后获取降级结果
    config_fallback = AIConfig(enabled=True, timeout=1, enable_fallback=True)
    ai_service_fallback = AIService(config_fallback)
    
    if not ai_service_ai.is_available():
        print("❌ AI服务不可用，跳过此测试")
        return
    
    conversation = """
用户: 如何优化SQL查询性能？

助手: SQL查询优化的常见方法：
1. 创建合适的索引（B-Tree、哈希索引）
2. 避免SELECT *，只查询需要的字段
3. 使用JOIN代替子查询
4. 分析执行计划（EXPLAIN）
5. 优化WHERE条件（避免函数操作）
6. 使用查询缓存
7. 分区表（大表优化）

用户: 什么时候应该使用索引？

助手: 索引适用场景：
- WHERE条件频繁查询的字段
- JOIN连接的字段
- ORDER BY排序的字段
- GROUP BY分组的字段

不适用场景：
- 数据量很小的表
- 频繁更新的字段
- 低选择性字段（如性别）
"""
    
    print("📄 测试对话：SQL查询优化（约600字符）\n")
    
    # 获取AI结果
    print("=" * 70)
    print("AI分析结果（Ollama + qwen2.5:3b）")
    print("=" * 70)
    
    result_ai = ai_service_ai.analyze_conversation(
        conversation,
        title="SQL查询优化"
    )
    
    if result_ai:
        print(f"📝 摘要: {result_ai.summary}")
        print(f"📁 分类: {result_ai.category}")
        print(f"🏷️  标签: {', '.join(result_ai.tags)}")
        print(f"📊 置信度: {result_ai.confidence}")
    else:
        print("❌ AI分析失败")
    
    input("\n按Enter继续获取降级结果...")
    
    # 获取降级结果
    print("\n" + "=" * 70)
    print("降级方案结果（基于规则）")
    print("=" * 70)
    
    result_fallback = ai_service_fallback.analyze_conversation(
        conversation,
        title="SQL查询优化"
    )
    
    if result_fallback:
        print(f"📝 摘要: {result_fallback.summary}")
        print(f"📁 分类: {result_fallback.category}")
        print(f"🏷️  标签: {', '.join(result_fallback.tags)}")
        print(f"📊 置信度: {result_fallback.confidence}")
    else:
        print("❌ 降级分析失败")
    
    # 对比分析
    if result_ai and result_fallback:
        print("\n" + "=" * 70)
        print("对比分析")
        print("=" * 70)
        print(f"\n分类对比：")
        print(f"  AI: {result_ai.category}")
        print(f"  降级: {result_fallback.category}")
        print(f"  一致性: {'✅ 相同' if result_ai.category == result_fallback.category else '❌ 不同'}")
        
        print(f"\n标签对比：")
        print(f"  AI: {', '.join(result_ai.tags)}")
        print(f"  降级: {', '.join(result_fallback.tags)}")
        
        common_tags = set(result_ai.tags) & set(result_fallback.tags)
        print(f"  共同标签: {', '.join(common_tags) if common_tags else '无'}")
        
        print(f"\n摘要长度对比：")
        print(f"  AI: {len(result_ai.summary)} 字符")
        print(f"  降级: {len(result_fallback.summary)} 字符")


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("ChatCompass AI降级方案测试")
    print("="*70)
    print("\n本测试将演示：")
    print("1. ✅ 正常AI分析")
    print("2. ✅ 超时后自动降级")
    print("3. ✅ 禁用降级方案")
    print("4. ✅ AI vs 降级质量对比")
    print("\n请确保：")
    print("- Ollama服务已启动 (ollama serve)")
    print("- 已拉取模型 (ollama pull qwen2.5:3b)")
    
    input("\n按Enter开始测试...")
    
    try:
        # 运行所有测试
        test_normal_analysis()
        input("\n按Enter继续下一个测试...")
        
        test_timeout_with_fallback()
        input("\n按Enter继续下一个测试...")
        
        test_timeout_without_fallback()
        input("\n按Enter继续最后一个测试...")
        
        test_fallback_quality()
        
        print("\n" + "="*70)
        print("✅ 所有测试完成!")
        print("="*70)
        print("\n总结：")
        print("- 降级方案可以在AI失败时提供基础分析")
        print("- 降级结果置信度较低（0.3），但总比没有好")
        print("- 生产环境建议启用降级方案（AI_ENABLE_FALLBACK=true）")
        print("- 降级方案响应速度极快（<1秒）")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
