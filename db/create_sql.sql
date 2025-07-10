-- video_source
CREATE TABLE video_source (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    video_name TEXT,                        -- 名称
    web_path TEXT,                        -- web_path
    local_path TEXT,                     -- local_path
    duration TEXT,                     -- 时长
    description TEXT,                     -- 描述
    video_type TINYINT DEFAULT 0,             -- 0:未使用 1：使用中
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0             -- 逻辑删除
);
-- audio_source
CREATE TABLE audio_source (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    audio_name TEXT,                        -- 名称
    prompt_text TEXT,                     -- 参考文本
    web_path TEXT,                        -- web_path
    local_path TEXT,                     -- local_path
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0             -- 逻辑删除
);
