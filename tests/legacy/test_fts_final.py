"""
诊断FTS搜索问题
"""
import sqlite3

db = sqlite3.connect('demo.db')
cursor = db.cursor()

print("=" * 60)
print("FTS表诊断")
print("=" * 60)

# 1. 检查FTS表内容
print("\n[1] 检查FTS表数据:")
cursor.execute("SELECT rowid, title FROM conversations_fts")
rows = cursor.fetchall()
print(f"FTS表中有 {len(rows)} 条记录")
for row in rows:
    print(f"  rowid={row[0]}: {row[1]}")

# 2. 测试不同的搜索方式
print("\n[2] 测试不同搜索语法:")

# 方式1: 直接搜索
print("\n  方式1: MATCH 'Python'")
cursor.execute("SELECT rowid, title FROM conversations_fts WHERE conversations_fts MATCH 'Python'")
print(f"    结果: {len(cursor.fetchall())} 条")

# 方式2: 通配符
print("\n  方式2: MATCH 'Python*'")
cursor.execute("SELECT rowid, title FROM conversations_fts WHERE conversations_fts MATCH 'Python*'")
print(f"    结果: {len(cursor.fetchall())} 条")

# 方式3: 搜索raw_content
print("\n  方式3: MATCH 'raw_content:Python'")
cursor.execute("SELECT rowid, title FROM conversations_fts WHERE conversations_fts MATCH 'raw_content:Python'")
results = cursor.fetchall()
print(f"    结果: {len(results)} 条")
for r in results:
    print(f"      - {r[1]}")

# 方式4: 小写搜索
print("\n  方式4: MATCH 'python'")
cursor.execute("SELECT rowid, title FROM conversations_fts WHERE conversations_fts MATCH 'python'")
results = cursor.fetchall()
print(f"    结果: {len(results)} 条")
for r in results:
    print(f"      - {r[1]}")

# 方式5: 搜索标题中的内容
print("\n  方式5: MATCH 'title:数据分析'")
cursor.execute("SELECT rowid, title FROM conversations_fts WHERE conversations_fts MATCH 'title:数据分析'")
print(f"    结果: {len(cursor.fetchall())} 条")

# 方式6: 使用LIKE (非FTS)
print("\n  方式6: 使用LIKE查询原表")
cursor.execute("SELECT id, title FROM conversations WHERE title LIKE '%Python%'")
results = cursor.fetchall()
print(f"    结果: {len(results)} 条")
for r in results:
    print(f"      - {r[1]}")

# 3. 检查raw_content的实际内容
print("\n[3] 检查raw_content字段内容:")
cursor.execute("SELECT id, title, substr(raw_content, 1, 100) FROM conversations LIMIT 1")
row = cursor.fetchone()
print(f"  ID={row[0]}")
print(f"  标题: {row[1]}")
print(f"  内容前100字符: {row[2]}")

db.close()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
