"""
爬虫工厂类
自动识别URL并选择合适的爬虫
"""
from typing import Optional
from .base_scraper import BaseScraper, ConversationData
from .chatgpt_scraper import ChatGPTScraper
from .claude_scraper import ClaudeScraper


class ScraperFactory:
    """爬虫工厂"""
    
    def __init__(self):
        # 注册所有可用的爬虫
        self.scrapers = [
            ChatGPTScraper(use_playwright=True),
            ClaudeScraper(use_playwright=True),
            # 未来可以添加更多平台：
            # GeminiScraper(),
            # DeepSeekScraper(),
            # KimiScraper(),
        ]
    
    def get_scraper(self, url: str) -> Optional[BaseScraper]:
        """根据URL获取对应的爬虫"""
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                return scraper
        return None
    
    def scrape(self, url: str) -> ConversationData:
        """自动识别并抓取"""
        scraper = self.get_scraper(url)
        
        if not scraper:
            raise ValueError(f"不支持的链接格式: {url}\n"
                           f"目前支持的平台: ChatGPT, Claude")
        
        print(f"识别到平台: {scraper.platform_name.upper()}")
        return scraper.scrape(url)
    
    def get_supported_platforms(self) -> list[str]:
        """获取支持的平台列表"""
        return [scraper.platform_name for scraper in self.scrapers]


# 使用示例
if __name__ == '__main__':
    factory = ScraperFactory()
    
    # 测试URL
    test_urls = [
        "https://chatgpt.com/share/abc123",
        "https://claude.ai/share/xyz789",
    ]
    
    for url in test_urls:
        scraper = factory.get_scraper(url)
        if scraper:
            print(f"{url} -> {scraper.platform_name}")
        else:
            print(f"{url} -> 不支持")
