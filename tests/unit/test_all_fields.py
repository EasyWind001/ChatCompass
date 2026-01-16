"""
Complete field validation test
Tests ALL required fields that main.py expects
"""
import pytest
import tempfile
import os
from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter


@pytest.fixture
def storage_adapter():
    """Create temporary storage adapter for testing"""
    temp_db = tempfile.mktemp('.db')
    sqlite_mgr = SQLiteManager(temp_db)
    adapter = StorageAdapter(sqlite_mgr)
    
    yield adapter
    
    adapter.close()
    try:
        os.unlink(temp_db)
    except:
        pass


def test_all_required_fields(storage_adapter):
    """Test ALL required fields that main.py expects"""
    
    # Add test conversation
    conv_id = storage_adapter.add_conversation(
        source_url='https://test.com/123',
        platform='ChatGPT',
        title='Test Conversation',
        raw_content={
            'messages': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        },
        summary='Test summary',
        category='Test',
        tags=['test', 'demo']
    )
    
    assert conv_id is not None, "Should return conversation ID"
    
    # Test list command - this is what main.py uses
    conversations = storage_adapter.get_all_conversations(limit=10)
    
    assert len(conversations) > 0, "Should return conversations"
    
    conv = conversations[0]
    
    # Check ALL fields that main.py expects
    required_fields = ['id', 'title', 'platform', 'created_at']
    
    for field in required_fields:
        assert field in conv, f"Missing required field: {field}"
        assert conv[field] is not None, f"Field {field} should not be None"
    
    # Test that we can access fields like main.py does
    output = f"平台: {conv['platform']} | 时间: {conv['created_at']}"
    assert len(output) > 0, "Should generate output successfully"


def test_optional_fields(storage_adapter):
    """Test optional fields main.py might use"""
    
    conv_id = storage_adapter.add_conversation(
        source_url='https://test.com/123',
        platform='ChatGPT',
        title='Test',
        raw_content={'messages': []},
        summary='Summary',
        category='Category',
        tags=['tag1']
    )
    
    conversations = storage_adapter.get_all_conversations(limit=1)
    conv = conversations[0]
    
    # These fields should exist
    optional_fields = ['summary', 'category', 'tags', 'updated_at', 'source_url']
    
    for field in optional_fields:
        assert field in conv, f"Optional field {field} should exist"
