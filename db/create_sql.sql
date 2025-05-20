-- chat_history
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    introduce TEXT,                        -- 名称
    content TEXT,                          -- 聊天内容
    user_id INTEGER,                       -- 用户id
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0             -- 逻辑删除
);

-- chat_role
CREATE TABLE chat_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    role_name TEXT,                        -- 角色名称
    role_setting TEXT,                     -- 角色设定
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0             -- 逻辑删除
);

