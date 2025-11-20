# tools/migrate_channels_schema.py
import os
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)  # up from tools/
CANDIDATES = [
    os.path.join(ROOT, "data", "ytkol.db"),
    os.path.join(ROOT, "data", "youtube_kol.db"),
    os.path.join(ROOT, "data", "app.db"),
    os.path.join(ROOT, "ytkol.db"),
    os.path.join(ROOT, "youtube_kol.db"),
    os.path.join(ROOT, "app.db"),
]

NEED_COLUMNS = {
    "homepage_url": "TEXT",
    "youtube_handle": "TEXT",
    "custom_url": "TEXT",
    "detected_language": "TEXT",
}

def find_db():
    for p in CANDIDATES:
        if os.path.isfile(p):
            return p
    # 兜底：全项目搜 *.db
    for root, _, files in os.walk(ROOT):
        for f in files:
            if f.lower().endswith(".db"):
                return os.path.join(root, f)
    return None

def get_cols(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}  # 第二列是列名

def add_col(conn, table, name, typ):
    conn.execute(f'ALTER TABLE {table} ADD COLUMN "{name}" {typ}')

def main():
    db = find_db()
    if not db:
        print("ERROR: 未找到数据库（*.db）。请确认 data 目录或项目根目录下的 DB 文件。")
        return

    print("DB:", db)
    conn = sqlite3.connect(db)
    try:
        # 确认表是否存在
        t = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='channels'"
        ).fetchone()
        if not t:
            # 若你删了旧数据，表可能根本不存在；这里给出最小表结构（与导出用到的列匹配）
            print("WARN: 表 'channels' 不存在，正在创建最小结构...")
            conn.execute("""
                CREATE TABLE channels (
                    channel_id TEXT PRIMARY KEY,
                    title TEXT,
                    homepage_url TEXT,
                    youtube_handle TEXT,
                    custom_url TEXT,
                    country TEXT,
                    detected_language TEXT,
                    subscriber_count INTEGER,
                    video_count INTEGER,
                    view_count INTEGER
                )
            """)
            conn.commit()
            print("OK: 已创建 'channels' 表。")
        else:
            # 表存在则补齐缺失列
            cols = get_cols(conn, "channels")
            to_add = [(k, v) for k, v in NEED_COLUMNS.items() if k not in cols]
            if to_add:
                print("补列:", ", ".join([c for c, _ in to_add]))
                for c, typ in to_add:
                    add_col(conn, "channels", c, typ)
                conn.commit()
                print("OK: 列已补齐。")
            else:
                print("OK: 所需列均已存在。")

        # 打印最终列集合
        print("channels 列：", sorted(get_cols(conn, "channels")))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
