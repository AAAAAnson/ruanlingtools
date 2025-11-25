# -*- coding: utf-8 -*-
"""
YouTube Data Repository

Handles database operations for YouTube KOL crawler data
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class YouTubeRepository:
    """YouTube data access layer"""

    def __init__(self, db_path: str = None):
        """
        Initialize repository

        Args:
            db_path: Path to SQLite database (default: ./data/youtube_kol.db)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / 'data' / 'youtube_kol.db')

        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """Ensure database exists and is initialized"""
        db_file = Path(self.db_path)

        if not db_file.exists():
            logger.warning(f"Database not found at {self.db_path}, initializing...")
            # Create parent directory
            db_file.parent.mkdir(parents=True, exist_ok=True)

            # Initialize database
            from tools.init_youtube_db import init_database
            init_database(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn

    def save_search(self, search_data: Dict[str, Any]) -> int:
        """
        Save search record

        Args:
            search_data: Search parameters and results

        Returns:
            Search ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Prepare search params JSON
            search_params = {
                'min_subscribers': search_data.get('min_subscribers'),
                'max_results': search_data.get('max_results'),
                'published_after': search_data.get('published_after'),
                'published_before': search_data.get('published_before'),
                'order_by': search_data.get('order_by', 'relevance')
            }

            cursor.execute("""
                INSERT INTO youtube_searches (
                    keyword, search_params, min_subscribers, max_results,
                    published_after, published_before, order_by,
                    total_channels, total_videos, api_key_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search_data['keyword'],
                json.dumps(search_params),
                search_data.get('min_subscribers', 10000),
                search_data.get('max_results', 50),
                search_data.get('published_after'),
                search_data.get('published_before'),
                search_data.get('order_by', 'relevance'),
                search_data.get('total_channels', 0),
                search_data.get('total_videos', 0),
                search_data.get('api_key_used', '')
            ))

            search_id = cursor.lastrowid
            conn.commit()

            logger.info(f"Saved search record #{search_id} for keyword: {search_data['keyword']}")
            return search_id

        except sqlite3.Error as e:
            logger.error(f"Error saving search: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def save_channel(self, channel_data: Dict[str, Any]):
        """
        Save or update channel data

        Args:
            channel_data: Channel information
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO youtube_channels (
                    channel_id, title, custom_url, description, country,
                    subscriber_count, video_count, view_count, thumbnail_url,
                    published_at, last_updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(channel_id) DO UPDATE SET
                    title = excluded.title,
                    custom_url = excluded.custom_url,
                    description = excluded.description,
                    country = excluded.country,
                    subscriber_count = excluded.subscriber_count,
                    video_count = excluded.video_count,
                    view_count = excluded.view_count,
                    thumbnail_url = excluded.thumbnail_url,
                    last_updated_at = CURRENT_TIMESTAMP
            """, (
                channel_data['channel_id'],
                channel_data.get('channel_title', ''),
                channel_data.get('custom_url', ''),
                channel_data.get('description', ''),
                channel_data.get('country', 'Unknown'),
                channel_data.get('subscriber_count', 0),
                channel_data.get('total_video_count', 0),
                channel_data.get('total_view_count', 0),
                channel_data.get('thumbnail', ''),
                channel_data.get('published_at', '')
            ))

            conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Error saving channel {channel_data.get('channel_id')}: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def save_videos(self, videos: List[Dict[str, Any]]):
        """
        Save multiple videos

        Args:
            videos: List of video data
        """
        if not videos:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            for video in videos:
                cursor.execute("""
                    INSERT OR REPLACE INTO youtube_videos (
                        video_id, channel_id, title, published_at,
                        view_count, like_count, comment_count, engagement_rate,
                        duration_seconds, thumbnail_url, video_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    video['video_id'],
                    video['channel_id'],
                    video.get('title', ''),
                    video.get('published_at', ''),
                    video.get('view_count', 0),
                    video.get('like_count', 0),
                    video.get('comment_count', 0),
                    video.get('engagement_rate', 0.0),
                    video.get('duration_seconds', 0),
                    video.get('thumbnail', ''),
                    video.get('url', '')
                ))

            conn.commit()
            logger.info(f"Saved {len(videos)} videos")

        except sqlite3.Error as e:
            logger.error(f"Error saving videos: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def save_search_channel_association(
        self,
        search_id: int,
        channel_id: str,
        stats: Dict[str, Any],
        rank: int
    ):
        """
        Save search-channel association

        Args:
            search_id: Search record ID
            channel_id: Channel ID
            stats: Channel statistics for this search
            rank: Ranking position in search results
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO youtube_search_channels (
                    search_id, channel_id, keyword_videos_count,
                    keyword_total_views, keyword_avg_views, keyword_avg_engagement,
                    rank_position
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                search_id,
                channel_id,
                stats.get('keyword_videos_count', 0),
                stats.get('keyword_total_views', 0),
                stats.get('keyword_avg_views', 0),
                stats.get('keyword_avg_engagement', 0.0),
                rank
            ))

            conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Error saving search-channel association: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def log_api_usage(self, key_index: int, operation: str, cost: int, details: Dict = None):
        """
        Log API quota usage

        Args:
            key_index: API key index
            operation: Operation type (search, videos, channels)
            cost: API cost in units
            details: Additional request details
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO youtube_api_quota_usage (
                    api_key_index, operation, cost, request_details
                ) VALUES (?, ?, ?, ?)
            """, (
                key_index,
                operation,
                cost,
                json.dumps(details) if details else None
            ))

            conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Error logging API usage: {e}")
            conn.rollback()

        finally:
            conn.close()

    def get_search_history(
        self,
        keyword: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get search history

        Args:
            keyword: Filter by keyword (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of search records
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM youtube_searches WHERE 1=1"
            params = []

            if keyword:
                query += " AND keyword LIKE ?"
                params.append(f"%{keyword}%")

            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date)

            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'keyword': row['keyword'],
                    'search_params': json.loads(row['search_params']) if row['search_params'] else {},
                    'total_channels': row['total_channels'],
                    'total_videos': row['total_videos'],
                    'created_at': row['created_at']
                })

            return results

        finally:
            conn.close()

    def get_search_detail(self, search_id: int) -> Optional[Dict]:
        """
        Get detailed search results

        Args:
            search_id: Search record ID

        Returns:
            Search details with channels and videos
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get search record
            cursor.execute("SELECT * FROM youtube_searches WHERE id = ?", (search_id,))
            search_row = cursor.fetchone()

            if not search_row:
                return None

            # Get channels for this search
            cursor.execute("""
                SELECT c.*, sc.keyword_videos_count, sc.keyword_total_views,
                       sc.keyword_avg_views, sc.keyword_avg_engagement, sc.rank_position
                FROM youtube_channels c
                JOIN youtube_search_channels sc ON c.channel_id = sc.channel_id
                WHERE sc.search_id = ?
                ORDER BY sc.rank_position
            """, (search_id,))

            channels = []
            for row in cursor.fetchall():
                channels.append(dict(row))

            return {
                'id': search_row['id'],
                'keyword': search_row['keyword'],
                'search_params': json.loads(search_row['search_params']) if search_row['search_params'] else {},
                'total_channels': search_row['total_channels'],
                'total_videos': search_row['total_videos'],
                'created_at': search_row['created_at'],
                'channels': channels
            }

        finally:
            conn.close()

    def get_quota_usage_today(self, key_index: Optional[int] = None) -> int:
        """
        Get API quota usage for today

        Args:
            key_index: API key index (optional, returns total if not specified)

        Returns:
            Total quota used today
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT SUM(cost) as total FROM youtube_api_quota_usage WHERE date = DATE('now')"
            params = []

            if key_index is not None:
                query += " AND api_key_index = ?"
                params.append(key_index)

            cursor.execute(query, params)
            row = cursor.fetchone()

            return row['total'] if row['total'] else 0

        finally:
            conn.close()
