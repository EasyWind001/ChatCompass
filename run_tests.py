#!/usr/bin/env python3
"""
ChatCompass 测试运行脚本

快速运行各类测试的便捷脚本。
"""
import sys
import subprocess
import argparse


def run_command(cmd):
    """运行命令并返回结果"""
    print(f"\n{'='*70}")
    print(f"运行: {' '.join(cmd)}")
    print('='*70)
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='ChatCompass测试运行脚本')
    parser.add_argument('test_type', nargs='?', default='all',
                        choices=['all', 'unit', 'e2e', 'integration', 'quick', 'cov'],
                        help='测试类型')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')
    parser.add_argument('-k', '--keyword', type=str,
                        help='按关键词过滤测试')
    parser.add_argument('-m', '--marker', type=str,
                        help='按标记过滤测试')
    
    args = parser.parse_args()
    
    # 基础pytest命令
    base_cmd = ['pytest']
    if args.verbose:
        base_cmd.append('-v')
    if args.keyword:
        base_cmd.extend(['-k', args.keyword])
    if args.marker:
        base_cmd.extend(['-m', args.marker])
    
    # 根据测试类型选择
    if args.test_type == 'all':
        print("\n🧪 运行所有测试...")
        cmd = base_cmd + ['tests/']
        success = run_command(cmd)
    
    elif args.test_type == 'unit':
        print("\n⚡ 运行单元测试...")
        cmd = base_cmd + ['tests/unit/']
        success = run_command(cmd)
    
    elif args.test_type == 'e2e':
        print("\n🎯 运行E2E测试...")
        cmd = base_cmd + ['tests/e2e/']
        success = run_command(cmd)
    
    elif args.test_type == 'integration':
        print("\n🔗 运行集成测试...")
        cmd = base_cmd + ['tests/integration/']
        success = run_command(cmd)
    
    elif args.test_type == 'quick':
        print("\n⚡ 运行快速测试（跳过慢速测试）...")
        cmd = base_cmd + ['-m', 'not slow', 'tests/']
        success = run_command(cmd)
    
    elif args.test_type == 'cov':
        print("\n📊 运行测试并生成覆盖率报告...")
        cmd = base_cmd + [
            '--cov=.',
            '--cov-report=html',
            '--cov-report=term',
            'tests/'
        ]
        success = run_command(cmd)
        if success:
            print("\n✅ 覆盖率报告已生成: htmlcov/index.html")
    
    # 返回结果
    if success:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
