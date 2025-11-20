# tools/init_db_min.py
import os, sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)  # up from tools/
DB_PATH = os.path.join(ROOT, "data", "youtube_kol.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# 最小可用结构：channels（含导出所需列）
cur.execute("""
CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    title TEXT,
    homepage_url TEXT,
    youtube_handle TEXT,
    custom_url TEXT,
    country TEXT,
    detected_language TEXT,
    subscriber_count INTEGER,
    video_count INTEGER,
    view_count INTEGER,
    thumbnail_url TEXT,
    banner_url TEXT,
    description TEXT,
    branding_json TEXT,
    social_links TEXT,
    etag TEXT,
    detected_country TEXT,
    created_at TEXT,
    updated_at TEXT,
    captured_at TEXT
);
""")

con.commit()
con.close()
print("OK: youtube_kol.db 初始化完成：", DB_PATH)
