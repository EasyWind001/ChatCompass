"""测试FTS - 检查索引"""
import sqlite3

conn = sqlite3.connect("test_fts.db")
cursor = conn.cursor()

# 检查FTS表内容
print("检查FTS表内容...")
cursor.execute("SELECT rowid, title, content FROM conversations_fts")
fts_rows = cursor.fetchall()
print(f"FTS表有 {len(fts_rows)} 条记录")
for row in fts_rows:
    print(f"  rowid={row[0]}, title={row[1]}, content={row[2]}")

# 检查主表
print("\n检查主表内容...")
cursor.execute("SELECT id, title, content FROM conversations")
main_rows = cursor.fetchall()
print(f"主表有 {len(main_rows)} 条记录")
for row in main_rows:
    print(f"  id={row[0]}, title={row[1]}, content={row[2]}")

# 尝试不同的搜索
print("\n尝试不同搜索...")
searches = ["Python", "python", "教程", "编程", "*"]
for search_term in searches:
    try:
        cursor.execute("""
            SELECT count(*) FROM conversations_fts WHERE conversations_fts MATCH ?
        """, (search_term,))
        count = cursor.fetchone()[0]
        print(f"  '{search_term}': {count} 条")
    except Exception as e:
        print(f"  '{search_term}': 错误 - {e}")

conn.close()
