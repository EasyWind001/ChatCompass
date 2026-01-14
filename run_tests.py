"""
测试运行脚本
提供便捷的测试运行方式
"""
import sys
import pytest
from pathlib import Path


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    return pytest.main(["-v", "tests/"])


def run_unit_tests():
    """仅运行单元测试"""
    print("=" * 60)
    print("运行单元测试")
    print("=" * 60)
    return pytest.main(["-v", "tests/unit/"])


def run_integration_tests():
    """仅运行集成测试"""
    print("=" * 60)
    print("运行集成测试")
    print("=" * 60)
    return pytest.main(["-v", "tests/integration/"])


def run_coverage():
    """运行测试并生成覆盖率报告"""
    print("=" * 60)
    print("运行测试并生成覆盖率报告")
    print("=" * 60)
    return pytest.main([
        "-v",
        "--cov=database",
        "--cov=scrapers",
        "--cov=ai",
        "--cov-report=html",
        "--cov-report=term-missing",
        "tests/"
    ])


def run_specific_file(filepath):
    """运行指定测试文件"""
    print("=" * 60)
    print(f"运行测试文件: {filepath}")
    print("=" * 60)
    return pytest.main(["-v", filepath])


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "unit":
            exit_code = run_unit_tests()
        elif command == "integration":
            exit_code = run_integration_tests()
        elif command == "coverage":
            exit_code = run_coverage()
        elif command == "file" and len(sys.argv) > 2:
            exit_code = run_specific_file(sys.argv[2])
        elif command == "help":
            print_help()
            exit_code = 0
        else:
            print(f"未知命令: {command}")
            print_help()
            exit_code = 1
    else:
        # 默认运行所有测试
        exit_code = run_all_tests()
    
    return exit_code


def print_help():
    """打印帮助信息"""
    print("""
测试运行脚本

用法:
    python run_tests.py [命令]

命令:
    (无)          - 运行所有测试
    unit          - 仅运行单元测试
    integration   - 仅运行集成测试
    coverage      - 运行测试并生成覆盖率报告
    file <路径>   - 运行指定测试文件
    help          - 显示此帮助信息

示例:
    python run_tests.py
    python run_tests.py unit
    python run_tests.py file tests/unit/test_database.py
    python run_tests.py coverage
    """)


if __name__ == '__main__':
    sys.exit(main())
