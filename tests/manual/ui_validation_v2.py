#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2界面快速验证脚本 - 检查代码一致性和潜在问题
"""
import sys
import os
import io

# 设置标准输出为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_file_exists(filepath: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(filepath)

def validate_v2_structure():
    """验证V2代码结构"""
    print("=" * 60)
    print("ChatCompass V2 代码结构验证")
    print("=" * 60)
    
    issues = []
    
    # 检查核心文件
    core_files = {
        "主窗口V2": "gui/modern/layouts/modern_main_window_v2.py",
        "样式管理器": "gui/modern/styles/style_manager.py",
        "颜色方案": "gui/modern/styles/color_scheme.py",
        "对话网格": "gui/modern/widgets/conversation_grid.py",
        "对话列表": "gui/modern/widgets/conversation_list.py",
        "搜索结果项": "gui/modern/widgets/search_result_item.py",
        "抓取状态面板": "gui/modern/widgets/scraping_status_panel.py",
        "添加对话框": "gui/modern/widgets/add_dialog.py",
    }
    
    print("\n检查核心文件:")
    for name, path in core_files.items():
        if check_file_exists(path):
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: {path} (缺失)")
            issues.append(f"缺失文件: {path}")
    
    # 检查V2主窗口代码
    print("\n检查V2主窗口代码:")
    v2_file = "gui/modern/layouts/modern_main_window_v2.py"
    if check_file_exists(v2_file):
        with open(v2_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查关键方法
            required_methods = [
                "_create_title_bar",
                "_create_search_bar",
                "_create_search_results_container",
                "_create_detail_panel",
                "_perform_search",
                "_clear_search",
                "_on_view_toggle",
                "_on_conversation_selected",
                "_on_add_clicked",
                "_prev_match",
                "_next_match",
            ]
            
            for method in required_methods:
                if f"def {method}" in content:
                    print(f"  ✅ 方法: {method}")
                else:
                    print(f"  ❌ 方法: {method} (缺失)")
                    issues.append(f"缺失方法: {method}")
            
            # 检查关键属性
            required_attrs = [
                "_view_mode",
                "_search_mode",
                "_search_expanded",
                "_search_results",
                "_current_matches",
                "_current_match_index",
            ]
            
            print("\n检查关键属性:")
            for attr in required_attrs:
                if f"self.{attr}" in content:
                    print(f"  ✅ 属性: {attr}")
                else:
                    print(f"  ❌ 属性: {attr} (缺失)")
                    issues.append(f"缺失属性: {attr}")
            
            # 检查组件
            required_components = [
                "conversation_grid",
                "conversation_list",
                "search_results_container",
                "search_input",
                "detail_panel",
                "scraping_panel",
                "nav_container",
            ]
            
            print("\n检查UI组件:")
            for comp in required_components:
                if f"self.{comp}" in content:
                    print(f"  ✅ 组件: {comp}")
                else:
                    print(f"  ❌ 组件: {comp} (缺失)")
                    issues.append(f"缺失组件: {comp}")
    
    # 检查测试文件
    print("\n检查测试文件:")
    test_file = "test_modern_ui_v2.py"
    if check_file_exists(test_file):
        print(f"  ✅ V2测试入口: {test_file}")
    else:
        print(f"  ❌ V2测试入口: {test_file} (缺失)")
        issues.append(f"缺失测试文件: {test_file}")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("验证报告")
    print("=" * 60)
    
    if not issues:
        print("✅ 所有检查通过！V2代码结构完整。")
        return True
    else:
        print(f"❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False

def check_code_quality():
    """检查代码质量问题"""
    print("\n" + "=" * 60)
    print("代码质量检查")
    print("=" * 60)
    
    v2_file = "gui/modern/layouts/modern_main_window_v2.py"
    if not check_file_exists(v2_file):
        print("❌ V2文件不存在，跳过检查")
        return
    
    with open(v2_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    # 检查搜索模式下的布局逻辑
    print("\n检查搜索模式布局逻辑:")
    search_logic_found = False
    for i, line in enumerate(lines, 1):
        if "_perform_search" in line and "def" in line:
            search_logic_found = True
            # 检查后续行是否有正确的布局设置
            chunk = "".join(lines[i:min(i+30, len(lines))])
            if "setSizes" in chunk:
                print(f"  ✅ 第{i}行: 搜索模式布局调整逻辑存在")
            else:
                print(f"  ⚠️  第{i}行: 搜索模式可能缺少布局调整")
                issues.append(f"第{i}行: _perform_search可能缺少布局调整")
    
    if not search_logic_found:
        print("  ❌ 未找到_perform_search方法")
        issues.append("未找到_perform_search方法")
    
    # 检查清除搜索的布局恢复
    print("\n检查清除搜索恢复逻辑:")
    clear_logic_found = False
    for i, line in enumerate(lines, 1):
        if "_clear_search" in line and "def" in line:
            clear_logic_found = True
            chunk = "".join(lines[i:min(i+30, len(lines))])
            if "setSizes" in chunk and "show()" in chunk:
                print(f"  ✅ 第{i}行: 清除搜索恢复逻辑存在")
            else:
                print(f"  ⚠️  第{i}行: 清除搜索可能缺少完整恢复逻辑")
                issues.append(f"第{i}行: _clear_search可能缺少完整恢复")
    
    if not clear_logic_found:
        print("  ❌ 未找到_clear_search方法")
        issues.append("未找到_clear_search方法")
    
    # 检查视图切换逻辑
    print("\n检查视图切换逻辑:")
    toggle_logic_found = False
    for i, line in enumerate(lines, 1):
        if "_on_view_toggle" in line and "def" in line:
            toggle_logic_found = True
            chunk = "".join(lines[i:min(i+30, len(lines))])
            if "_search_mode" in chunk:
                print(f"  ✅ 第{i}行: 视图切换检查搜索模式")
            else:
                print(f"  ⚠️  第{i}行: 视图切换可能未检查搜索模式")
                issues.append(f"第{i}行: _on_view_toggle应检查搜索模式")
    
    if not toggle_logic_found:
        print("  ❌ 未找到_on_view_toggle方法")
        issues.append("未找到_on_view_toggle方法")
    
    # 总结
    print("\n" + "=" * 60)
    if not issues:
        print("✅ 代码质量检查通过！")
        return True
    else:
        print(f"⚠️  发现 {len(issues)} 个潜在问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False

def suggest_improvements():
    """建议改进项"""
    print("\n" + "=" * 60)
    print("改进建议")
    print("=" * 60)
    
    suggestions = [
        "1. 添加键盘快捷键支持 (Ctrl+F 搜索, Esc 清除)",
        "2. 搜索结果高亮动画效果",
        "3. 抓取队列进度条动画",
        "4. 详情面板滚动位置记忆",
        "5. 搜索历史记录",
        "6. 导出搜索结果功能",
        "7. 批量操作支持（批量删除、批量导出）",
        "8. 响应式布局适配不同屏幕尺寸",
    ]
    
    for suggestion in suggestions:
        print(f"  💡 {suggestion}")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print("\n")
    
    # 结构验证
    structure_ok = validate_v2_structure()
    
    # 代码质量检查
    quality_ok = check_code_quality()
    
    # 改进建议
    suggest_improvements()
    
    # 最终结果
    print("\n" + "=" * 60)
    print("最终结果")
    print("=" * 60)
    
    if structure_ok and quality_ok:
        print("✅ V2代码验证通过！可以进行UI测试。")
        print("\n运行UI测试:")
        print("  python ui_automation_v2_test.py")
        print("\n或运行V2演示:")
        print("  python test_modern_ui_v2.py")
    else:
        print("⚠️  发现一些问题，建议先修复后再测试。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
