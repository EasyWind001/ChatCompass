"""测试不同的FTS5配置"""
import sqlite3

conn = sqlite3.connect("test_fts3.db")
cursor = conn.cursor()

# 创建表
cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, text TEXT)")

# 创建FTS5表 - 使用unicode61分词器
cursor.execute("""
CREATE VIRTUAL TABLE test_fts USING fts5(
    text,
    tokenize='unicode61'
)
""")

# 插入数据 - 直接插入FTS表
cursor.execute("INSERT INTO test_fts (text) VALUES (?)", ("Python编程教程",))
cursor.execute("INSERT INTO test_fts (text) VALUES (?)", ("JavaScript异步编程",))

conn.commit()

# 搜索
print("搜索测试...")
searches = ["Python", "编程", "教程", "JavaScript"]
for term in searches:
    cursor.execute("SELECT rowid, text FROM test_fts WHERE test_fts MATCH ?", (term,))
    results = cursor.fetchall()
    print(f"  '{term}': 找到 {len(results)} 条")
    for row in results:
        print(f"    -> {row[1]}")

conn.close()
