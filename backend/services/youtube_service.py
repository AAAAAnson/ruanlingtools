# -*- coding: utf-8 -*-
"""
YouTube KOL Search Service with Multi-Key Support

Supports multiple API keys with automatic rotation on quota exhaustion
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

logger = logging.getLogger(__name__)


class YouTubeService:
    """YouTube API service for KOL search with multi-key support"""

    def __init__(self, api_keys: Optional[List[str]] = None):
        """
        Initialize YouTube service

        Args:
            api_keys: List of YouTube Data API keys (optional, will load from settings)
        """
        # Import here to avoid circular dependency
        from services.settings_service import get_settings_service

        if api_keys:
            self.api_keys = api_keys
        else:
            # Load from settings service
            settings_service = get_settings_service()
            self.api_keys = settings_service.get_youtube_keys()

        if not self.api_keys:
            raise ValueError("No YouTube API keys configured")

        self.current_key_index = 0
        self.youtube = self._build_service()
        logger.info(f"YouTube service initialized with {len(self.api_keys)} API key(s)")

    def _build_service(self):
        """Build YouTube service with current API key"""
        if self.current_key_index >= len(self.api_keys):
            raise Exception("All API keys exhausted")

        current_key = self.api_keys[self.current_key_index]
        logger.info(f"Using API key #{self.current_key_index + 1} (***{current_key[-6:]})")
        return build('youtube', 'v3', developerKey=current_key)

    def _switch_key(self):
        """Switch to next available API key"""
        self.current_key_index += 1

        if self.current_key_index >= len(self.api_keys):
            logger.warning("All API keys exhausted")
            raise Exception("All API keys have been exhausted. Please try again later or add more keys.")

        self.youtube = self._build_service()
        logger.info(f"Switched to API key #{self.current_key_index + 1}")

    def _execute_with_retry(self, request):
        """Execute API request with automatic key rotation on quota errors"""
        max_retries = len(self.api_keys)
        attempts = 0

        while attempts < max_retries:
            try:
                return request.execute()
            except HttpError as e:
                error_reason = e.error_details[0].get('reason', '') if e.error_details else ''

                # Check if quota exceeded
                if error_reason in ['quotaExceeded', 'dailyLimitExceeded']:
                    logger.warning(f"API key #{self.current_key_index + 1} quota exceeded")
                    attempts += 1

                    if attempts < max_retries:
                        # Try next key
                        self._switch_key()
                        # Rebuild the request with new service
                        # Note: Caller needs to handle request rebuild
                        raise Exception("QUOTA_EXCEEDED_RETRY")
                    else:
                        raise Exception("All API keys quota exceeded")
                else:
                    # Other HTTP errors
                    raise

    def parse_iso8601_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration format to seconds

        Args:
            duration_str: ISO 8601 duration string (e.g., PT4M13S)

        Returns:
            Duration in seconds
        """
        if not duration_str:
            return 0

        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def calculate_engagement_rate(self, like_count: int, comment_count: int, view_count: int) -> float:
        """
        Calculate engagement rate

        Engagement Rate = (Likes + Comments) / Views * 100

        Args:
            like_count: Number of likes
            comment_count: Number of comments
            view_count: Number of views

        Returns:
            Engagement rate as percentage
        """
        if view_count == 0:
            return 0.0
        return ((like_count + comment_count) / view_count) * 100

    def format_number(self, num: int) -> str:
        """Format number for display (e.g., 1.2K, 3.4M)"""
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        elif num < 1000000000:
            return f"{num/1000000:.1f}M"
        else:
            return f"{num/1000000000:.1f}B"

    async def search_kols(
        self,
        keyword: str,
        max_results: int = 50,
        min_subscribers: int = 10000,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        order_by: str = "relevance",
        get_latest_videos: bool = True,
        save_to_database: bool = True
    ) -> Dict[str, Any]:
        """
        Search for KOLs (influential channels) by keyword

        Args:
            keyword: Search keyword
            max_results: Maximum number of results
            min_subscribers: Minimum subscriber count filter

        Returns:
            Dictionary containing KOL analysis results
        """
        try:
            logger.info(f"Searching KOLs for keyword: {keyword}")

            # Step 1: Search for videos with retry logic
            retry_count = 0
            max_retries = len(self.api_keys)

            while retry_count < max_retries:
                try:
                    # Build search parameters
                    search_params = {
                        'q': keyword,
                        'part': 'id,snippet',
                        'type': 'video',
                        'maxResults': min(max_results, 50),
                        'order': order_by,
                        'relevanceLanguage': 'en'
                    }

                    # Add time range filters if provided
                    if published_after:
                        search_params['publishedAfter'] = published_after
                    if published_before:
                        search_params['publishedBefore'] = published_before

                    search_response = self.youtube.search().list(**search_params).execute()
                    break  # Success, exit retry loop
                except Exception as e:
                    if str(e) == "QUOTA_EXCEEDED_RETRY":
                        retry_count += 1
                        continue
                    raise

            if not search_response.get('items'):
                return {
                    'keyword': keyword,
                    'channels': [],
                    'total_videos': 0,
                    'message': 'No results found'
                }

            # Step 2: Extract video IDs and channel IDs
            video_ids = []
            channel_ids = set()

            for item in search_response['items']:
                if item['id'].get('videoId'):
                    video_ids.append(item['id']['videoId'])
                    channel_ids.add(item['snippet']['channelId'])

            # Step 3: Get video details (for engagement data)
            videos_data = {}
            if video_ids:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        videos_response = self.youtube.videos().list(
                            id=','.join(video_ids),
                            part='statistics,contentDetails,snippet'
                        ).execute()
                        break
                    except Exception as e:
                        if str(e) == "QUOTA_EXCEEDED_RETRY":
                            retry_count += 1
                            continue
                        raise

                for video in videos_response.get('items', []):
                    duration_seconds = self.parse_iso8601_duration(
                        video.get('contentDetails', {}).get('duration', '')
                    )

                    # Skip Shorts (videos <= 60 seconds)
                    if duration_seconds <= 60:
                        continue

                    stats = video.get('statistics', {})
                    view_count = int(stats.get('viewCount', 0))
                    like_count = int(stats.get('likeCount', 0))
                    comment_count = int(stats.get('commentCount', 0))

                    channel_id = video['snippet']['channelId']

                    if channel_id not in videos_data:
                        videos_data[channel_id] = {
                            'channel_id': channel_id,
                            'channel_title': video['snippet']['channelTitle'],
                            'videos': [],
                            'total_views': 0,
                            'video_count': 0
                        }

                    engagement_rate = self.calculate_engagement_rate(
                        like_count, comment_count, view_count
                    )

                    videos_data[channel_id]['videos'].append({
                        'video_id': video['id'],
                        'title': video['snippet']['title'],
                        'view_count': view_count,
                        'like_count': like_count,
                        'comment_count': comment_count,
                        'engagement_rate': engagement_rate,
                        'published_at': video['snippet']['publishedAt'],
                        'thumbnail': video['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                        'url': f"https://youtube.com/watch?v={video['id']}"
                    })

                    videos_data[channel_id]['total_views'] += view_count
                    videos_data[channel_id]['video_count'] += 1

            # Step 4: Get channel details
            channels_list = list(videos_data.keys())
            kol_results = []

            if channels_list:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        channels_response = self.youtube.channels().list(
                            id=','.join(channels_list),
                            part='snippet,statistics,brandingSettings'
                        ).execute()
                        break
                    except Exception as e:
                        if str(e) == "QUOTA_EXCEEDED_RETRY":
                            retry_count += 1
                            continue
                        raise

                for channel in channels_response.get('items', []):
                    channel_id = channel['id']
                    if channel_id not in videos_data:
                        continue

                    stats = channel.get('statistics', {})
                    subscriber_count = int(stats.get('subscriberCount', 0))

                    # Filter by minimum subscribers
                    if subscriber_count < min_subscribers:
                        continue

                    snippet = channel.get('snippet', {})
                    video_data = videos_data[channel_id]

                    # Calculate average engagement rate
                    avg_engagement = sum(
                        v['engagement_rate'] for v in video_data['videos']
                    ) / len(video_data['videos']) if video_data['videos'] else 0

                    # Calculate average views
                    avg_views = (
                        video_data['total_views'] / video_data['video_count']
                        if video_data['video_count'] > 0 else 0
                    )

                    kol_results.append({
                        'channel_id': channel_id,
                        'channel_title': snippet.get('title', ''),
                        'channel_url': f"https://youtube.com/channel/{channel_id}",
                        'custom_url': snippet.get('customUrl', ''),
                        'description': snippet.get('description', '')[:200],  # Truncate
                        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'country': snippet.get('country', 'Unknown'),
                        'subscriber_count': subscriber_count,
                        'subscriber_count_formatted': self.format_number(subscriber_count),
                        'total_video_count': int(stats.get('videoCount', 0)),
                        'total_view_count': int(stats.get('viewCount', 0)),
                        'keyword_videos_count': video_data['video_count'],
                        'keyword_total_views': video_data['total_views'],
                        'keyword_avg_views': int(avg_views),
                        'keyword_avg_engagement': round(avg_engagement, 2),
                        'latest_videos': video_data['videos'][:5]  # Top 5 videos
                    })

            # Sort by subscriber count
            kol_results.sort(key=lambda x: x['subscriber_count'], reverse=True)

            # Prepare result
            result = {
                'keyword': keyword,
                'channels': kol_results,
                'total_channels': len(kol_results),
                'total_videos': sum(c['keyword_videos_count'] for c in kol_results),
                'timestamp': datetime.now().isoformat(),
                'api_key_used': f"#{self.current_key_index + 1} of {len(self.api_keys)}"
            }

            # Save to database if requested
            if save_to_database and kol_results:
                try:
                    from repositories.youtube_repository import YouTubeRepository

                    repo = YouTubeRepository()

                    # Save search record
                    search_data = {
                        'keyword': keyword,
                        'min_subscribers': min_subscribers,
                        'max_results': max_results,
                        'published_after': published_after,
                        'published_before': published_before,
                        'order_by': order_by,
                        'total_channels': len(kol_results),
                        'total_videos': sum(c['keyword_videos_count'] for c in kol_results),
                        'api_key_used': result['api_key_used']
                    }
                    search_id = repo.save_search(search_data)

                    # Save channels and videos
                    for rank, channel in enumerate(kol_results, 1):
                        # Save channel
                        repo.save_channel(channel)

                        # Save videos
                        if channel.get('latest_videos'):
                            videos_to_save = []
                            for video in channel['latest_videos']:
                                video['channel_id'] = channel['channel_id']
                                videos_to_save.append(video)
                            repo.save_videos(videos_to_save)

                        # Save search-channel association
                        repo.save_search_channel_association(
                            search_id=search_id,
                            channel_id=channel['channel_id'],
                            stats={
                                'keyword_videos_count': channel['keyword_videos_count'],
                                'keyword_total_views': channel['keyword_total_views'],
                                'keyword_avg_views': channel['keyword_avg_views'],
                                'keyword_avg_engagement': channel['keyword_avg_engagement']
                            },
                            rank=rank
                        )

                    result['search_id'] = search_id
                    logger.info(f"Saved search #{search_id} to database")

                except Exception as e:
                    logger.error(f"Error saving to database: {e}", exc_info=True)
                    # Don't fail the request if database save fails

            return result

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            error_details = e.error_details[0] if e.error_details else {}
            raise Exception(f"YouTube API Error: {error_details.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error searching KOLs: {e}", exc_info=True)
            raise Exception(f"Failed to search KOLs: {str(e)}")

    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get detailed channel information

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dictionary containing channel information
        """
        try:
            retry_count = 0
            max_retries = len(self.api_keys)

            while retry_count < max_retries:
                try:
                    response = self.youtube.channels().list(
                        id=channel_id,
                        part='snippet,statistics,brandingSettings,contentDetails'
                    ).execute()
                    break
                except Exception as e:
                    if str(e) == "QUOTA_EXCEEDED_RETRY":
                        retry_count += 1
                        continue
                    raise

            if not response.get('items'):
                raise Exception(f"Channel not found: {channel_id}")

            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            stats = channel.get('statistics', {})

            return {
                'channel_id': channel_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'custom_url': snippet.get('customUrl', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'country': snippet.get('country', 'Unknown'),
                'published_at': snippet.get('publishedAt', ''),
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'channel_url': f"https://youtube.com/channel/{channel_id}"
            }

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise Exception(f"YouTube API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting channel info: {e}", exc_info=True)
            raise Exception(f"Failed to get channel information: {str(e)}")
