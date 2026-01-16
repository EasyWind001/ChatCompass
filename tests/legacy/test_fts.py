"""测试FTS全文搜索"""
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect("test_fts.db")
cursor = conn.cursor()

# 创建表
print("创建表...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT
)
""")

cursor.execute("""
CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
    title, content,
    content='conversations',
    content_rowid='id'
)
""")

# 创建触发器
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS conversations_ai AFTER INSERT ON conversations BEGIN
    INSERT INTO conversations_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END
""")

conn.commit()

# 插入数据
print("插入数据...")
cursor.execute("""
INSERT INTO conversations (title, content) VALUES (?, ?)
""", ("Python教程", "学习Python编程语言的基础知识"))

conn.commit()

# 测试搜索
print("\n测试搜索...")
cursor.execute("""
SELECT c.id, c.title, 
       snippet(conversations_fts, 1, '<mark>', '</mark>', '...', 32) as snippet
FROM conversations_fts
JOIN conversations c ON conversations_fts.rowid = c.id
WHERE conversations_fts MATCH ?
""", ("Python",))

results = cursor.fetchall()
print(f"搜索'Python': 找到 {len(results)} 条结果")

for row in results:
    print(f"  ID={row[0]}, 标题={row[1]}")
    print(f"  片段={row[2]}")

conn.close()
print("\n测试完成!")
