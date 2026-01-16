"""测试FTS5 - 使用简单查询"""
import sqlite3

conn = sqlite3.connect("test_fts_final.db")
cursor = conn.cursor()

# 创建表并直接插入FTS
cursor.execute("""
CREATE VIRTUAL TABLE docs USING fts5(content)
""")

# 插入数据
docs = [
    "Python is a programming language",
    "JavaScript is used for web development",
    "学习编程需要耐心",
]

for doc in docs:
    cursor.execute("INSERT INTO docs VALUES (?)", (doc,))

conn.commit()

# 测试搜索
print("搜索测试...")

# 尝试查询所有
cursor.execute("SELECT * FROM docs")
all_rows = cursor.fetchall()
print(f"\n总共 {len(all_rows)} 条记录:")
for row in all_rows:
    print(f"  {row[0]}")

# 尝试搜索
print("\n搜索...")
searches = ["Python", "programming", "JavaScript", "编程"]

for term in searches:
    cursor.execute("SELECT * FROM docs WHERE docs MATCH ?", (term,))
    results = cursor.fetchall()
    print(f"  '{term}': {len(results)} 条")
    for row in results:
        print(f"    -> {row[0]}")

conn.close()
