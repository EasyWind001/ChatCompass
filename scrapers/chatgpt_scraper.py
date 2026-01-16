"""
ChatGPT分享链接爬虫
支持格式: https://chat.openai.com/share/xxx 或 https://chatgpt.com/share/xxx
"""
import re
import json
import time
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ConversationData, Message


class ChatGPTScraper(BaseScraper):
    """ChatGPT爬虫实现"""
    
    def __init__(self, use_playwright: bool = True):
        super().__init__()
        self.use_playwright = use_playwright
        self.platform_name = 'chatgpt'
    
    def can_handle(self, url: str) -> bool:
        """判断是否为ChatGPT分享链接"""
        patterns = [
            r'https?://chat\.openai\.com/share/[a-zA-Z0-9\-]+',
            r'https?://chatgpt\.com/share/[a-zA-Z0-9\-]+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def scrape(self, url: str) -> ConversationData:
        """抓取ChatGPT对话内容"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        if not self.can_handle(url):
            raise ValueError(f"不支持的ChatGPT链接格式: {url}")
        
        # 优先使用Playwright（处理动态内容）
        if self.use_playwright:
            return self._scrape_with_playwright(url)
        else:
            return self._scrape_with_requests(url)
    
    def _scrape_with_playwright(self, url: str) -> ConversationData:
        """使用Playwright抓取（推荐方式）"""
        print(f"[ChatGPT] 🌐 使用Playwright抓取: {url}")
        print(f"[ChatGPT] ⏳ 正在启动浏览器...")
        
        with sync_playwright() as p:
            # 启动浏览器（无头模式）
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # 访问页面
                print(f"[ChatGPT] 📡 正在加载页面...")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 尝试多种选择器等待内容加载
                print(f"[ChatGPT] ⏳ 等待内容加载...")
                selectors_to_try = [
                    '[data-testid^="conversation-turn"]',
                    'article',
                    '[role="article"]',
                    '[data-message-author-role]',
                    '[class*="conversation"]',
                ]
                
                content_loaded = False
                for selector in selectors_to_try:
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        print(f"[ChatGPT] 内容加载完成 (选择器: {selector})")
                        content_loaded = True
                        break
                    except PlaywrightTimeout:
                        continue
                
                if not content_loaded:
                    print("[ChatGPT] 警告: 使用标准选择器未找到内容，尝试通用方法...")
                
                # 额外等待确保内容完全加载
                time.sleep(3)
                
                # 获取页面HTML
                html_content = page.content()
                
                # 解析内容
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 提取标题
                title = self._extract_title(soup, page)
                
                # 提取消息（尝试多种方法）
                print(f"[ChatGPT] 🔍 正在提取对话内容...")
                messages = self._extract_messages_enhanced(soup, page)
                
                if not messages:
                    raise ValueError("未能提取到对话内容，可能页面结构已变化。请运行 debug_chatgpt.py 诊断问题。")
                
                total_chars = sum(len(msg.content) for msg in messages)
                print(f"[ChatGPT] ✅ 成功提取 {len(messages)} 条消息（共 {total_chars:,} 字符）")
                
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
        """使用requests抓取（备用方案，可能失败）"""
        import requests
        
        print(f"[ChatGPT] 使用requests抓取: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试从<script>标签中提取JSON数据
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # 这里需要根据实际JSON结构解析
                    # ChatGPT的分享页面可能在__NEXT_DATA__中包含对话数据
                    if 'props' in data and 'pageProps' in data['props']:
                        # 解析逻辑（需要根据实际结构调整）
                        pass
                except:
                    continue
            
            # 如果JSON解析失败，尝试HTML解析
            title = self._extract_title(soup)
            messages = self._extract_messages(soup)
            
            if not messages:
                raise ValueError("requests方法未能提取内容，建议使用Playwright")
            
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
        # 方法1: 从页面标题提取
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            # 移除"ChatGPT"等后缀
            title = re.sub(r'\s*[-|]\s*ChatGPT.*$', '', title)
            if title and title != 'ChatGPT':
                return title
        
        # 方法2: 从第一条用户消息提取（截取前50字符）
        first_message = soup.find('[data-testid^="conversation-turn-"]')
        if first_message:
            text = first_message.get_text(strip=True)
            return text[:50] + ('...' if len(text) > 50 else '')
        
        # 方法3: 使用Playwright获取
        if page:
            try:
                title_element = page.query_selector('h1, [role="heading"]')
                if title_element:
                    return title_element.inner_text()
            except:
                pass
        
        return "未命名对话"
    
    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """提取对话消息"""
        messages = []
        
        # ChatGPT的消息通常在data-testid="conversation-turn-*"的div中
        conversation_turns = soup.find_all('div', {'data-testid': re.compile(r'conversation-turn-\d+')})
        
        for turn in conversation_turns:
            # 判断角色（通常通过class或data属性）
            role = self._determine_role(turn)
            
            # 提取文本内容
            content = self._extract_message_content(turn)
            
            if content:
                messages.append(Message(
                    role=role,
                    content=content.strip()
                ))
        
        return messages
    
    def _extract_messages_enhanced(self, soup: BeautifulSoup, page=None) -> list[Message]:
        """增强的消息提取方法（支持多种页面结构）"""
        messages = []
        
        # 方法1: 使用data-testid
        conversation_turns = soup.find_all('div', {'data-testid': re.compile(r'conversation-turn-\d+')})
        if conversation_turns:
            print(f"[ChatGPT] 方法1: 找到 {len(conversation_turns)} 个conversation-turn")
            for turn in conversation_turns:
                role = self._determine_role(turn)
                content = self._extract_message_content(turn)
                if content:
                    messages.append(Message(role=role, content=content.strip()))
            if messages:
                return messages
        
        # 方法2: 使用article标签
        articles = soup.find_all('article')
        if articles:
            print(f"[ChatGPT] 方法2: 找到 {len(articles)} 个article")
            for i, article in enumerate(articles):
                # 交替user/assistant
                role = 'user' if i % 2 == 0 else 'assistant'
                content = self._extract_message_content(article)
                if content:
                    messages.append(Message(role=role, content=content.strip()))
            if messages:
                return messages
        
        # 方法3: 使用data-message-author-role
        message_elements = soup.find_all(attrs={'data-message-author-role': True})
        if message_elements:
            print(f"[ChatGPT] 方法3: 找到 {len(message_elements)} 个带author-role的元素")
            for element in message_elements:
                role = element.get('data-message-author-role')
                role = 'user' if role == 'user' else 'assistant'
                content = self._extract_message_content(element)
                if content:
                    messages.append(Message(role=role, content=content.strip()))
            if messages:
                return messages
        
        # 方法4: 使用Playwright直接提取
        if page:
            print("[ChatGPT] 方法4: 尝试使用Playwright直接提取")
            try:
                # 尝试找到所有消息元素
                elements = page.query_selector_all('article, [data-testid^="conversation-turn"], [role="article"]')
                if elements:
                    print(f"[ChatGPT] Playwright找到 {len(elements)} 个消息元素")
                    for i, element in enumerate(elements):
                        try:
                            text = element.inner_text()
                            if text and len(text.strip()) > 0:
                                role = 'user' if i % 2 == 0 else 'assistant'
                                messages.append(Message(role=role, content=text.strip()))
                        except:
                            continue
                    if messages:
                        return messages
            except Exception as e:
                print(f"[ChatGPT] Playwright提取失败: {e}")
        
        # 方法5: 通用方法 - 查找包含大量文本的div
        print("[ChatGPT] 方法5: 使用通用文本提取")
        all_divs = soup.find_all('div', class_=True)
        text_blocks = []
        for div in all_divs:
            text = div.get_text(strip=True)
            # 过滤掉太短的内容
            if len(text) > 20 and len(text) < 5000:
                # 检查是否是独立的文本块
                children_text = sum(len(child.get_text(strip=True)) for child in div.find_all('div'))
                if children_text < len(text) * 0.5:  # 子元素文本不超过自身的50%
                    text_blocks.append(text)
        
        if text_blocks:
            print(f"[ChatGPT] 找到 {len(text_blocks)} 个文本块")
            for i, text in enumerate(text_blocks[:20]):  # 最多20条
                role = 'user' if i % 2 == 0 else 'assistant'
                messages.append(Message(role=role, content=text))
            if messages:
                return messages
        
        return messages
    
    def _determine_role(self, element) -> str:
        """判断消息角色"""
        # 方法1: 检查data-message-author-role属性
        author_role = element.get('data-message-author-role')
        if author_role:
            return 'user' if author_role == 'user' else 'assistant'
        
        # 方法2: 检查class名称
        classes = element.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else classes
        
        if 'user' in class_str.lower():
            return 'user'
        elif 'assistant' in class_str.lower() or 'bot' in class_str.lower():
            return 'assistant'
        
        # 方法3: 检查子元素
        if element.find('div', class_=re.compile(r'.*agent.*', re.I)):
            return 'assistant'
        
        # 默认交替判断（第一条通常是user）
        return 'user'
    
    def _extract_message_content(self, element) -> str:
        """提取消息文本内容"""
        # 移除不需要的元素（按钮、图标等）
        for unwanted in element.find_all(['button', 'svg', 'img']):
            unwanted.decompose()
        
        # 获取纯文本
        text = element.get_text(separator='\n', strip=True)
        
        # 清理多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text


# 使用示例
if __name__ == '__main__':
    scraper = ChatGPTScraper(use_playwright=True)
    
    # 测试URL
    test_url = "https://chatgpt.com/share/example-id"
    
    if scraper.can_handle(test_url):
        try:
            data = scraper.scrape(test_url)
            print(f"标题: {data.title}")
            print(f"消息数: {data.message_count}")
            print(f"字数: {data.word_count}")
            print("\n完整对话:")
            print(data.get_full_text())
        except Exception as e:
            print(f"错误: {e}")
