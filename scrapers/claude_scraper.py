"""
Claude分享链接爬虫
支持格式: https://claude.ai/share/xxx
"""
import re
import json
import time
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ConversationData, Message


class ClaudeScraper(BaseScraper):
    """Claude爬虫实现"""
    
    def __init__(self, use_playwright: bool = True):
        super().__init__()
        self.use_playwright = use_playwright
        self.platform_name = 'claude'
    
    def can_handle(self, url: str) -> bool:
        """判断是否为Claude分享链接"""
        pattern = r'https?://claude\.ai/share/[a-zA-Z0-9\-]+'
        return bool(re.match(pattern, url))
    
    def scrape(self, url: str) -> ConversationData:
        """抓取Claude对话内容"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        if not self.can_handle(url):
            raise ValueError(f"不支持的Claude链接格式: {url}")
        
        # Claude分享页面通常需要JavaScript渲染
        if self.use_playwright:
            return self._scrape_with_playwright(url)
        else:
            return self._scrape_with_requests(url)
    
    def _scrape_with_playwright(self, url: str) -> ConversationData:
        """使用Playwright抓取"""
        print(f"[Claude] 使用Playwright抓取: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # 访问页面
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 等待对话容器加载（根据实际页面结构调整选择器）
                # Claude的页面结构可能使用不同的选择器
                try:
                    page.wait_for_selector('[data-test-render-count]', timeout=10000)
                except:
                    # 备用选择器
                    page.wait_for_selector('div[class*="message"]', timeout=10000)
                
                # 等待内容完全加载
                time.sleep(2)
                
                # 滚动到底部确保所有内容加载
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
                
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 提取标题
                title = self._extract_title(soup, page)
                
                # 提取消息
                messages = self._extract_messages(soup, page)
                
                if not messages:
                    raise ValueError("未能提取到对话内容")
                
                return ConversationData(
                    platform=self.platform_name,
                    url=url,
                    title=title,
                    messages=messages,
                    metadata={'scrape_method': 'playwright'}
                )
                
            except PlaywrightTimeout:
                raise TimeoutError(f"页面加载超时: {url}")
            except Exception as e:
                raise RuntimeError(f"抓取失败: {str(e)}")
            finally:
                browser.close()
    
    def _scrape_with_requests(self, url: str) -> ConversationData:
        """使用requests抓取（可能不可用）"""
        import requests
        
        print(f"[Claude] 使用requests抓取: {url}")
        print("[警告] Claude分享页面通常需要JavaScript，requests方法可能失败")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试从script标签提取数据
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # 尝试解析初始状态数据
                    try:
                        json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', script.string)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            # 根据实际数据结构解析
                            # 这部分需要根据Claude的实际数据格式调整
                            pass
                    except:
                        continue
            
            title = self._extract_title(soup)
            messages = self._extract_messages(soup)
            
            if not messages:
                raise ValueError("requests方法失败，请使用Playwright")
            
            return ConversationData(
                platform=self.platform_name,
                url=url,
                title=title,
                messages=messages,
                metadata={'scrape_method': 'requests'}
            )
            
        except requests.RequestException as e:
            raise RuntimeError(f"网络请求失败: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup, page=None) -> str:
        """提取对话标题"""
        # 方法1: 从页面标题
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            title = re.sub(r'\s*[-|]\s*Claude.*$', '', title)
            if title and title != 'Claude':
                return title
        
        # 方法2: 使用Playwright查找标题元素
        if page:
            try:
                # Claude可能在特定位置显示对话标题
                title_selectors = [
                    'h1',
                    '[class*="title"]',
                    '[class*="conversation-name"]'
                ]
                for selector in title_selectors:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text().strip()
                        if text and len(text) < 100:
                            return text
            except:
                pass
        
        # 方法3: 从第一条消息提取
        messages = soup.find_all('div', class_=re.compile(r'.*message.*', re.I))
        if messages:
            first_text = messages[0].get_text(strip=True)
            return first_text[:50] + ('...' if len(first_text) > 50 else '')
        
        return "未命名对话"
    
    def _extract_messages(self, soup: BeautifulSoup, page=None) -> list[Message]:
        """提取对话消息"""
        messages = []
        
        # Claude的消息结构（需要根据实际页面调整）
        # 可能的选择器：
        message_selectors = [
            'div[class*="message"]',
            'div[data-test-render-count]',
            'div[class*="conversation-item"]'
        ]
        
        message_elements = []
        for selector in message_selectors:
            elements = soup.select(selector)
            if elements:
                message_elements = elements
                break
        
        # 如果HTML解析失败，尝试使用Playwright直接提取
        if not message_elements and page:
            message_elements = self._extract_messages_with_playwright(page)
        
        for element in message_elements:
            role = self._determine_role(element)
            content = self._extract_message_content(element)
            
            if content:
                messages.append(Message(
                    role=role,
                    content=content.strip()
                ))
        
        return messages
    
    def _extract_messages_with_playwright(self, page) -> list:
        """使用Playwright直接提取消息"""
        try:
            # 获取所有消息元素
            message_elements = page.query_selector_all('div[class*="message"]')
            return [elem for elem in message_elements]
        except:
            return []
    
    def _determine_role(self, element) -> str:
        """判断消息角色"""
        # 检查class或data属性
        element_str = str(element)
        
        if 'human' in element_str.lower() or 'user' in element_str.lower():
            return 'user'
        elif 'assistant' in element_str.lower() or 'claude' in element_str.lower():
            return 'assistant'
        
        # 检查是否包含特定标识
        classes = element.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
        
        if 'human' in class_str or 'user' in class_str:
            return 'user'
        
        return 'assistant'
    
    def _extract_message_content(self, element) -> str:
        """提取消息文本内容"""
        # 如果是Playwright元素
        if hasattr(element, 'inner_text'):
            return element.inner_text()
        
        # 如果是BeautifulSoup元素
        # 移除按钮等不需要的元素
        if hasattr(element, 'find_all'):
            for unwanted in element.find_all(['button', 'svg']):
                unwanted.decompose()
            
            text = element.get_text(separator='\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text
        
        return str(element)


# 使用示例
if __name__ == '__main__':
    scraper = ClaudeScraper(use_playwright=True)
    
    test_url = "https://claude.ai/share/example-id"
    
    if scraper.can_handle(test_url):
        try:
            data = scraper.scrape(test_url)
            print(f"标题: {data.title}")
            print(f"消息数: {data.message_count}")
            print(f"字数: {data.word_count}")
        except Exception as e:
            print(f"错误: {e}")
