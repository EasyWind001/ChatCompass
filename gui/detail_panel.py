"""
DetailPanel - 对话详情面板

显示选中对话的详细信息
"""
from typing import Optional, Dict, Any
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt


class DetailPanel(QWidget):
    """对话详情面板"""
    
    def __init__(self, db, parent=None):
        """
        初始化详情面板
        
        Args:
            db: 数据库连接
            parent: 父窗口
        """
        super().__init__(parent)
        self.db = db
        self.current_conversation = None
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 内容窗口
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 基本信息组
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        self.title_label = QLabel("标题: -")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        info_layout.addWidget(self.title_label)
        
        self.url_label = QLabel("链接: -")
        self.url_label.setWordWrap(True)
        self.url_label.setOpenExternalLinks(True)
        info_layout.addWidget(self.url_label)
        
        self.platform_label = QLabel("平台: -")
        info_layout.addWidget(self.platform_label)
        
        self.time_label = QLabel("时间: -")
        info_layout.addWidget(self.time_label)
        
        content_layout.addWidget(info_group)
        
        # 统计信息组
        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout(stats_group)
        
        self.message_count_label = QLabel("消息数: -")
        stats_layout.addWidget(self.message_count_label)
        
        self.category_label = QLabel("分类: -")
        stats_layout.addWidget(self.category_label)
        
        self.tags_label = QLabel("标签: -")
        self.tags_label.setWordWrap(True)
        stats_layout.addWidget(self.tags_label)
        
        content_layout.addWidget(stats_group)
        
        # 摘要组
        summary_group = QGroupBox("摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(100)
        summary_layout.addWidget(self.summary_text)
        
        content_layout.addWidget(summary_group)
        
        # 对话内容组
        content_group = QGroupBox("对话内容")
        content_content_layout = QVBoxLayout(content_group)
        
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        content_content_layout.addWidget(self.content_text)
        
        content_layout.addWidget(content_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("导出")
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
    def show_conversation(self, conversation_id: int):
        """
        显示对话详情
        
        Args:
            conversation_id: 对话ID
        """
        try:
            # 获取对话数据
            conversation = self.db.get_conversation(conversation_id)
            if not conversation:
                self._clear()
                return
                
            self.current_conversation = conversation
            
            # 更新基本信息
            title = conversation.get('title', 'Untitled')
            self.title_label.setText(f"标题: {title}")
            
            url = conversation.get('source_url', '-')
            if url and url != '-':
                self.url_label.setText(f'链接: <a href="{url}">{url}</a>')
            else:
                self.url_label.setText("链接: -")
                
            platform = conversation.get('platform', 'unknown')
            self.platform_label.setText(f"平台: {platform}")
            
            created_at = conversation.get('created_at', '-')
            self.time_label.setText(f"时间: {created_at}")
            
            # 更新统计信息
            # 解析raw_content获取消息数
            raw_content = conversation.get('raw_content', '{}')
            try:
                content_data = json.loads(raw_content)
                messages = content_data.get('messages', [])
                message_count = len(messages)
            except:
                message_count = 0
                
            self.message_count_label.setText(f"消息数: {message_count} 条")
            
            category = conversation.get('category') or '-'
            self.category_label.setText(f"分类: {category}")
            
            tags = conversation.get('tags', '')
            if tags:
                self.tags_label.setText(f"标签: {tags}")
            else:
                self.tags_label.setText("标签: -")
                
            # 更新摘要
            summary = conversation.get('summary') or '(无摘要)'
            self.summary_text.setPlainText(summary)
            
            # 更新对话内容
            self._load_conversation_content(raw_content)
            
            # 启用操作按钮
            self.export_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
        except Exception as e:
            self._clear()
            self.content_text.setPlainText(f"加载失败: {str(e)}")
            
    def _load_conversation_content(self, raw_content: str):
        """
        加载对话内容
        
        Args:
            raw_content: 原始对话JSON
        """
        try:
            content_data = json.loads(raw_content)
            messages = content_data.get('messages', [])
            
            html_parts = []
            for idx, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                # 角色标识
                if role == 'user':
                    role_text = f'<b style="color: #0066cc;">👤 用户 (消息 {idx}/{len(messages)})</b>'
                elif role == 'assistant':
                    role_text = f'<b style="color: #10a37f;">🤖 助手 (消息 {idx}/{len(messages)})</b>'
                else:
                    role_text = f'<b>📝 {role} (消息 {idx}/{len(messages)})</b>'
                    
                # 内容
                content_html = content.replace('\n', '<br>')
                
                html_parts.append(f"""
                <div style="margin-bottom: 20px; padding: 10px; border-left: 3px solid #ccc;">
                    {role_text}<br>
                    <div style="margin-top: 5px;">{content_html}</div>
                </div>
                """)
                
            full_html = "".join(html_parts)
            self.content_text.setHtml(full_html)
            
        except Exception as e:
            self.content_text.setPlainText(f"解析对话内容失败: {str(e)}")
            
    def _clear(self):
        """清空显示"""
        self.current_conversation = None
        
        self.title_label.setText("标题: -")
        self.url_label.setText("链接: -")
        self.platform_label.setText("平台: -")
        self.time_label.setText("时间: -")
        
        self.message_count_label.setText("消息数: -")
        self.category_label.setText("分类: -")
        self.tags_label.setText("标签: -")
        
        self.summary_text.clear()
        self.content_text.clear()
        
        self.export_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
