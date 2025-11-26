# -*- coding: utf-8 -*-
"""
YouTube API配额监控服务
用于跟踪每个API密钥的使用情况和剩余配额
"""

import sqlite3
import logging
from typing import Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class YouTubeQuotaService:
    """YouTube API配额监控服务"""

    # YouTube API每日配额限制（每个密钥）
    DAILY_QUOTA_LIMIT = 10000

    # API操作配额消耗
    QUOTA_COSTS = {
        'search': 100,
        'videos': 1,
        'channels': 1,
        'commentThreads': 1
    }

    def __init__(self, db_path: str = None):
        """
        初始化配额服务

        Args:
            db_path: SQLite数据库路径，默认为/app/data/youtube_quota.db
        """
        if db_path is None:
            db_path = os.getenv('YOUTUBE_QUOTA_DB_PATH', '/app/data/youtube_quota.db')

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建配额使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_api_quota_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_index INTEGER NOT NULL,
                operation_type TEXT NOT NULL,
                cost INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                request_details TEXT
            )
        ''')

        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_key_timestamp
            ON youtube_api_quota_usage(api_key_index, timestamp)
        ''')

        conn.commit()
        conn.close()

        logger.info(f"YouTube quota database initialized at {self.db_path}")

    def record_usage(self, api_key_index: int, operation_type: str, request_details: str = None):
        """
        记录API使用

        Args:
            api_key_index: API密钥索引（0-based）
            operation_type: 操作类型（search, videos, channels等）
            request_details: 请求详情（可选）
        """
        cost = self.QUOTA_COSTS.get(operation_type, 1)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO youtube_api_quota_usage (api_key_index, operation_type, cost, request_details)
            VALUES (?, ?, ?, ?)
        ''', (api_key_index, operation_type, cost, request_details))

        conn.commit()
        conn.close()

        logger.debug(f"Recorded {operation_type} usage (cost: {cost}) for API key #{api_key_index}")

    def get_all_keys_status(self, num_keys: int) -> Dict[str, Any]:
        """
        获取所有API密钥的状态概览

        Args:
            num_keys: API密钥总数

        Returns:
            Dict: {
                'total': 总数,
                'active': 生效数量,
                'exhausted': 用完数量,
                'keys': [{index, used, remaining, status}, ...]
            }
        """
        today = datetime.now().strftime('%Y-%m-%d')

        keys_status = []
        active_count = 0
        exhausted_count = 0

        for index in range(num_keys):
            used = self.get_key_daily_usage(index, today)
            remaining = max(0, self.DAILY_QUOTA_LIMIT - used)
            status = 'active' if remaining > 0 else 'exhausted'

            if status == 'active':
                active_count += 1
            else:
                exhausted_count += 1

            keys_status.append({
                'index': index,
                'used': used,
                'remaining': remaining,
                'status': status,
                'usage_percent': round((used / self.DAILY_QUOTA_LIMIT) * 100, 2)
            })

        return {
            'total': num_keys,
            'active': active_count,
            'exhausted': exhausted_count,
            'keys': keys_status
        }

    def get_key_daily_usage(self, api_key_index: int, date: str = None) -> int:
        """
        获取单个密钥的每日使用量

        Args:
            api_key_index: 密钥索引
            date: 日期（YYYY-MM-DD），默认今天

        Returns:
            int: 已使用配额
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM(cost) as total_cost
            FROM youtube_api_quota_usage
            WHERE api_key_index = ? AND DATE(timestamp) = ?
        ''', (api_key_index, date))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] is not None else 0

    def get_detailed_keys_info(self, num_keys: int) -> Dict[str, Any]:
        """
        获取所有密钥的详细信息（用于Settings页面）

        Args:
            num_keys: API密钥总数

        Returns:
            Dict: {
                'summary': {总计信息},
                'keys': [{详细信息}, ...]
            }
        """
        today = datetime.now().strftime('%Y-%m-%d')

        total_used = 0
        total_remaining = 0
        keys_details = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for index in range(num_keys):
            # 获取今日使用量
            cursor.execute('''
                SELECT SUM(cost) as total_cost, COUNT(*) as call_count
                FROM youtube_api_quota_usage
                WHERE api_key_index = ? AND DATE(timestamp) = ?
            ''', (index, today))

            result = cursor.fetchone()
            used = result[0] if result[0] is not None else 0
            call_count = result[1] if result[1] is not None else 0

            # 获取最后使用时间
            cursor.execute('''
                SELECT timestamp
                FROM youtube_api_quota_usage
                WHERE api_key_index = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (index,))

            last_used_result = cursor.fetchone()
            last_used = last_used_result[0] if last_used_result else None

            remaining = max(0, self.DAILY_QUOTA_LIMIT - used)
            status = 'active' if remaining > 0 else 'exhausted'

            total_used += used
            total_remaining += remaining

            keys_details.append({
                'index': index,
                'used': used,
                'remaining': remaining,
                'status': status,
                'usage_percent': round((used / self.DAILY_QUOTA_LIMIT) * 100, 2),
                'call_count': call_count,
                'last_used': last_used
            })

        conn.close()

        return {
            'summary': {
                'total_keys': num_keys,
                'total_used': total_used,
                'total_remaining': total_remaining,
                'total_quota': num_keys * self.DAILY_QUOTA_LIMIT,
                'usage_percent': round((total_used / (num_keys * self.DAILY_QUOTA_LIMIT)) * 100, 2) if num_keys > 0 else 0
            },
            'keys': keys_details
        }
