"""
数据库模型定义
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Float, Index, JSON, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Video(Base):
    """视频表"""
    __tablename__ = 'videos'

    video_id = Column(String(50), primary_key=True)
    keyword = Column(String(255), nullable=False)
    title = Column(Text)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(String(50), nullable=False)
    channel_title = Column(String(255))

    # 统计信息（JSON格式存储）
    stats_json = Column(JSON)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # 元数据
    duration = Column(String(50))
    duration_seconds = Column(Integer, default=0)  # 持续时间（秒）
    is_short = Column(Integer, default=0)  # 是否为YouTube Shorts (0=否, 1=是)
    thumbnail_url = Column(Text)
    tags = Column(JSON)
    category_id = Column(String(10))
    language = Column(String(10))

    # 系统字段
    etag = Column(String(255))
    captured_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index('idx_keyword_published', 'keyword', 'published_at'),
        Index('idx_channel_published', 'channel_id', 'published_at'),
        Index('idx_captured_at', 'captured_at'),
    )


class Channel(Base):
    """频道（KOL）表"""
    __tablename__ = 'channels'

    channel_id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    custom_url = Column(String(255))
    
    # 主页链接
    homepage_url = Column(String(255))  # 频道主页完整URL
    youtube_handle = Column(String(100))  # @handle格式的用户名

    # 地理位置
    country = Column(String(10))
    detected_country = Column(String(10))   # 推断的国家
    detected_language = Column(String(10))  # 检测的语言

    # 统计信息
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # 品牌信息（JSON格式）
    branding_json = Column(JSON)
    thumbnail_url = Column(Text)
    banner_url = Column(Text)

    # 社交媒体链接
    social_links = Column(JSON)

    # 系统字段
    etag = Column(String(255))
    created_at = Column(DateTime)
    captured_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index('idx_country', 'country'),
        Index('idx_subscriber_count', 'subscriber_count'),
        Index('idx_updated_at', 'updated_at'),
    )


class FailQueue(Base):
    """错误队列表"""
    __tablename__ = 'fail_queue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=False)  # search, video, channel
    keyword = Column(String(255))
    time_window = Column(String(100))
    page_token = Column(String(255))
    error_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    status = Column(String(20), default='pending')  # pending, retrying, done, dead

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    next_retry_at = Column(DateTime)

    # 索引
    __table_args__ = (
        Index('idx_status_retry', 'status', 'next_retry_at'),
        Index('idx_keyword_status', 'keyword', 'status'),
    )


class ApiUsage(Base):
    """API使用统计表"""
    __tablename__ = 'api_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_index = Column(Integer, nullable=False)
    api_key_prefix = Column(String(10))  # API Key前6位
    endpoint = Column(String(50), nullable=False)  # search, videos, channels
    cost = Column(Integer, nullable=False)  # API配额消耗
    success = Column(Integer, default=1)  # 1成功，0失败
    error_code = Column(String(50))

    timestamp = Column(DateTime, default=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_key_timestamp', 'api_key_index', 'timestamp'),
    )


class Database:
    """数据库管理类"""

    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        self.engine = None
        self.SessionLocal = None
        self.init_database()

    def init_database(self):
        """初始化数据库连接"""
        if self.db_type == 'sqlite':
            db_path = os.getenv('DB_PATH', './data/youtube_kol.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # SQLite 配置
            self.engine = create_engine(
                f'sqlite:///{db_path}',
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30,
                },
                echo=False,
                future=True,
            )

            # SQLAlchemy 2.x：使用 exec_driver_sql 执行 PRAGMA
            with self.engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL")
                conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
                conn.exec_driver_sql("PRAGMA cache_size=10000")
                conn.exec_driver_sql("PRAGMA temp_store=MEMORY")
                conn.exec_driver_sql("PRAGMA foreign_keys=ON")
                conn.commit()

        elif self.db_type == 'mysql':
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '3306'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'youtube_kol'),
            }

            connection_str = (
                f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset=utf8mb4"
            )

            self.engine = create_engine(
                connection_str,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False,
                future=True,
            )

            # MySQL 可选优化（按需启用）
            # with self.engine.connect() as conn:
            #     conn.execute(text("SET SESSION sql_mode=''"))
            #     conn.commit()

        # 创建表
        Base.metadata.create_all(bind=self.engine)

        # 创建 Session
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False, future=True)

    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()


# 单例
_db_instance = None

def get_db():
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
