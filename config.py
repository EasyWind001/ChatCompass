"""
配置管理模块
从环境变量或.env文件加载配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# ==================== AI配置 ====================

AI_MODE = os.getenv('AI_MODE', 'local')  # local / online / hybrid

# Ollama配置
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# DeepSeek配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# ==================== 数据库配置 ====================

# 存储类型: sqlite / elasticsearch
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'sqlite')

# SQLite配置
DATABASE_PATH = os.getenv('DATABASE_PATH', str(PROJECT_ROOT / 'data' / 'chatcompass.db'))

# Elasticsearch配置
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
ELASTICSEARCH_INDEX_PREFIX = os.getenv('ELASTICSEARCH_INDEX_PREFIX', 'chatcompass')
ELASTICSEARCH_USER = os.getenv('ELASTICSEARCH_USER', '')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', '')

# ==================== 爬虫配置 ====================

USE_PLAYWRIGHT = os.getenv('USE_PLAYWRIGHT', 'true').lower() == 'true'
SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '30'))
USER_AGENT = os.getenv('USER_AGENT', 
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

# ==================== 应用配置 ====================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
UI_THEME = os.getenv('UI_THEME', 'auto')  # light / dark / auto
LANGUAGE = os.getenv('LANGUAGE', 'zh_CN')

# ==================== 常量定义 ====================

# 支持的平台
SUPPORTED_PLATFORMS = ['chatgpt', 'claude', 'gemini', 'deepseek', 'kimi']

# 分类选项
CATEGORIES = ['编程', '写作', '学习', '策划', '休闲娱乐', '其他']

# 默认标签颜色
TAG_COLORS = {
    '编程': '#10B981',
    'Python': '#3B82F6',
    'JavaScript': '#F59E0B',
    '写作': '#8B5CF6',
    '学习': '#EC4899',
    '策划': '#F97316',
    '休闲娱乐': '#14B8A6',
    '其他': '#6B7280'
}


def get_storage():
    """根据配置获取存储实例（推荐使用此方法）"""
    from database.base_storage import StorageFactory
    
    if STORAGE_TYPE == 'sqlite':
        return StorageFactory.create('sqlite', db_path=DATABASE_PATH)
    elif STORAGE_TYPE == 'elasticsearch':
        kwargs = {
            'host': ELASTICSEARCH_HOST,
            'port': ELASTICSEARCH_PORT,
            'index_prefix': ELASTICSEARCH_INDEX_PREFIX
        }
        # 可选的认证信息
        if ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
            kwargs['username'] = ELASTICSEARCH_USER
            kwargs['password'] = ELASTICSEARCH_PASSWORD
        return StorageFactory.create('elasticsearch', **kwargs)
    else:
        raise ValueError(f"不支持的存储类型: {STORAGE_TYPE}")


def get_ai_service():
    """根据配置获取AI服务（推荐使用此方法）"""
    from ai import get_ai_service as _get_ai_service, AIConfig
    
    # 创建配置
    config = AIConfig(
        enabled=(AI_MODE in ['local', 'online', 'hybrid']),
        backend='ollama' if AI_MODE == 'local' else 'ollama',  # 默认使用ollama
        ollama_host=OLLAMA_BASE_URL,
        ollama_model=OLLAMA_MODEL
    )
    
    return _get_ai_service(config)


def get_ai_client():
    """根据配置获取AI客户端（向后兼容，推荐使用get_ai_service）"""
    if AI_MODE == 'local':
        from ai.ollama_client import OllamaClient
        return OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    
    elif AI_MODE == 'online':
        if DEEPSEEK_API_KEY:
            from ai.openai_client import DeepSeekClient
            return DeepSeekClient(api_key=DEEPSEEK_API_KEY, model=DEEPSEEK_MODEL)
        elif OPENAI_API_KEY:
            from ai.openai_client import OpenAIClient
            return OpenAIClient(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        else:
            raise ValueError("在线模式需要配置API密钥")
    
    elif AI_MODE == 'hybrid':
        # 混合模式：优先在线，失败降级到本地
        try:
            if DEEPSEEK_API_KEY:
                from ai.openai_client import DeepSeekClient
                client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
                if client.is_available():
                    return client
        except:
            pass
        
        # 降级到本地
        from ai.ollama_client import OllamaClient
        return OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    
    else:
        raise ValueError(f"不支持的AI模式: {AI_MODE}")


# 使用示例
if __name__ == '__main__':
    print(f"AI模式: {AI_MODE}")
    print(f"数据库路径: {DATABASE_PATH}")
    print(f"支持的平台: {SUPPORTED_PLATFORMS}")
    
    try:
        client = get_ai_client()
        print(f"AI客户端: {client.__class__.__name__}")
    except Exception as e:
        print(f"AI客户端初始化失败: {e}")
