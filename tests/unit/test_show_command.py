#!/usr/bin/env python3
"""Test show command fix - verify no more NoneType cursor error"""
import pytest
import tempfile
import os


@pytest.fixture
def storage_adapter():
    """Create temporary storage adapter"""
    from database.sqlite_manager import SQLiteManager
    from database.storage_adapter import StorageAdapter
    
    temp_db = tempfile.mktemp('.db')
    sqlite_mgr = SQLiteManager(temp_db)
    adapter = StorageAdapter(sqlite_mgr)
    
    yield adapter
    
    # Proper cleanup
    adapter.close()
    try:
        os.unlink(temp_db)
    except:
        pass  # Ignore cleanup errors


def test_storage_adapter_has_get_by_url():
    """Test that StorageAdapter has get_conversation_by_url method"""
    from database.storage_adapter import StorageAdapter
    assert hasattr(StorageAdapter, 'get_conversation_by_url'), \
        "StorageAdapter should have get_conversation_by_url method"


def test_get_conversation_by_url(storage_adapter):
    """Test get_conversation_by_url with SQLite backend"""
    test_url = "https://test.example.com/123"
    
    # Add test conversation
    conv_id = storage_adapter.add_conversation(
        source_url=test_url,
        platform="Test",
        title="Test Conversation",
        raw_content={"messages": [{"role": "user", "content": "Hello"}]}
    )
    
    # Test get_conversation_by_url
    conv = storage_adapter.get_conversation_by_url(test_url)
    
    assert conv is not None, "Should find conversation by URL"
    assert conv['source_url'] == test_url, "URL should match"
    assert 'id' in conv, "Should have id field"
    assert 'created_at' in conv, "Should have created_at field"


def test_show_conversation_logic(storage_adapter):
    """Test show_conversation logic (ID and URL lookup)"""
    test_url = "https://test.example.com/123"
    
    # Add conversation
    conv_id = storage_adapter.add_conversation(
        source_url=test_url,
        platform="Test",
        title="Test Conversation",
        raw_content={"messages": [{"role": "user", "content": "Hello"}]}
    )
    
    # Test with ID
    found_conv = storage_adapter.get_conversation(conv_id)
    if not found_conv:
        found_conv = storage_adapter.get_conversation_by_url(conv_id)
    
    assert found_conv is not None, "Should find conversation by ID"
    assert found_conv['title'] == "Test Conversation"
    
    # Test with URL
    found_conv = storage_adapter.get_conversation(test_url)
    if not found_conv:
        found_conv = storage_adapter.get_conversation_by_url(test_url)
    
    assert found_conv is not None, "Should find conversation by URL"
    assert found_conv['title'] == "Test Conversation"
