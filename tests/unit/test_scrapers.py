"""
爬虫模块单元测试
"""
import pytest
from scrapers.base_scraper import BaseScraper, ConversationData, Message
from scrapers.chatgpt_scraper import ChatGPTScraper
from scrapers.claude_scraper import ClaudeScraper
from scrapers.scraper_factory import ScraperFactory


class TestMessage:
    """测试Message数据类"""
    
    def test_message_creation(self):
        """测试创建消息"""
        msg = Message(role='user', content='Hello', timestamp='2024-01-01')
        assert msg.role == 'user'
        assert msg.content == 'Hello'
        assert msg.timestamp == '2024-01-01'
    
    def test_message_to_dict(self):
        """测试消息转字典"""
        msg = Message(role='assistant', content='Hi there')
        data = msg.to_dict()
        assert isinstance(data, dict)
        assert data['role'] == 'assistant'
        assert data['content'] == 'Hi there'


class TestConversationData:
    """测试ConversationData数据类"""
    
    def test_conversation_creation(self, sample_messages):
        """测试创建对话数据"""
        conv = ConversationData(
            platform='chatgpt',
            url='https://chatgpt.com/share/test',
            title='测试对话',
            messages=sample_messages
        )
        
        assert conv.platform == 'chatgpt'
        assert conv.url == 'https://chatgpt.com/share/test'
        assert conv.title == '测试对话'
        assert len(conv.messages) == 4
    
    def test_message_count(self, sample_messages):
        """测试消息计数"""
        conv = ConversationData(
            platform='chatgpt',
            url='https://test.com',
            title='测试',
            messages=sample_messages
        )
        assert conv.message_count == 4
    
    def test_word_count(self, sample_messages):
        """测试字数统计"""
        conv = ConversationData(
            platform='chatgpt',
            url='https://test.com',
            title='测试',
            messages=sample_messages
        )
        assert conv.word_count > 0
    
    def test_get_full_text(self, sample_messages):
        """测试获取完整文本"""
        conv = ConversationData(
            platform='chatgpt',
            url='https://test.com',
            title='测试',
            messages=sample_messages
        )
        
        full_text = conv.get_full_text()
        assert '用户:' in full_text
        assert '助手:' in full_text
        assert '机器学习' in full_text
    
    def test_to_dict(self, sample_messages):
        """测试转字典"""
        conv = ConversationData(
            platform='chatgpt',
            url='https://test.com',
            title='测试',
            messages=sample_messages,
            metadata={'key': 'value'}
        )
        
        data = conv.to_dict()
        assert isinstance(data, dict)
        assert data['platform'] == 'chatgpt'
        assert len(data['messages']) == 4
        assert data['metadata']['key'] == 'value'


class TestChatGPTScraper:
    """测试ChatGPT爬虫"""
    
    def test_can_handle_valid_urls(self):
        """测试识别有效URL"""
        scraper = ChatGPTScraper(use_playwright=False)
        
        valid_urls = [
            'https://chat.openai.com/share/abc123',
            'https://chatgpt.com/share/xyz-789',
            'http://chatgpt.com/share/test'
        ]
        
        for url in valid_urls:
            assert scraper.can_handle(url), f"应该能处理: {url}"
    
    def test_can_handle_invalid_urls(self):
        """测试拒绝无效URL"""
        scraper = ChatGPTScraper(use_playwright=False)
        
        invalid_urls = [
            'https://claude.ai/share/abc',
            'https://google.com',
            'https://chatgpt.com/other/path',
            'not-a-url'
        ]
        
        for url in invalid_urls:
            assert not scraper.can_handle(url), f"不应该处理: {url}"
    
    def test_validate_url(self):
        """测试URL验证"""
        scraper = ChatGPTScraper()
        
        assert scraper.validate_url('https://test.com')
        assert scraper.validate_url('http://test.com')
        assert not scraper.validate_url('ftp://test.com')
        assert not scraper.validate_url('test.com')


class TestClaudeScraper:
    """测试Claude爬虫"""
    
    def test_can_handle_valid_urls(self):
        """测试识别有效URL"""
        scraper = ClaudeScraper(use_playwright=False)
        
        valid_urls = [
            'https://claude.ai/share/abc123',
            'https://claude.ai/share/test-id-123',
            'http://claude.ai/share/xyz'
        ]
        
        for url in valid_urls:
            assert scraper.can_handle(url), f"应该能处理: {url}"
    
    def test_can_handle_invalid_urls(self):
        """测试拒绝无效URL"""
        scraper = ClaudeScraper(use_playwright=False)
        
        invalid_urls = [
            'https://chatgpt.com/share/abc',
            'https://claude.ai/other',
            'https://claude.com/share/abc'
        ]
        
        for url in invalid_urls:
            assert not scraper.can_handle(url), f"不应该处理: {url}"


class TestScraperFactory:
    """测试爬虫工厂"""
    
    def test_get_scraper_for_chatgpt(self):
        """测试获取ChatGPT爬虫"""
        factory = ScraperFactory()
        url = 'https://chatgpt.com/share/test123'
        scraper = factory.get_scraper(url)
        
        assert scraper is not None
        assert isinstance(scraper, ChatGPTScraper)
    
    def test_get_scraper_for_claude(self):
        """测试获取Claude爬虫"""
        factory = ScraperFactory()
        url = 'https://claude.ai/share/test123'
        scraper = factory.get_scraper(url)
        
        assert scraper is not None
        assert isinstance(scraper, ClaudeScraper)
    
    def test_get_scraper_unsupported_url(self):
        """测试不支持的URL"""
        factory = ScraperFactory()
        url = 'https://unsupported.com/share/test'
        scraper = factory.get_scraper(url)
        
        assert scraper is None
    
    def test_get_supported_platforms(self):
        """测试获取支持的平台"""
        factory = ScraperFactory()
        platforms = factory.get_supported_platforms()
        
        assert 'chatgpt' in platforms
        assert 'claude' in platforms
        assert len(platforms) >= 2
