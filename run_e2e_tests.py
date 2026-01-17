"""
v1.3.0 端到端测试执行脚本

运行完整的测试套件,使用渐进式测试模式
"""
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 80)
    print("🚀 ChatCompass v1.3.0 全面测试")
    print("=" * 80)
    print()
    
    # 测试套件列表 (按优先级排序)
    test_suites = [
        {
            "name": "快速核心测试",
            "path": "quick_test_e2e.py",
            "description": "数据库、错误处理、基础集成",
            "priority": 1
        },
        {
            "name": "单元测试",
            "path": "tests/unit",
            "description": "独立组件单元测试",
            "priority": 2
        },
        {
            "name": "GUI组件测试",
            "path": "tests/gui",
            "description": "GUI组件功能测试",
            "priority": 3
        },
        {
            "name": "集成测试",
            "path": "tests/integration",
            "description": "模块间集成测试",
            "priority": 4
        },
        {
            "name": "E2E场景测试",
            "path": "tests/e2e",
            "description": "真实场景端到端测试",
            "priority": 5
        }
    ]
    
    print("📋 测试计划:")
    for suite in test_suites:
        print(f"  {suite['priority']}. {suite['name']}")
        print(f"     📁 {suite['path']}")
        print(f"     📝 {suite['description']}")
        print()
    
    print("=" * 80)
    print("⚠️  使用渐进式测试模式:")
    print("   - 遇到错误会立即暂停")
    print("   - 可以查看完整错误信息")
    print("   - 修复后可以重试或继续")
    print("=" * 80)
    print()
    
    # 询问用户
    response = input("👉 开始测试? (建议先运行快速测试) [1-5/all/q]: ").strip().lower()
    
    if response == 'q':
        print("❌ 已取消测试")
        return
    
    if response == 'all':
        selected_suites = test_suites
    else:
        try:
            priority = int(response)
            selected_suites = [s for s in test_suites if s['priority'] == priority]
            if not selected_suites:
                print(f"❌ 无效的选项: {response}")
                return
        except ValueError:
            print(f"❌ 无效的选项: {response}")
            return
    
    print()
    print("=" * 80)
    print("🧪 开始执行测试")
    print("=" * 80)
    print()
    
    for suite in selected_suites:
        print(f"\n{'='*80}")
        print(f"📦 {suite['name']}")
        print(f"{'='*80}\n")
        
        # 构建命令
        cmd = [
            sys.executable,
            "run_tests_interactive.py",
            suite['path']
        ]
        
        # 如果是快速测试,添加--quick标志
        if suite['priority'] == 1:
            cmd.append("--quick")
        
        print(f"▶️  执行命令: {' '.join(cmd)}")
        print()
        
        # 运行测试
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print(f"\n⚠️  {suite['name']} 测试中断或失败")
            response = input("\n👉 继续下一个测试套件? [y/n]: ").strip().lower()
            if response != 'y':
                print("❌ 测试已停止")
                return
        else:
            print(f"\n✅ {suite['name']} 测试完成")
    
    print("\n" + "=" * 80)
    print("🎉 测试执行完毕!")
    print("=" * 80)
    print("\n📊 查看结果:")
    print("  - 控制台输出")
    print("  - logs/chatcompass_*.log")
    print("  - GUI → 帮助 → 查看错误日志")
    print()

if __name__ == "__main__":
    main()
