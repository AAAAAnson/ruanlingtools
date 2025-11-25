-- YouTube KOL Crawler Database Schema
-- SQLite compatible schema

-- 搜索记录表
CREATE TABLE IF NOT EXISTS youtube_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(100) NOT NULL,
    search_params TEXT,  -- JSON格式存储搜索参数
    min_subscribers INTEGER DEFAULT 10000,
    max_results INTEGER DEFAULT 50,
    published_after TEXT,  -- ISO 8601 datetime
    published_before TEXT,  -- ISO 8601 datetime
    order_by VARCHAR(20) DEFAULT 'relevance',  -- relevance, date, viewCount, rating
    total_channels INTEGER DEFAULT 0,
    total_videos INTEGER DEFAULT 0,
    api_key_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_yt_search_keyword ON youtube_searches(keyword);
CREATE INDEX IF NOT EXISTS idx_yt_search_created ON youtube_searches(created_at);

-- 频道表
CREATE TABLE IF NOT EXISTS youtube_channels (
    channel_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200),
    custom_url VARCHAR(100),
    description TEXT,
    country VARCHAR(50),
    subscriber_count INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    thumbnail_url TEXT,
    published_at TEXT,  -- ISO 8601 datetime
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_yt_channel_subs ON youtube_channels(subscriber_count);
CREATE INDEX IF NOT EXISTS idx_yt_channel_country ON youtube_channels(country);
CREATE INDEX IF NOT EXISTS idx_yt_channel_updated ON youtube_channels(last_updated_at);

-- 视频表
CREATE TABLE IF NOT EXISTS youtube_videos (
    video_id VARCHAR(20) PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    published_at TEXT,  -- ISO 8601 datetime
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0.0,
    duration_seconds INTEGER DEFAULT 0,
    thumbnail_url TEXT,
    video_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES youtube_channels(channel_id)
);

CREATE INDEX IF NOT EXISTS idx_yt_video_channel ON youtube_videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_yt_video_published ON youtube_videos(published_at);
CREATE INDEX IF NOT EXISTS idx_yt_video_engagement ON youtube_videos(engagement_rate);
CREATE INDEX IF NOT EXISTS idx_yt_video_views ON youtube_videos(view_count);

-- 搜索-频道关联表
CREATE TABLE IF NOT EXISTS youtube_search_channels (
    search_id INTEGER NOT NULL,
    channel_id VARCHAR(50) NOT NULL,
    keyword_videos_count INTEGER DEFAULT 0,
    keyword_total_views BIGINT DEFAULT 0,
    keyword_avg_views INTEGER DEFAULT 0,
    keyword_avg_engagement REAL DEFAULT 0.0,
    rank_position INTEGER,  -- 在搜索结果中的排名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (search_id, channel_id),
    FOREIGN KEY (search_id) REFERENCES youtube_searches(id),
    FOREIGN KEY (channel_id) REFERENCES youtube_channels(channel_id)
);

CREATE INDEX IF NOT EXISTS idx_yt_sc_search ON youtube_search_channels(search_id);
CREATE INDEX IF NOT EXISTS idx_yt_sc_channel ON youtube_search_channels(channel_id);
CREATE INDEX IF NOT EXISTS idx_yt_sc_rank ON youtube_search_channels(rank_position);

-- API配额使用记录表
CREATE TABLE IF NOT EXISTS youtube_api_quota_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_index INTEGER NOT NULL,
    operation VARCHAR(50) NOT NULL,  -- search, videos, channels
    cost INTEGER NOT NULL,  -- API配额消耗
    request_details TEXT,  -- JSON格式存储请求详情
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT (DATE('now'))
);

CREATE INDEX IF NOT EXISTS idx_yt_quota_date ON youtube_api_quota_usage(date);
CREATE INDEX IF NOT EXISTS idx_yt_quota_key ON youtube_api_quota_usage(api_key_index);
CREATE INDEX IF NOT EXISTS idx_yt_quota_op ON youtube_api_quota_usage(operation);
