-- ============================================
-- AI对话知识库管理系统 - 数据库Schema
-- ============================================

-- 1. 对话主表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT UNIQUE NOT NULL,              -- 原始分享链接
    platform TEXT NOT NULL,                        -- 平台标识: chatgpt, claude, gemini等
    title TEXT,                                    -- 对话标题
    raw_content TEXT NOT NULL,                     -- 原始对话内容(JSON格式)
    summary TEXT,                                  -- AI生成的摘要
    category TEXT,                                 -- 主分类: 编程/写作/学习/策划/休闲娱乐/其他
    word_count INTEGER DEFAULT 0,                  -- 字数统计
    message_count INTEGER DEFAULT 0,               -- 消息轮次数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 更新时间
    is_favorite INTEGER DEFAULT 0,                 -- 是否收藏
    notes TEXT                                     -- 用户备注
);

-- 2. 标签表
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,                     -- 标签名称
    color TEXT DEFAULT '#3B82F6',                  -- 标签颜色(HEX)
    usage_count INTEGER DEFAULT 0,                 -- 使用次数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 对话-标签关联表 (多对多)
CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (conversation_id, tag_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 4. FTS5全文搜索虚拟表
CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
    title,                    -- 标题
    summary,                  -- 摘要
    raw_content,              -- 完整对话内容
    content='conversations',  -- 关联到conversations表
    content_rowid='id',       -- 使用id作为rowid
    tokenize='porter unicode61 remove_diacritics 1'  -- 分词器配置(支持中英文)
);

-- ============================================
-- 触发器：自动同步FTS索引
-- ============================================

-- 插入时同步到FTS表
CREATE TRIGGER IF NOT EXISTS conversations_ai AFTER INSERT ON conversations BEGIN
    INSERT INTO conversations_fts(rowid, title, summary, raw_content)
    VALUES (new.id, new.title, new.summary, new.raw_content);
END;

-- 更新时同步到FTS表
CREATE TRIGGER IF NOT EXISTS conversations_au AFTER UPDATE ON conversations BEGIN
    DELETE FROM conversations_fts WHERE rowid = old.id;
    INSERT INTO conversations_fts(rowid, title, summary, raw_content)
    VALUES (new.id, new.title, new.summary, new.raw_content);
END;

-- 删除时同步到FTS表
CREATE TRIGGER IF NOT EXISTS conversations_ad AFTER DELETE ON conversations BEGIN
    DELETE FROM conversations_fts WHERE rowid = old.id;
END;

-- 更新updated_at时间戳
CREATE TRIGGER IF NOT EXISTS conversations_update_timestamp 
AFTER UPDATE ON conversations
FOR EACH ROW
BEGIN
    UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- 索引优化
-- ============================================

-- 平台索引
CREATE INDEX IF NOT EXISTS idx_conversations_platform ON conversations(platform);

-- 分类索引
CREATE INDEX IF NOT EXISTS idx_conversations_category ON conversations(category);

-- 创建时间索引(降序，用于最新列表)
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- 收藏索引
CREATE INDEX IF NOT EXISTS idx_conversations_favorite ON conversations(is_favorite);

-- 标签名称索引
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- 标签使用次数索引
CREATE INDEX IF NOT EXISTS idx_tags_usage_count ON tags(usage_count DESC);

-- ============================================
-- 初始化数据
-- ============================================

-- 插入默认分类标签
INSERT OR IGNORE INTO tags (name, color) VALUES 
    ('编程', '#10B981'),
    ('Python', '#3B82F6'),
    ('JavaScript', '#F59E0B'),
    ('写作', '#8B5CF6'),
    ('学习', '#EC4899'),
    ('策划', '#F97316'),
    ('休闲娱乐', '#14B8A6'),
    ('其他', '#6B7280');
