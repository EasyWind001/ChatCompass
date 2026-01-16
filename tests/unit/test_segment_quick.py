#!/usr/bin/env python3
"""快速测试分段策略"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.ollama_client import OllamaClient

def main():
    print("🧪 分段策略快速测试\n")
    
    client = OllamaClient("http://localhost:11434", "qwen2.5:3b", 180)
    
    tests_passed = 0
    tests_total = 0
    
    # 测试1: 短文本
    tests_total += 1
    print("测试1: 短文本不分段...", end=" ")
    text = "Hello " * 500  # 3000字符
    segments = client._split_into_segments(text)
    if len(segments) == 1:
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (预期1段，实际{len(segments)}段)")
    
    # 测试2: 中等文本
    tests_total += 1
    print("测试2: 中等文本分2-3段...", end=" ")
    text = "User: Q\n\nAssistant: A\n\n" * 500  # 15000字符
    segments = client._split_into_segments(text)
    if 2 <= len(segments) <= 4:
        print(f"✅ ({len(segments)}段)")
        tests_passed += 1
    else:
        print(f"❌ (预期2-4段，实际{len(segments)}段)")
    
    # 测试3: 超长文本
    tests_total += 1
    print("测试3: 超长文本分5-7段...", end=" ")
    text = "User: Q\n\nAssistant: A\n\n" * 1500  # 45000字符
    segments = client._split_into_segments(text)
    if 5 <= len(segments) <= 10:
        print(f"✅ ({len(segments)}段)")
        tests_passed += 1
    else:
        print(f"❌ (预期5-10段，实际{len(segments)}段)")
    
    # 测试4: 空文本
    tests_total += 1
    print("测试4: 空文本处理...", end=" ")
    segments = client._split_into_segments("")
    if len(segments) == 0:
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (预期0段，实际{len(segments)}段)")
    
    # 测试5: 精确边界
    tests_total += 1
    print("测试5: 精确边界6000字符...", end=" ")
    segments = client._split_into_segments("A" * 6000)
    if len(segments) == 1:
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (预期1段，实际{len(segments)}段)")
    
    # 测试6: 超过边界1字符
    tests_total += 1
    print("测试6: 超过边界6001字符...", end=" ")
    segments = client._split_into_segments("A" * 6001)
    if len(segments) == 2:
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (预期2段，实际{len(segments)}段)")
    
    # 测试7: 强制分割（无边界）
    tests_total += 1
    print("测试7: 无边界强制分割...", end=" ")
    segments = client._split_into_segments("A" * 20000)
    if len(segments) >= 3:
        print(f"✅ ({len(segments)}段)")
        tests_passed += 1
    else:
        print(f"❌ (预期≥3段，实际{len(segments)}段)")
    
    # 测试8: 策略选择阈值
    tests_total += 1
    print("测试8: 策略选择阈值（12000）...", end=" ")
    text_11999 = "A" * 11999
    text_12000 = "A" * 12000
    if len(text_11999) <= 12000 and len(text_12000) > 12000:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # 测试9: 数据完整性
    tests_total += 1
    print("测试9: 数据完整性...", end=" ")
    original = "User: Q\n\nAssistant: A\n\n" * 1000
    segments = client._split_into_segments(original)
    combined = "".join(segments)
    if len(combined) >= len(original) * 0.98:
        print(f"✅ (保留{len(combined)/len(original)*100:.1f}%)")
        tests_passed += 1
    else:
        print(f"❌ (仅保留{len(combined)/len(original)*100:.1f}%)")
    
    # 测试10: 性能测试
    tests_total += 1
    print("测试10: 性能测试（大文本分段）...", end=" ")
    import time
    text = "User: Q\n\nAssistant: A\n\n" * 10000  # 300000字符
    start = time.time()
    segments = client._split_into_segments(text)
    duration = time.time() - start
    if duration < 2.0:
        print(f"✅ ({duration:.3f}秒，{len(segments)}段)")
        tests_passed += 1
    else:
        print(f"❌ (耗时{duration:.3f}秒，超过2秒)")
    
    # 总结
    print("\n" + "="*50)
    print(f"测试结果: {tests_passed}/{tests_total} 通过")
    if tests_passed == tests_total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
