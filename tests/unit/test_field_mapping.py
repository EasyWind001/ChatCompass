"""
Test field name mapping between Elasticsearch and main.py
"""

print("="*70)
print("Field Mapping Test")
print("="*70)

# Simulate Elasticsearch response
es_response = {
    '_id': 'test_id_123',
    '_source': {
        'title': 'Test Conversation',
        'platform': 'ChatGPT',
        'create_time': '2026-01-15T10:30:00',  # ES uses create_time
        'update_time': '2026-01-15T11:00:00',  # ES uses update_time
        'summary': 'Test summary',
        'category': 'Test'
    }
}

print("\n[1] Original Elasticsearch response:")
print(f"  _id: {es_response['_id']}")
print(f"  _source fields: {list(es_response['_source'].keys())}")

# Apply our mapping logic
conversation = es_response['_source']
conversation['id'] = es_response['_id']

# Field name mapping
if 'create_time' in conversation and 'created_at' not in conversation:
    conversation['created_at'] = conversation['create_time']
if 'update_time' in conversation and 'updated_at' not in conversation:
    conversation['updated_at'] = conversation['update_time']

print("\n[2] After mapping:")
print(f"  Fields: {list(conversation.keys())}")

# Test what main.py expects
print("\n[3] Testing main.py expectations...")

required_for_list = ['id', 'title', 'platform', 'created_at']
required_for_show = ['id', 'title', 'platform', 'created_at', 'source_url']

print("\n  For 'list' command (main.py:355-356):")
all_ok = True
for field in required_for_list:
    if field in conversation:
        print(f"    ✅ {field}: {conversation[field]}")
    else:
        print(f"    ❌ MISSING: {field}")
        all_ok = False

# Simulate the exact line from main.py:356
print("\n[4] Simulating main.py:356...")
try:
    output = f"      平台: {conversation['platform']} | 时间: {conversation['created_at']}"
    print(f"  ✅ Success: {output}")
except KeyError as e:
    print(f"  ❌ KeyError: {e}")
    all_ok = False

# Simulate main.py:241
print("\n[5] Simulating main.py:241...")
try:
    output = f"📅 时间: {conversation['created_at']}"
    print(f"  ✅ Success: {output}")
except KeyError as e:
    print(f"  ❌ KeyError: {e}")
    all_ok = False

print("\n" + "="*70)
if all_ok:
    print("✅ Field mapping works correctly!")
    print("="*70)
    print("\nThe fix should work. The mapping adds:")
    print("  - 'id' from '_id'")
    print("  - 'created_at' from 'create_time'")
    print("  - 'updated_at' from 'update_time'")
else:
    print("❌ Field mapping has issues")
    print("="*70)
