"""Test list command ID field"""
import sys
import os
from pathlib import Path
import tempfile

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("Testing SQLite list command")
print("=" * 70)

from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter

temp_db = tempfile.mktemp(suffix=".db")

try:
    # Initialize
    print("\n[1] Initializing SQLite...")
    sqlite_mgr = SQLiteManager(temp_db)
    adapter = StorageAdapter(sqlite_mgr)
    print("  OK: Initialized")
    
    # Add test data
    print("\n[2] Adding test conversation...")
    conv_id = adapter.add_conversation(
        source_url='https://test.com/123',
        platform='Test',
        title='Test Conversation',
        raw_content={'messages': [{'role': 'user', 'content': 'test'}]}
    )
    print(f"  OK: Added ID: {conv_id}")
    
    # Test list
    print("\n[3] Testing list command...")
    conversations = adapter.get_all_conversations(limit=10)
    
    print(f"\n  Returned records: {len(conversations)}")
    
    if len(conversations) > 0:
        first = conversations[0]
        print(f"  Fields: {list(first.keys())}")
        
        if 'id' in first:
            print(f"  OK: Has id field: {first['id']}")
            print(f"  OK: Title: {first['title']}")
            print("\nOK: SQLite test passed!")
        else:
            print("  FAIL: Missing id field!")
            print(f"  Full data: {first}")
            sys.exit(1)
    else:
        print("  FAIL: No records returned!")
        sys.exit(1)
    
    adapter.close()

finally:
    try:
        os.unlink(temp_db)
    except:
        pass

print("\n" + "=" * 70)
print("All tests passed!")
print("=" * 70)
