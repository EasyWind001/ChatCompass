"""
ChatCompass - AI对话知识库管理系统
主程序入口
"""
import sys
import os
from pathlib import Path

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.storage_adapter import StorageAdapter
from scrapers.scraper_factory import ScraperFactory
from config import get_storage, get_ai_service, STORAGE_TYPE


class ChatCompass:
    """主应用类"""
    
    def __init__(self):
        print("=" * 60)
        print("ChatCompass - AI对话知识库管理系统 v1.2.2")
        print("=" * 60)
        
        # 初始化存储（自动选择SQLite或Elasticsearch）
        print(f"\n[INFO] 初始化存储后端: {STORAGE_TYPE}")
        try:
            storage = get_storage()
            self.db = StorageAdapter(storage)
            print(f"[OK] 存储初始化成功: {storage.__class__.__name__}")
        except Exception as e:
            print(f"[ERROR] 存储初始化失败: {e}")
            raise
        
        # 初始化爬虫工厂
        self.scraper_factory = ScraperFactory()
        
        # 初始化AI服务（统一使用新的AIService）
        print(f"[INFO] 初始化AI服务...")
        try:
            self.ai_service = get_ai_service()
            
            # 检查AI服务状态
            if self.ai_service.is_available():
                status = self.ai_service.get_status()
                print(f"[OK] AI服务已就绪")
                print(f"    - 后端: {status['backend']}")
                print(f"    - 模型: {status.get('model', 'N/A')}")
            else:
                print(f"[WARN] AI服务不可用（将跳过AI分析）")
                self.ai_service = None
        except Exception as e:
            print(f"[WARN] AI服务初始化失败: {e}")
            self.ai_service = None
    
    def add_conversation_from_url(self, url: str):
        """从URL添加对话"""
        print(f"\n处理链接: {url}")
        
        try:
            # 1. 抓取对话内容
            print("  [1/3] 抓取对话内容...")
            conversation_data = self.scraper_factory.scrape(url)
            print(f"  [OK] 抓取成功: {conversation_data.title}")
            print(f"      - 消息数: {conversation_data.message_count}")
            print(f"      - 字数: {conversation_data.word_count}")
            
            # 2. AI分析
            summary = None
            category = None
            tags = []
            
            if self.ai_service:
                print("  [2/3] AI分析中...")
                try:
                    full_text = conversation_data.get_full_text()
                    
                    # 使用新的AI服务进行分析
                    analysis = self.ai_service.analyze_conversation(
                        full_text, 
                        conversation_data.title
                    )
                    
                    if analysis:
                        summary = analysis.summary
                        category = analysis.category
                        tags = analysis.tags
                        
                        print(f"  [OK] 分析完成")
                        print(f"      - 摘要: {summary[:50]}..." if summary else "      - 摘要: (空)")
                        print(f"      - 分类: {category}" if category else "      - 分类: (未分类)")
                        print(f"      - 标签: {', '.join(tags)}" if tags else "      - 标签: (无)")
                    else:
                        print(f"  [WARN] AI分析未返回结果")
                except Exception as e:
                    print(f"  [WARN] AI分析失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("  [2/3] 跳过AI分析（服务不可用）")
            
            # 3. 保存到数据库
            print("  [3/3] 保存到数据库...")
            conv_id = self.db.add_conversation(
                source_url=url,
                platform=conversation_data.platform,
                title=conversation_data.title,
                raw_content=conversation_data.to_dict(),
                summary=summary,
                category=category,
                tags=tags
            )
            
            print(f"  [OK] 保存成功 (ID: {conv_id})")
            return conv_id
            
        except Exception as e:
            print(f"  [ERROR] 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def search(self, keyword: str):
        """搜索对话（增强版：显示上下文定位）"""
        print(f"\n🔍 搜索: {keyword}")
        results = self.db.search_conversations(keyword, limit=10, context_size=80)
        
        if not results:
            print("  未找到结果")
            return
        
        print(f"  找到 {len(results)} 条结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"  [{i}] 📄 {result['title']}")
            print(f"      💬 平台: {result['platform']} | 📁 分类: {result.get('category', '未分类')}")
            
            tags = result.get('tags', [])
            if tags:
                print(f"      🏷️  标签: {', '.join(tags)}")
            
            # 显示匹配片段（带上下文）
            matches = result.get('matches', [])
            if matches:
                print(f"      📍 找到 {len(matches)} 处匹配:\n")
                
                # 最多显示前3个匹配
                for match_idx, match in enumerate(matches[:3], 1):
                    role_icon = "👤" if match['role'] == 'user' else "🤖"
                    role_name = "用户" if match['role'] == 'user' else "助手"
                    
                    print(f"         {role_icon} {role_name} (第 {match['message_index']}/{match['total_messages']} 条消息)")
                    
                    # 拼接上下文，高亮关键词
                    context = (
                        match['before_context'] + 
                        f"【{match['match_text']}】" + 
                        match['after_context']
                    )
                    
                    # 格式化输出（缩进处理）
                    print(f"         {context}")
                    print()
                
                if len(matches) > 3:
                    print(f"         ... 还有 {len(matches) - 3} 处匹配")
                    print()
            else:
                # 如果没有提取到matches，显示snippet
                print(f"      片段: {result.get('snippet', '')[:100]}...")
                print()
            
            print(f"      💡 输入 'show {result['id']}' 查看完整对话")
            print()
    
    def delete_conversation(self, identifier: str):
        """删除单个对话
        
        Args:
            identifier: 对话ID或URL
        """
        # 尝试作为ID查询
        conversation = self.db.get_conversation(identifier)
        
        # 如果未找到，尝试作为URL查询
        if not conversation:
            conversation = self.db.get_conversation_by_url(identifier)
        
        if not conversation:
            print(f"\n❌ 未找到对话: {identifier}")
            print("提示: 使用 'list' 命令查看所有对话")
            return False
        
        # 显示将要删除的对话信息
        print("\n" + "=" * 70)
        print(f"⚠️  确认删除对话")
        print("=" * 70)
        print(f"ID: {conversation['id']}")
        print(f"标题: {conversation['title']}")
        print(f"平台: {conversation['platform']}")
        print(f"创建时间: {conversation['created_at']}")
        
        # 询问确认
        try:
            confirm = input("\n确定删除吗？(yes/no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\n❌ 已取消删除")
            return False
        
        if confirm not in ['yes', 'y']:
            print("\n❌ 已取消删除")
            return False
        
        # 执行删除
        success = self.db.delete_conversation(conversation['id'])
        
        if success:
            print(f"\n✅ 删除成功: {conversation['title']}")
            return True
        else:
            print(f"\n❌ 删除失败")
            return False
    
    def show_statistics(self):
        """显示统计信息"""
        stats = self.db.get_statistics()
        
        print("\n" + "=" * 60)
        print("统计信息")
        print("=" * 60)
        print(f"总对话数: {stats['total_conversations']}")
        
        if stats['by_platform']:
            print("\n按平台:")
            for platform, count in stats['by_platform'].items():
                print(f"  - {platform}: {count}")
        
        if stats['by_category']:
            print("\n按分类:")
            for category, count in stats['by_category'].items():
                print(f"  - {category}: {count}")
        
        print(f"\n总标签数: {stats['total_tags']}")
        print("=" * 60)
    
    def show_conversation(self, identifier: str):
        """显示单个对话的详细内容
        
        Args:
            identifier: 对话ID或URL
        """
        import json
        
        # 尝试作为ID查询
        conversation = self.db.get_conversation(identifier)
        
        # 如果未找到，尝试作为URL查询
        if not conversation:
            conversation = self.db.get_conversation_by_url(identifier)
        
        if not conversation:
            print(f"\n未找到对话: {identifier}")
            print("提示: 使用 'list' 命令查看所有对话")
            return
        
        # 显示对话详情
        print("\n" + "=" * 70)
        print(f"对话详情 (ID: {conversation['id']})")
        print("=" * 70)
        
        # 基本信息
        print(f"\n📝 标题: {conversation['title']}")
        print(f"🔗 链接: {conversation['source_url']}")
        print(f"💬 平台: {conversation['platform']}")
        print(f"📅 时间: {conversation['created_at']}")
        
        # 统计信息
        print(f"\n📊 统计:")
        print(f"  - 消息数: {conversation.get('message_count', 0)} 条")
        print(f"  - 字数: {conversation.get('word_count', 0)} 字")
        
        # 分类和标签
        if conversation.get('category'):
            print(f"  - 分类: {conversation['category']}")
        
        tags = self.db.get_conversation_tags(conversation['id'])
        if tags:
            print(f"  - 标签: {', '.join(tags)}")
        
        # 摘要
        if conversation.get('summary'):
            print(f"\n📄 摘要:")
            print(f"  {conversation['summary']}")
        
        # 备注
        if conversation.get('notes'):
            print(f"\n📌 备注:")
            print(f"  {conversation['notes']}")
        
        # 收藏状态
        if conversation.get('is_favorite'):
            print(f"\n⭐ 已收藏")
        
        # 对话内容
        print(f"\n💬 对话内容:")
        print("-" * 70)
        
        try:
            # raw_content可能是字符串或字典
            if isinstance(conversation['raw_content'], str):
                raw_content = json.loads(conversation['raw_content'])
            else:
                raw_content = conversation['raw_content']
            
            messages = raw_content.get('messages', [])
            
            if messages:
                for i, msg in enumerate(messages, 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    
                    # 角色图标
                    icon = "👤" if role == 'user' else "🤖"
                    role_name = "用户" if role == 'user' else "助手"
                    
                    print(f"\n{icon} {role_name} (消息 {i}/{len(messages)}):")
                    print(f"{content}")
                    
                    if i < len(messages):
                        print("-" * 70)
            else:
                print("（无消息内容）")
        
        except json.JSONDecodeError:
            print("（内容解析失败）")
        except Exception as e:
            print(f"（显示内容时出错: {e}）")
        
        print("\n" + "=" * 70)
    
    def interactive_mode(self):
        """交互式命令行模式"""
        print("\n进入交互模式（输入 'help' 查看帮助）\n")
        
        while True:
            try:
                command = input("ChatCompass> ").strip()
                
                if not command:
                    continue
                
                if command == 'help':
                    print("""
可用命令:
  add <url>        - 添加对话链接
  search <keyword> - 搜索对话
  list             - 列出最近的对话
  show <id|url>    - 查看对话详细内容
  delete <id|url>  - 删除对话（需要确认）
  stats            - 显示统计信息
  help             - 显示帮助
  exit             - 退出程序

示例:
  show 1                          - 查看ID为1的对话
  show 4                          - 查看ID为4的对话
  show https://chatgpt.com/...    - 通过URL查看对话
  delete 1                        - 删除ID为1的对话
  delete https://chatgpt.com/...  - 通过URL删除对话
                    """)
                
                elif command.startswith('add '):
                    url = command[4:].strip()
                    self.add_conversation_from_url(url)
                
                elif command.startswith('search '):
                    keyword = command[7:].strip()
                    self.search(keyword)
                
                elif command.startswith('show '):
                    identifier = command[5:].strip()
                    if identifier:
                        self.show_conversation(identifier)
                    else:
                        print("请指定对话ID或URL")
                        print("示例: show 1  或  show https://chatgpt.com/...")
                
                elif command.startswith('delete '):
                    identifier = command[7:].strip()
                    if identifier:
                        self.delete_conversation(identifier)
                    else:
                        print("请指定对话ID或URL")
                        print("示例: delete 1  或  delete https://chatgpt.com/...")
                
                elif command == 'list':
                    conversations = self.db.get_all_conversations(limit=10)
                    print(f"\n最近的 {len(conversations)} 条对话:\n")
                    for i, conv in enumerate(conversations, 1):
                        print(f"  [{conv['id']}] {conv['title']}")
                        print(f"      平台: {conv['platform']} | 时间: {conv['created_at']}")
                        print(f"      提示: 输入 'show {conv['id']}' 查看详情")
                        print()
                
                elif command == 'stats':
                    self.show_statistics()
                
                elif command in ['exit', 'quit']:
                    print("再见！")
                    break
                
                else:
                    print(f"未知命令: {command}（输入 'help' 查看帮助）")
            
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def close(self):
        """关闭资源"""
        if self.db:
            self.db.close()


def main():
    """主函数"""
    app = ChatCompass()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'add' and len(sys.argv) > 2:
            url = sys.argv[2]
            app.add_conversation_from_url(url)
        
        elif command == 'search' and len(sys.argv) > 2:
            keyword = ' '.join(sys.argv[2:])
            app.search(keyword)
        
        elif command == 'show' and len(sys.argv) > 2:
            identifier = sys.argv[2]
            app.show_conversation(identifier)
        
        elif command == 'delete' and len(sys.argv) > 2:
            identifier = sys.argv[2]
            app.delete_conversation(identifier)
        
        elif command == 'stats':
            app.show_statistics()
        
        elif command == 'gui':
            print("GUI模式开发中...")
            # TODO: 启动PyQt6 GUI
        
        else:
            print(f"用法: python main.py [add <url> | search <keyword> | show <id|url> | delete <id|url> | stats | gui]")
    
    else:
        # 无参数时进入交互模式
        app.interactive_mode()
    
    app.close()


if __name__ == '__main__':
    main()
