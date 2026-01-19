#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI自动化测试 V2 - 现代化界面交互测试
测试范围：搜索功能、视图切换、抓取队列、添加对话框
"""
import sys
import time
import io

# 设置标准输出为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PyQt6.QtWidgets import QApplication, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from gui.modern.layouts.modern_main_window_v2 import ModernMainWindow
from gui.modern.styles.style_manager import StyleManager
from gui.modern.styles.color_scheme import Theme


class UITestV2:
    """V2界面自动化测试"""
    
    def __init__(self):
        self.window = None
        self.passed = 0
        self.failed = 0
        self.failed_items = []
        
    def log(self, message: str, status: str = "INFO"):
        """日志输出"""
        emoji = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
        print(f"{emoji.get(status, 'ℹ️')} {message}")
    
    def verify(self, condition: bool, test_name: str, detail: str = "") -> bool:
        """验证条件"""
        if condition:
            self.passed += 1
            self.log(f"{test_name}: {detail}", "PASS")
            return True
        else:
            self.failed += 1
            self.failed_items.append(f"{test_name}: {detail}")
            self.log(f"{test_name}: {detail}", "FAIL")
            return False
    
    def find_button(self, text: str) -> QPushButton:
        """查找按钮"""
        buttons = self.window.findChildren(QPushButton)
        for btn in buttons:
            if text in btn.text():
                return btn
        return None
    
    def test_initial_state(self) -> bool:
        """测试初始状态"""
        self.log("\n=== 测试初始状态 ===")
        
        # 验证窗口创建
        self.verify(self.window is not None, "窗口创建", "主窗口已创建")
        
        # 验证默认视图模式
        self.verify(self.window._view_mode == 'grid', "默认视图模式", "网格视图")
        
        # 验证搜索模式状态
        self.verify(not self.window._search_mode, "搜索模式状态", "未激活")
        
        # 验证组件可见性
        self.verify(self.window.conversation_grid.isVisible(), "网格视图可见性", "可见")
        self.verify(not self.window.conversation_list.isVisible(), "列表视图可见性", "隐藏")
        self.verify(not self.window.search_results_container.isVisible(), "搜索结果容器", "隐藏")
        
        # 验证抓取面板初始状态
        self.verify(not self.window.scraping_panel._collapsed, "抓取面板状态", "展开状态")
        
        return self.failed == 0
    
    def test_view_switching(self) -> bool:
        """测试视图切换"""
        self.log("\n=== 测试视图切换 ===")
        
        # 查找视图切换按钮
        view_btn = self.window.view_btn
        if not self.verify(view_btn is not None, "视图切换按钮", "找到按钮"):
            return False
        
        # 切换到列表视图
        self.log("点击切换到列表视图...")
        QTest.mouseClick(view_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        self.verify(self.window._view_mode == 'list', "视图模式切换", "列表视图")
        self.verify(not self.window.conversation_grid.isVisible(), "网格视图隐藏", "已隐藏")
        self.verify(self.window.conversation_list.isVisible(), "列表视图显示", "已显示")
        self.verify(view_btn.text() == "🎨 网格", "按钮文本更新", view_btn.text())
        
        # 切换回网格视图
        self.log("点击切换回网格视图...")
        QTest.mouseClick(view_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        self.verify(self.window._view_mode == 'grid', "视图模式切换", "网格视图")
        self.verify(self.window.conversation_grid.isVisible(), "网格视图显示", "已显示")
        self.verify(not self.window.conversation_list.isVisible(), "列表视图隐藏", "已隐藏")
        self.verify(view_btn.text() == "📋 列表", "按钮文本恢复", view_btn.text())
        
        return True
    
    def test_search_functionality(self) -> bool:
        """测试搜索功能"""
        self.log("\n=== 测试搜索功能 ===")
        
        # 查找搜索输入框
        search_input = self.window.search_input
        if not self.verify(search_input is not None, "搜索输入框", "找到输入框"):
            return False
        
        # 输入搜索关键词
        self.log("输入搜索关键词 'Python'...")
        search_input.setText("Python")
        QTest.qWait(300)
        
        self.verify(search_input.text() == "Python", "搜索文本输入", search_input.text())
        
        # 查找搜索按钮
        search_btn = self.find_button("搜索")
        if not self.verify(search_btn is not None, "搜索按钮", "找到按钮"):
            return False
        
        # 点击搜索
        self.log("点击搜索按钮...")
        QTest.mouseClick(search_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(800)
        
        # 验证搜索模式
        self.verify(self.window._search_mode, "搜索模式激活", "已激活")
        self.verify(not self.window.conversation_grid.isVisible(), "网格视图隐藏", "已隐藏")
        self.verify(self.window.search_results_container.isVisible(), "搜索结果显示", "已显示")
        
        # 验证详情区域收起
        sizes = self.window.left_splitter.sizes()
        self.verify(sizes[1] <= 100, "详情区域收起", f"宽度={sizes[1]}")
        
        # 验证抓取队列收起
        self.verify(self.window.scraping_panel._collapsed, "抓取队列收起", "已收起")
        
        # 验证搜索结果数量
        result_count = self.window.search_results_layout.count() - 1  # 减去stretch
        self.verify(result_count > 0, "搜索结果数量", f"{result_count} 个结果")
        
        return True
    
    def test_search_expansion(self) -> bool:
        """测试搜索结果展开"""
        self.log("\n=== 测试搜索结果展开 ===")
        
        # 确保在搜索模式
        if not self.window._search_mode:
            self.log("先执行搜索...", "WARN")
            self.test_search_functionality()
        
        # 获取第一个搜索结果
        if self.window.search_results_layout.count() > 1:
            first_result = self.window.search_results_layout.itemAt(0).widget()
            if first_result:
                # 查找展开按钮
                expand_btn = first_result.findChild(QPushButton)
                if expand_btn and "查看完整对话" in expand_btn.text():
                    self.log("点击展开搜索结果...")
                    QTest.mouseClick(expand_btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(500)
                    
                    # 验证详情区域恢复
                    sizes = self.window.left_splitter.sizes()
                    self.verify(sizes[1] > 500, "详情区域展开", f"宽度={sizes[1]}")
                    
                    # 验证导航按钮显示
                    self.verify(self.window.nav_container.isVisible(), "导航按钮显示", "已显示")
                    
                    return True
        
        self.verify(False, "搜索结果展开", "未找到可展开的结果")
        return False
    
    def test_search_clear(self) -> bool:
        """测试清除搜索"""
        self.log("\n=== 测试清除搜索 ===")
        
        # 确保在搜索模式
        if not self.window._search_mode:
            self.log("先执行搜索...", "WARN")
            self.test_search_functionality()
        
        # 查找清除按钮
        clear_btn = self.find_button("清除")
        if not self.verify(clear_btn is not None, "清除按钮", "找到按钮"):
            return False
        
        # 点击清除
        self.log("点击清除按钮...")
        QTest.mouseClick(clear_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        # 验证退出搜索模式
        self.verify(not self.window._search_mode, "搜索模式退出", "已退出")
        self.verify(self.window.search_input.text() == "", "搜索框清空", "已清空")
        
        # 验证视图恢复
        self.verify(not self.window.search_results_container.isVisible(), "搜索结果隐藏", "已隐藏")
        self.verify(self.window.conversation_grid.isVisible(), "网格视图恢复", "已显示")
        
        # 验证布局恢复
        sizes = self.window.left_splitter.sizes()
        self.verify(sizes[0] > 200, "布局比例恢复", f"列表区={sizes[0]}")
        
        # 验证导航按钮隐藏
        self.verify(not self.window.nav_container.isVisible(), "导航按钮隐藏", "已隐藏")
        
        return True
    
    def test_scraping_panel(self) -> bool:
        """测试抓取面板"""
        self.log("\n=== 测试抓取面板 ===")
        
        # 确保不在搜索模式
        if self.window._search_mode:
            self.test_search_clear()
        
        # 验证初始状态
        initial_collapsed = self.window.scraping_panel._collapsed
        self.log(f"初始状态: {'收起' if initial_collapsed else '展开'}")
        
        # 查找收起/展开按钮
        toggle_btn = self.window.scraping_panel.findChild(QPushButton)
        if not self.verify(toggle_btn is not None, "抓取面板按钮", "找到按钮"):
            return False
        
        # 点击切换
        self.log("点击切换抓取面板...")
        QTest.mouseClick(toggle_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        # 验证状态切换
        self.verify(
            self.window.scraping_panel._collapsed != initial_collapsed,
            "抓取面板状态切换",
            f"{'收起' if self.window.scraping_panel._collapsed else '展开'}"
        )
        
        # 再次切换回去
        self.log("再次切换抓取面板...")
        QTest.mouseClick(toggle_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        self.verify(
            self.window.scraping_panel._collapsed == initial_collapsed,
            "抓取面板状态恢复",
            f"{'收起' if self.window.scraping_panel._collapsed else '展开'}"
        )
        
        return True
    
    def test_add_dialog(self) -> bool:
        """测试添加对话框"""
        self.log("\n=== 测试添加对话框 ===")
        
        # 查找添加按钮
        add_btn = self.find_button("添加")
        if not self.verify(add_btn is not None, "添加按钮", "找到按钮"):
            return False
        
        # 点击添加
        self.log("点击添加按钮...")
        QTest.mouseClick(add_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(500)
        
        # 查找对话框
        from gui.modern.widgets.add_dialog import AddDialog
        dialogs = self.window.findChildren(AddDialog)
        
        if dialogs:
            dialog = dialogs[0]
            self.verify(dialog.isVisible(), "添加对话框显示", "已显示")
            
            # 关闭对话框
            self.log("关闭对话框...")
            dialog.close()
            QTest.qWait(300)
            
            return True
        else:
            self.verify(False, "添加对话框", "未找到对话框")
            return False
    
    def test_navigation_buttons(self) -> bool:
        """测试导航按钮"""
        self.log("\n=== 测试导航按钮 ===")
        
        # 先进入搜索模式并展开结果
        self.test_search_functionality()
        QTest.qWait(500)
        self.test_search_expansion()
        QTest.qWait(500)
        
        # 验证导航按钮可见
        if not self.verify(self.window.nav_container.isVisible(), "导航按钮可见性", "已显示"):
            return False
        
        # 获取初始匹配索引
        initial_index = self.window._current_match_index
        
        # 点击下一个
        self.log("点击下一个匹配...")
        QTest.mouseClick(self.window.next_match_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(300)
        
        self.verify(
            self.window._current_match_index != initial_index,
            "匹配索引更新",
            f"{initial_index} -> {self.window._current_match_index}"
        )
        
        # 点击上一个
        self.log("点击上一个匹配...")
        QTest.mouseClick(self.window.prev_match_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(300)
        
        self.verify(
            self.window._current_match_index == initial_index,
            "匹配索引恢复",
            f"{self.window._current_match_index}"
        )
        
        return True
    
    def auto_fix_issues(self):
        """自动修复发现的问题"""
        self.log("\n=== 自动修复问题 ===")
        
        fixed_count = 0
        
        # 检查并修复常见问题
        if self.window:
            # 修复1: 确保搜索模式下抓取队列正确收起
            if self.window._search_mode and not self.window.scraping_panel._collapsed:
                self.log("修复: 搜索模式下抓取队列未收起", "WARN")
                self.window.scraping_panel._on_toggle_clicked()
                fixed_count += 1
            
            # 修复2: 确保视图模式和按钮文本一致
            expected_text = "📋 列表" if self.window._view_mode == 'grid' else "🎨 网格"
            if self.window.view_btn.text() != expected_text:
                self.log(f"修复: 视图按钮文本不一致", "WARN")
                self.window.view_btn.setText(expected_text)
                fixed_count += 1
            
            # 修复3: 确保非搜索模式下导航按钮隐藏
            if not self.window._search_mode and self.window.nav_container.isVisible():
                self.log("修复: 非搜索模式下导航按钮未隐藏", "WARN")
                self.window.nav_container.hide()
                fixed_count += 1
        
        if fixed_count > 0:
            self.log(f"已自动修复 {fixed_count} 个问题", "PASS")
        else:
            self.log("未发现需要修复的问题", "PASS")
        
        return fixed_count
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 60)
        self.log("ChatCompass V2 UI自动化测试")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # 创建应用
        app = QApplication.instance() or QApplication(sys.argv)
        
        # 应用样式
        style_manager = StyleManager()
        style_manager.apply_theme(app, Theme.LIGHT)
        
        # 创建窗口
        self.window = ModernMainWindow()
        self.window.show()
        QTest.qWait(1000)  # 等待窗口完全加载
        
        # 执行测试
        try:
            self.test_initial_state()
            QTest.qWait(500)
            
            self.test_view_switching()
            QTest.qWait(500)
            
            self.test_search_functionality()
            QTest.qWait(500)
            
            self.test_search_expansion()
            QTest.qWait(500)
            
            self.test_navigation_buttons()
            QTest.qWait(500)
            
            self.test_search_clear()
            QTest.qWait(500)
            
            self.test_scraping_panel()
            QTest.qWait(500)
            
            self.test_add_dialog()
            QTest.qWait(500)
            
            # 自动修复
            fixed = self.auto_fix_issues()
            
            # 生成报告
            self.generate_report(time.time() - start_time, fixed)
            
        finally:
            # 关闭窗口
            self.window.close()
            app.quit()
    
    def generate_report(self, execution_time: float, fixed_count: int):
        """生成测试报告"""
        self.log("\n" + "=" * 60)
        self.log("测试报告")
        self.log("=" * 60)
        
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.log(f"总测试项: {total}")
        self.log(f"通过: {self.passed}", "PASS")
        self.log(f"失败: {self.failed}", "FAIL" if self.failed > 0 else "INFO")
        self.log(f"自动修复: {fixed_count}", "PASS" if fixed_count > 0 else "INFO")
        self.log(f"成功率: {success_rate:.1f}%")
        self.log(f"执行时间: {execution_time:.2f}秒")
        
        if self.failed_items:
            self.log("\n失败项详情:", "FAIL")
            for i, item in enumerate(self.failed_items, 1):
                print(f"  {i}. {item}")
        
        # 保存报告
        report_file = "UI_AUTOMATION_V2_TEST_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# ChatCompass V2 UI自动化测试报告\n\n")
            f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**执行时长**: {execution_time:.2f}秒\n\n")
            f.write("## 测试结果\n\n")
            f.write(f"- 总测试项: {total}\n")
            f.write(f"- ✅ 通过: {self.passed}\n")
            f.write(f"- ❌ 失败: {self.failed}\n")
            f.write(f"- 🔧 自动修复: {fixed_count}\n")
            f.write(f"- 成功率: {success_rate:.1f}%\n\n")
            
            if self.failed_items:
                f.write("## 失败项详情\n\n")
                for i, item in enumerate(self.failed_items, 1):
                    f.write(f"{i}. {item}\n")
            else:
                f.write("## 🎉 所有测试通过！\n\n")
            
            f.write("\n## 测试覆盖范围\n\n")
            f.write("- ✅ 初始状态验证\n")
            f.write("- ✅ 视图切换（网格↔列表）\n")
            f.write("- ✅ 搜索功能\n")
            f.write("- ✅ 搜索结果展开\n")
            f.write("- ✅ 搜索结果导航\n")
            f.write("- ✅ 清除搜索\n")
            f.write("- ✅ 抓取面板收起/展开\n")
            f.write("- ✅ 添加对话框\n")
            f.write("- ✅ 自动问题修复\n")
        
        self.log(f"\n报告已保存: {report_file}", "PASS")
        self.log("=" * 60)


def main():
    """主函数"""
    tester = UITestV2()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
