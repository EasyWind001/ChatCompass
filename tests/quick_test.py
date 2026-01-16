#!/usr/bin/env python3
"""Quick test of all 3 bug fixes"""
from database.sqlite_manager import SQLiteManager
from database.storage_adapter import StorageAdapter
import tempfile, os

print("="*60)
print("Quick Bug Fix Verification Test")
print("="*60)

# Setup
temp = tempfile.mktemp('.db')
mgr = SQLiteManager(temp)
adp = StorageAdapter(mgr)

# Test data
test_data = {
    'source_url': 'https://chatgpt.com/share/test-123',
    'platform': 'ChatGPT',
    'title': 'AWS Analytics Test',
    'messages': [
        {'role': 'user', 'content': 'Hello AWS'},
        {'role': 'assistant', 'content': 'Hello! How can I help?'}
    ]
}

# Test 1: Add conversation
print("\n[1] Adding conversation...")
cid = adp.add_conversation(
    source_url=test_data['source_url'],
    platform=test_data['platform'],
    title=test_data['title'],
    raw_content=test_data
)
print(f"✅ Added: {cid}")

# Test 2: Get by ID (Bug#1 and Bug#2 check)
print("\n[2] Get by ID (checking Bug#1 and Bug#2)...")
conv = adp.get_conversation(cid)

if 'id' not in conv:
    print("❌ Bug#1 NOT FIXED: Missing 'id' field")
    exit(1)
else:
    print(f"✅ Bug#1 FIXED: id={conv['id']}")

if 'created_at' not in conv:
    print("❌ Bug#2 NOT FIXED: Missing 'created_at' field")
    exit(1)
else:
    print(f"✅ Bug#2 FIXED: created_at={conv['created_at']}")

# Test 3: Get by URL (Bug#3 check)
print("\n[3] Get by URL (checking Bug#3)...")
try:
    conv_by_url = adp.get_conversation_by_url(test_data['source_url'])
    if conv_by_url is None:
        print("❌ Bug#3 NOT FIXED: get_conversation_by_url returned None")
        exit(1)
    if 'id' not in conv_by_url:
        print("❌ Bug#3 NOT FIXED: Missing 'id' in result")
        exit(1)
    print(f"✅ Bug#3 FIXED: Found by URL, id={conv_by_url['id']}")
except AttributeError as e:
    print(f"❌ Bug#3 NOT FIXED: {e}")
    exit(1)

# Test 4: List conversations
print("\n[4] List conversations...")
convs = adp.get_all_conversations(10)
if len(convs) == 0:
    print("❌ Empty list")
    exit(1)
if 'id' not in convs[0]:
    print("❌ List result missing 'id'")
    exit(1)
if 'created_at' not in convs[0]:
    print("❌ List result missing 'created_at'")
    exit(1)
print(f"✅ List OK: {len(convs)} conversations")

# Cleanup
os.unlink(temp)

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("✅ Bug#1 FIXED: 'id' field present")
print("✅ Bug#2 FIXED: 'created_at' field present")
print("✅ Bug#3 FIXED: get_conversation_by_url works")
print("="*60)
