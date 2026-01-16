#!/usr/bin/env python3
"""
统一测试运行脚本
运行所有测试套件并生成报告
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_pytest_tests(test_dir, description):
    """运行pytest测试"""
    print_section(f"{description} - pytest测试")
    
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
        "-q"
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def run_script_tests(test_file, description):
    """运行独立测试脚本"""
    print_section(f"{description} - 独立脚本测试")
    
    result = subprocess.run([sys.executable, str(test_file)], capture_output=False)
    return result.returncode == 0


def main():
    """运行所有测试"""
    print_section("ChatCompass 测试套件")
    print("运行所有测试...")
    
    results = {}
    
    # 1. 单元测试
    results['单元测试'] = run_pytest_tests(
        PROJECT_ROOT / "tests" / "unit",
        "单元测试"
    )
    
    # 2. 集成测试
    integration_dir = PROJECT_ROOT / "tests" / "integration"
    if integration_dir.exists() and list(integration_dir.glob("test_*.py")):
        results['集成测试'] = run_pytest_tests(
            integration_dir,
            "集成测试"
        )
    
    # 3. E2E测试（独立脚本）
    delete_e2e = PROJECT_ROOT / "tests" / "e2e" / "test_delete_e2e.py"
    if delete_e2e.exists():
        results['Delete E2E测试'] = run_script_tests(
            delete_e2e,
            "Delete功能端到端测试"
        )
    
    # 4. 功能测试
    basic_tests = PROJECT_ROOT / "tests" / "test_basic_functions.py"
    if basic_tests.exists():
        results['功能测试'] = run_pytest_tests(
            basic_tests,
            "基础功能测试"
        )
    
    # 生成报告
    print_section("测试结果汇总")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {name}")
    
    print("\n" + "=" * 80)
    print(f"总计: {passed}/{total} 测试套件通过")
    print("=" * 80)
    
    return all(results.values())


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
