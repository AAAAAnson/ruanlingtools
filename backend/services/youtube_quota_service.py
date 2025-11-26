# -*- coding: utf-8 -*-
"""
YouTube API Quota Management Service

Tracks and predicts API quota consumption for YouTube Data API v3
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, date
from repositories.youtube_repository import YouTubeRepository

logger = logging.getLogger(__name__)


class YouTubeQuotaService:
    """Service for managing YouTube API quota consumption"""

    # YouTube Data API v3 quota costs
    QUOTA_COSTS = {
        'search': 100,        # search.list
        'videos': 1,          # videos.list
        'channels': 1,        # channels.list
    }

    # Daily quota limit per API key
    DAILY_QUOTA_LIMIT = 10000

    def __init__(self):
        self.repository = YouTubeRepository()

    def estimate_search_quota(
        self,
        max_results: int = 50,
        get_latest_videos: bool = True,
        num_pages: int = 1
    ) -> Dict[str, Any]:
        """
        Estimate API quota consumption for a search operation

        Args:
            max_results: Max results per search
            get_latest_videos: Whether to fetch latest videos for each channel
            num_pages: Number of pages to fetch (0 = unlimited)

        Returns:
            Dictionary with quota estimation details
        """
        # Unlimited mode
        if num_pages <= 0:
            return {
                'estimated_quota': 'Unlimited',
                'unlimited': True,
                'breakdown': {
                    'note': 'Unlimited mode will fetch all available results',
                    'warning': 'This may consume significant API quota',
                    'recommendation': 'Consider starting with limited pages first'
                },
                'estimated_channels': 'Unknown',
                'estimated_videos': 'Unknown',
                'pages': 'Unlimited'
            }

        quota_breakdown = {
            'channel_search': 0,
            'video_search': 0,
            'video_details': 0,
            'channel_details': 0,
            'channel_videos': 0,
            'total': 0
        }

        # 1. Channel search (100 units per page)
        quota_breakdown['channel_search'] = self.QUOTA_COSTS['search'] * num_pages

        # 2. Video search (100 units per page)
        quota_breakdown['video_search'] = self.QUOTA_COSTS['search'] * num_pages

        # 3. Video details (1 unit per 50 videos)
        estimated_videos = min(max_results * num_pages, 50 * num_pages)
        video_detail_calls = (estimated_videos + 49) // 50  # Ceiling division
        quota_breakdown['video_details'] = self.QUOTA_COSTS['videos'] * video_detail_calls

        # 4. Channel details (1 unit per 50 channels)
        estimated_channels = min(max_results * num_pages // 2, 50)  # Assume ~50% unique channels
        channel_detail_calls = (estimated_channels + 49) // 50
        quota_breakdown['channel_details'] = self.QUOTA_COSTS['channels'] * channel_detail_calls

        # 5. Fetch latest videos for each channel (100 + 1 units per channel)
        if get_latest_videos:
            quota_breakdown['channel_videos'] = estimated_channels * (self.QUOTA_COSTS['search'] + self.QUOTA_COSTS['videos'])

        # Calculate total
        quota_breakdown['total'] = sum(quota_breakdown.values())

        return {
            'estimated_quota': quota_breakdown['total'],
            'unlimited': False,
            'breakdown': quota_breakdown,
            'estimated_channels': estimated_channels,
            'estimated_videos': estimated_videos,
            'pages': num_pages
        }

    def record_quota_usage(
        self,
        api_key_index: int,
        operation: str,
        cost: int,
        request_details: Dict[str, Any] = None
    ):
        """
        Record API quota usage to database

        Args:
            api_key_index: Index of API key used
            operation: Operation type (search, videos, channels)
            cost: Quota units consumed
            request_details: Additional details about the request
        """
        try:
            conn = self.repository._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO youtube_api_quota_usage
                (api_key_index, operation, cost, request_details, timestamp, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                api_key_index,
                operation,
                cost,
                str(request_details) if request_details else None,
                datetime.now().isoformat(),
                date.today().isoformat()
            ))

            conn.commit()
            conn.close()

            logger.info(f"Recorded quota usage: {operation} = {cost} units (API key #{api_key_index + 1})")

        except Exception as e:
            logger.error(f"Error recording quota usage: {e}")

    def get_daily_quota_usage(self, target_date: str = None) -> Dict[str, Any]:
        """
        Get quota usage statistics for a specific date

        Args:
            target_date: Date in ISO format (YYYY-MM-DD), defaults to today

        Returns:
            Dictionary with usage statistics
        """
        if target_date is None:
            target_date = date.today().isoformat()

        try:
            conn = self.repository._get_connection()
            cursor = conn.cursor()

            # Get total usage by API key
            cursor.execute("""
                SELECT
                    api_key_index,
                    SUM(cost) as total_cost,
                    COUNT(*) as request_count
                FROM youtube_api_quota_usage
                WHERE date = ?
                GROUP BY api_key_index
                ORDER BY api_key_index
            """, (target_date,))

            key_usage = []
            total_quota_used = 0

            for row in cursor.fetchall():
                key_index = row[0]
                total_cost = row[1]
                request_count = row[2]

                key_usage.append({
                    'api_key_index': key_index,
                    'api_key_label': f"API Key #{key_index + 1}",
                    'quota_used': total_cost,
                    'quota_remaining': self.DAILY_QUOTA_LIMIT - total_cost,
                    'usage_percentage': round((total_cost / self.DAILY_QUOTA_LIMIT) * 100, 2),
                    'request_count': request_count
                })

                total_quota_used += total_cost

            # Get usage by operation type
            cursor.execute("""
                SELECT
                    operation,
                    SUM(cost) as total_cost,
                    COUNT(*) as request_count
                FROM youtube_api_quota_usage
                WHERE date = ?
                GROUP BY operation
            """, (target_date,))

            operation_breakdown = []
            for row in cursor.fetchall():
                operation_breakdown.append({
                    'operation': row[0],
                    'quota_used': row[1],
                    'request_count': row[2]
                })

            conn.close()

            # Calculate statistics
            num_keys = len(key_usage) if key_usage else 1
            total_available = self.DAILY_QUOTA_LIMIT * num_keys
            total_remaining = total_available - total_quota_used

            return {
                'date': target_date,
                'total_quota_used': total_quota_used,
                'total_quota_available': total_available,
                'total_quota_remaining': total_remaining,
                'usage_percentage': round((total_quota_used / total_available) * 100, 2) if total_available > 0 else 0,
                'num_api_keys': num_keys,
                'key_usage': key_usage,
                'operation_breakdown': operation_breakdown,
                'quota_limit_per_key': self.DAILY_QUOTA_LIMIT
            }

        except Exception as e:
            logger.error(f"Error getting daily quota usage: {e}")
            return {
                'date': target_date,
                'error': str(e),
                'total_quota_used': 0,
                'total_quota_available': self.DAILY_QUOTA_LIMIT,
                'total_quota_remaining': self.DAILY_QUOTA_LIMIT
            }

    def get_quota_recommendation(self, num_keys: int, avg_daily_usage: int) -> Dict[str, Any]:
        """
        Provide recommendations for API key management

        Args:
            num_keys: Current number of API keys
            avg_daily_usage: Average daily quota usage

        Returns:
            Dictionary with recommendations
        """
        total_daily_quota = self.DAILY_QUOTA_LIMIT * num_keys
        usage_ratio = avg_daily_usage / total_daily_quota if total_daily_quota > 0 else 0

        recommendation = {
            'current_keys': num_keys,
            'total_daily_quota': total_daily_quota,
            'avg_daily_usage': avg_daily_usage,
            'usage_ratio': round(usage_ratio * 100, 2),
            'status': 'healthy',
            'message': 'Your API quota is sufficient for current usage.',
            'recommended_keys': num_keys,
            'add_keys': 0
        }

        if usage_ratio > 0.9:
            # Critical: Over 90% usage
            recommended_keys = int((avg_daily_usage / self.DAILY_QUOTA_LIMIT) * 1.5) + 1
            recommendation['status'] = 'critical'
            recommendation['message'] = '⚠️ CRITICAL: API quota usage is very high! Risk of hitting daily limit.'
            recommendation['recommended_keys'] = recommended_keys
            recommendation['add_keys'] = recommended_keys - num_keys
        elif usage_ratio > 0.7:
            # Warning: 70-90% usage
            recommended_keys = int((avg_daily_usage / self.DAILY_QUOTA_LIMIT) * 1.3) + 1
            recommendation['status'] = 'warning'
            recommendation['message'] = '⚠️ WARNING: API quota usage is high. Consider adding more keys.'
            recommendation['recommended_keys'] = recommended_keys
            recommendation['add_keys'] = recommended_keys - num_keys
        elif usage_ratio > 0.5:
            # Caution: 50-70% usage
            recommendation['status'] = 'caution'
            recommendation['message'] = '⚡ CAUTION: API quota usage is moderate. Monitor closely.'
        elif usage_ratio < 0.2 and num_keys > 1:
            # Underutilized
            recommendation['status'] = 'underutilized'
            recommendation['message'] = '💡 INFO: API quota is underutilized. You may have excess keys.'

        return recommendation
