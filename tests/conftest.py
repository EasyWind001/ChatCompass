"""
Pytest配置文件
定义共享的fixture和配置
"""
import pytest
import os
import sys
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_db():
    """创建临时数据库fixture"""
    import time
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # 清理 - 确保数据库连接已关闭
    time.sleep(0.1)  # 给一点时间让连接关闭
    try:
        if os.path.exists(db_path):
            os.unlink(db_path)
    except PermissionError:
        # 如果无法删除，稍后重试
        time.sleep(0.5)
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except:
            pass  # 忽略清理失败


@pytest.fixture
def temp_dir():
    """创建临时目录fixture"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_conversation_data():
    """示例对话数据"""
    return {
        'messages': [
            {'role': 'user', 'content': '你好，请介绍一下Python'},
            {'role': 'assistant', 'content': 'Python是一种高级编程语言，具有简洁的语法和强大的功能。'},
            {'role': 'user', 'content': '它有哪些应用领域？'},
            {'role': 'assistant', 'content': 'Python广泛应用于Web开发、数据分析、机器学习、自动化等领域。'}
        ]
    }


@pytest.fixture
def sample_messages():
    """示例消息列表"""
    from scrapers.base_scraper import Message
    return [
        Message(role='user', content='什么是机器学习？'),
        Message(role='assistant', content='机器学习是人工智能的一个分支...'),
        Message(role='user', content='有哪些常见算法？'),
        Message(role='assistant', content='常见算法包括线性回归、决策树、神经网络等。')
    ]
