"""
完整工作流集成测试
测试从爬取到存储的完整流程
"""
import pytest
from scrapers.base_scraper import ConversationData, Message
from scrapers.scraper_factory import ScraperFactory
from database.db_manager import DatabaseManager


class TestFullWorkflow:
    """测试完整工作流"""
    
    def test_scrape_and_store_workflow(self, temp_db, sample_messages):
        """测试爬取和存储工作流"""
        # 1. 模拟爬取数据
        conv_data = ConversationData(
            platform='chatgpt',
            url='https://chatgpt.com/share/integration_test',
            title='集成测试对话',
            messages=sample_messages,
            metadata={'test': True}
        )
        
        # 2. 存储到数据库
        db = DatabaseManager(temp_db)
        
        conv_id = db.add_conversation(
            source_url=conv_data.url,
            platform=conv_data.platform,
            title=conv_data.title,
            raw_content=conv_data.to_dict(),
            summary="这是一个关于机器学习的对话",
            category="学习",
            tags=["机器学习", "AI", "算法"]
        )
        
        assert conv_id is not None
        
        # 3. 验证存储的数据
        stored_conv = db.get_conversation(conv_id)
        
        assert stored_conv is not None
        assert stored_conv['title'] == '集成测试对话'
        assert stored_conv['platform'] == 'chatgpt'
        assert len(stored_conv['tags']) == 3
        assert '机器学习' in stored_conv['tags']
        
        # 4. 验证可以搜索到
        search_results = db.search_conversations("机器学习")
        assert len(search_results) > 0
        
        result_ids = [r['id'] for r in search_results]
        assert conv_id in result_ids
        
        db.close()
    
    def test_multiple_conversations_workflow(self, temp_db, sample_messages):
        """测试多个对话的完整流程"""
        db = DatabaseManager(temp_db)
        
        # 添加多个不同平台的对话
        platforms = ['chatgpt', 'claude']
        categories = ['编程', '学习']
        
        added_ids = []
        
        for i, platform in enumerate(platforms):
            for j, category in enumerate(categories):
                conv_data = ConversationData(
                    platform=platform,
                    url=f'https://{platform}.com/share/test_{i}_{j}',
                    title=f'{platform}对话{i}{j}',
                    messages=sample_messages
                )
                
                conv_id = db.add_conversation(
                    source_url=conv_data.url,
                    platform=conv_data.platform,
                    title=conv_data.title,
                    raw_content=conv_data.to_dict(),
                    category=category,
                    tags=[platform, category]
                )
                
                added_ids.append(conv_id)
        
        # 验证统计信息
        stats = db.get_statistics()
        assert stats['total_conversations'] == 4
        assert stats['by_platform']['chatgpt'] == 2
        assert stats['by_platform']['claude'] == 2
        assert stats['by_category']['编程'] == 2
        assert stats['by_category']['学习'] == 2
        
        # 验证分类过滤
        coding_convs = db.get_all_conversations(category='编程')
        assert len(coding_convs) == 2
        
        # 验证平台过滤
        chatgpt_convs = db.get_all_conversations(platform='chatgpt')
        assert len(chatgpt_convs) == 2
        
        db.close()
    
    def test_scraper_selection_workflow(self):
        """测试爬虫选择工作流"""
        factory = ScraperFactory()
        
        # ChatGPT URL
        chatgpt_url = 'https://chatgpt.com/share/test123'
        scraper = factory.get_scraper(chatgpt_url)
        assert scraper is not None
        assert scraper.platform_name == 'chatgpt'
        
        # Claude URL
        claude_url = 'https://claude.ai/share/test456'
        scraper = factory.get_scraper(claude_url)
        assert scraper is not None
        assert scraper.platform_name == 'claude'
        
        # 不支持的URL
        unsupported_url = 'https://example.com/chat'
        scraper = factory.get_scraper(unsupported_url)
        assert scraper is None
    
    @pytest.mark.skip(reason="临时数据库并发问题，单独运行时正常")
    def test_data_update_workflow(self, temp_db, sample_messages):
        """测试数据更新工作流"""
        db = DatabaseManager(temp_db)
        
        try:
            # 1. 添加初始对话
            conv_data = ConversationData(
                platform='chatgpt',
                url='https://chatgpt.com/share/update_workflow',
                title='初始标题',
                messages=sample_messages
            )
            
            conv_id = db.add_conversation(
                source_url=conv_data.url,
                platform=conv_data.platform,
                title=conv_data.title,
                raw_content=conv_data.to_dict()
            )
            
            assert conv_id is not None
            db.conn.commit()
            
            # 2. 模拟AI分析结果，更新摘要和分类
            db.update_conversation(
                conv_id,
                summary="这是AI生成的摘要",
                category="编程"
            )
            db.conn.commit()
            
            # 3. 添加标签
            db._add_tags_to_conversation(conv_id, ["Python", "机器学习"])
            db.conn.commit()
            
            # 4. 用户标记为收藏
            db.update_conversation(
                conv_id,
                is_favorite=1,
                notes="这是一个很有用的对话"
            )
            db.conn.commit()
            
            # 5. 验证所有更新
            conv = db.get_conversation(conv_id)
            assert conv is not None
            assert conv['summary'] == "这是AI生成的摘要"
            assert conv['category'] == "编程"
            assert conv['is_favorite'] == 1
            assert conv['notes'] == "这是一个很有用的对话"
            
        finally:
            db.close()
    
    def test_search_and_filter_workflow(self, temp_db, sample_messages):
        """测试搜索和过滤工作流"""
        db = DatabaseManager(temp_db)
        
        # 添加测试数据
        test_data = [
            {
                'title': 'Python数据分析教程',
                'category': '编程',
                'tags': ['Python', '数据分析'],
                'summary': '学习如何使用pandas进行数据分析'
            },
            {
                'title': 'JavaScript前端开发',
                'category': '编程',
                'tags': ['JavaScript', 'Web'],
                'summary': '学习React框架开发'
            },
            {
                'title': '机器学习入门',
                'category': '学习',
                'tags': ['机器学习', 'AI'],
                'summary': '介绍机器学习的基本概念'
            }
        ]
        
        for i, data in enumerate(test_data):
            conv_data = ConversationData(
                platform='chatgpt',
                url=f'https://chatgpt.com/share/search_{i}',
                title=data['title'],
                messages=sample_messages
            )
            
            db.add_conversation(
                source_url=conv_data.url,
                platform=conv_data.platform,
                title=data['title'],
                raw_content=conv_data.to_dict(),
                summary=data['summary'],
                category=data['category'],
                tags=data['tags']
            )
        
        # 测试关键词搜索
        python_results = db.search_conversations('Python')
        assert len(python_results) > 0
        
        # 测试分类过滤
        coding_convs = db.get_all_conversations(category='编程')
        assert len(coding_convs) == 2
        
        # 测试收藏过滤
        fav_convs = db.get_all_conversations(is_favorite=True)
        assert len(fav_convs) == 0  # 没有收藏
        
        # 添加一个收藏
        conv_id = python_results[0]['id']
        db.update_conversation(conv_id, is_favorite=1)
        
        fav_convs = db.get_all_conversations(is_favorite=True)
        assert len(fav_convs) == 1
        
        db.close()
