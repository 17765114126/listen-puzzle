-- chat_history
CREATE TABLE chat_history_title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    introduce TEXT,                          -- 名称
    user_id INTEGER,                       -- 用户id
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);

-- chat_history
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    thumb_img TEXT,                        -- 图片
    content TEXT,                          -- 聊天内容
    chat_history_title_id INTEGER,         -- chat_history_title_id
    role_type TEXT,                        -- user-用户 assistant-系统
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);

