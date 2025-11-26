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
from services.youtube_quota_service import YouTubeQuotaService

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
        self.quota_service = YouTubeQuotaService()
        self.quota_used_this_request = 0  # Track quota for current request
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

    def _search_with_pagination(
        self,
        search_params: Dict[str, Any],
        max_pages: int = 3,
        max_total_results: int = 150
    ) -> List[Dict[str, Any]]:
        """
        Search with automatic pagination support

        Args:
            search_params: Search parameters for YouTube API
            max_pages: Maximum number of pages to fetch (0 or -1 = unlimited)
            max_total_results: Maximum total results to fetch (0 = unlimited)

        Returns:
            List of all search result items
        """
        all_items = []
        next_page_token = None
        pages_fetched = 0
        max_retries = len(self.api_keys)

        # Unlimited mode: max_pages = 0 or -1
        unlimited_pages = max_pages <= 0
        unlimited_results = max_total_results <= 0

        while (unlimited_pages or pages_fetched < max_pages) and (unlimited_results or len(all_items) < max_total_results):
            retry_count = 0

            # Add pageToken if this is not the first page
            if next_page_token:
                search_params['pageToken'] = next_page_token

            while retry_count < max_retries:
                try:
                    response = self.youtube.search().list(**search_params).execute()

                    # Record quota usage (search.list = 100 units)
                    self.quota_service.record_quota_usage(
                        api_key_index=self.current_key_index,
                        operation='search',
                        cost=100,
                        request_details={'params': str(search_params)}
                    )
                    self.quota_used_this_request += 100

                    # Add items from this page
                    items = response.get('items', [])
                    all_items.extend(items)

                    # Get next page token
                    next_page_token = response.get('nextPageToken')

                    pages_fetched += 1
                    logger.info(f"Fetched page {pages_fetched}, total items so far: {len(all_items)}")

                    # Break if no more pages
                    if not next_page_token:
                        logger.info("No more pages available")
                        break

                    break  # Success, exit retry loop

                except Exception as e:
                    if str(e) == "QUOTA_EXCEEDED_RETRY":
                        retry_count += 1
                        continue
                    raise

            # If no next page token, stop pagination
            if not next_page_token:
                break

        logger.info(f"Pagination complete: fetched {pages_fetched} pages, {len(all_items)} total items")

        # Return all items in unlimited mode, otherwise trim
        if unlimited_results:
            return all_items
        return all_items[:max_total_results]

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
        save_to_database: bool = True,
        max_pages: int = 3
    ) -> Dict[str, Any]:
        """
        Search for KOLs (influential channels) by keyword with pagination support

        Args:
            keyword: Search keyword
            max_results: Maximum number of results per page (50 max per API)
            min_subscribers: Minimum subscriber count filter
            published_after: ISO 8601 datetime for filtering videos after this date
            published_before: ISO 8601 datetime for filtering videos before this date
            order_by: Sort order (relevance, date, viewCount, rating)
            get_latest_videos: Whether to fetch latest videos for each channel
            save_to_database: Whether to save results to database
            max_pages: Maximum number of pages to fetch (default: 3)

        Returns:
            Dictionary containing KOL analysis results with quota usage info
        """
        try:
            logger.info(f"Searching KOLs for keyword: {keyword}, max_pages: {max_pages}")

            # Reset quota tracking for this request
            self.quota_used_this_request = 0

            channel_ids = set()
            video_ids = []

            # Step 1: Search for channels with pagination (to find channels with keyword in name/description)
            logger.info(f"Step 1: Searching for channels matching '{keyword}'")
            channel_search_params = {
                'q': keyword,
                'part': 'id,snippet',
                'type': 'channel',
                'maxResults': min(max_results, 50),
                'order': order_by,
                'relevanceLanguage': 'en'
            }

            # In unlimited mode, fetch as many as possible
            max_total = 0 if max_pages <= 0 else max_results * max_pages

            channel_items = self._search_with_pagination(
                channel_search_params,
                max_pages=max_pages,
                max_total_results=max_total
            )

            for item in channel_items:
                if item['id'].get('channelId'):
                    channel_ids.add(item['id']['channelId'])

            logger.info(f"Found {len(channel_ids)} channels from channel search")

            # Step 2: Search for videos with pagination (to find channels with videos matching keyword)
            logger.info(f"Step 2: Searching for videos matching '{keyword}'")

            video_search_params = {
                'q': keyword,
                'part': 'id,snippet',
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order_by,
                'relevanceLanguage': 'en'
            }

            # Add time range filters if provided
            if published_after:
                video_search_params['publishedAfter'] = published_after
            if published_before:
                video_search_params['publishedBefore'] = published_before

            video_items = self._search_with_pagination(
                video_search_params,
                max_pages=max_pages,
                max_total_results=max_total
            )

            for item in video_items:
                if item['id'].get('videoId'):
                    video_ids.append(item['id']['videoId'])
                    channel_ids.add(item['snippet']['channelId'])

            logger.info(f"Found {len(video_ids)} videos from {len(channel_ids)} total unique channels")

            if not channel_ids:
                return {
                    'keyword': keyword,
                    'channels': [],
                    'total_videos': 0,
                    'message': 'No channels found matching the keyword'
                }

            # Step 3: Get video details (for engagement data)
            videos_data = {}
            max_retries = len(self.api_keys)
            if video_ids:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        videos_response = self.youtube.videos().list(
                            id=','.join(video_ids),
                            part='statistics,contentDetails,snippet'
                        ).execute()

                        # Record quota usage (videos.list = 1 unit)
                        self.quota_service.record_quota_usage(
                            api_key_index=self.current_key_index,
                            operation='videos',
                            cost=1,
                            request_details={'video_count': len(video_ids)}
                        )
                        self.quota_used_this_request += 1

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

            # Step 4: Get channel details for ALL found channels
            logger.info(f"Step 4: Getting details for {len(channel_ids)} channels")
            channels_list = list(channel_ids)
            kol_results = []

            if channels_list:
                retry_count = 0
                # Process channels in batches of 50 (API limit)
                channels_to_process = []
                for i in range(0, len(channels_list), 50):
                    batch = channels_list[i:i+50]
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            channels_response = self.youtube.channels().list(
                                id=','.join(batch),
                                part='snippet,statistics,brandingSettings'
                            ).execute()

                            # Record quota usage (channels.list = 1 unit)
                            self.quota_service.record_quota_usage(
                                api_key_index=self.current_key_index,
                                operation='channels',
                                cost=1,
                                request_details={'channel_count': len(batch)}
                            )
                            self.quota_used_this_request += 1

                            channels_to_process.extend(channels_response.get('items', []))
                            break
                        except Exception as e:
                            if str(e) == "QUOTA_EXCEEDED_RETRY":
                                retry_count += 1
                                continue
                            raise

                logger.info(f"Retrieved details for {len(channels_to_process)} channels")

                # Step 5: For channels without video data, fetch their latest videos
                for channel in channels_to_process:
                    channel_id = channel['id']
                    stats = channel.get('statistics', {})
                    subscriber_count = int(stats.get('subscriberCount', 0))

                    # Filter by minimum subscribers
                    if subscriber_count < min_subscribers:
                        continue

                    # If channel has no video data yet and get_latest_videos is enabled, fetch them
                    if channel_id not in videos_data and get_latest_videos:
                        logger.info(f"Fetching latest videos for channel: {channel['snippet'].get('title')}")
                        retry_count = 0
                        while retry_count < max_retries:
                            try:
                                # Search for videos from this specific channel
                                channel_videos_params = {
                                    'channelId': channel_id,
                                    'part': 'id,snippet',
                                    'type': 'video',
                                    'maxResults': 10,
                                    'order': 'date'  # Get latest videos
                                }

                                # Add time filters if provided
                                if published_after:
                                    channel_videos_params['publishedAfter'] = published_after
                                if published_before:
                                    channel_videos_params['publishedBefore'] = published_before

                                channel_videos_response = self.youtube.search().list(**channel_videos_params).execute()

                                # Record quota usage (search.list = 100 units)
                                self.quota_service.record_quota_usage(
                                    api_key_index=self.current_key_index,
                                    operation='search',
                                    cost=100,
                                    request_details={'type': 'channel_videos', 'channel_id': channel_id}
                                )
                                self.quota_used_this_request += 100

                                # Collect video IDs from this channel
                                channel_video_ids = []
                                for item in channel_videos_response.get('items', []):
                                    if item['id'].get('videoId'):
                                        channel_video_ids.append(item['id']['videoId'])

                                # Get video details
                                if channel_video_ids:
                                    videos_response = self.youtube.videos().list(
                                        id=','.join(channel_video_ids),
                                        part='statistics,contentDetails,snippet'
                                    ).execute()

                                    # Record quota usage (videos.list = 1 unit)
                                    self.quota_service.record_quota_usage(
                                        api_key_index=self.current_key_index,
                                        operation='videos',
                                        cost=1,
                                        request_details={'video_count': len(channel_video_ids), 'channel_id': channel_id}
                                    )
                                    self.quota_used_this_request += 1

                                    # Initialize videos_data for this channel
                                    videos_data[channel_id] = {
                                        'channel_id': channel_id,
                                        'channel_title': channel['snippet'].get('title'),
                                        'videos': [],
                                        'total_views': 0,
                                        'video_count': 0
                                    }

                                    for video in videos_response.get('items', []):
                                        duration_seconds = self.parse_iso8601_duration(
                                            video.get('contentDetails', {}).get('duration', '')
                                        )

                                        # Include all videos (don't skip Shorts for comprehensive analysis)
                                        stats_v = video.get('statistics', {})
                                        view_count = int(stats_v.get('viewCount', 0))
                                        like_count = int(stats_v.get('likeCount', 0))
                                        comment_count = int(stats_v.get('commentCount', 0))

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

                                break
                            except Exception as e:
                                if str(e) == "QUOTA_EXCEEDED_RETRY":
                                    retry_count += 1
                                    continue
                                # Don't fail if fetching channel videos fails, just log and continue
                                logger.warning(f"Failed to fetch videos for channel {channel_id}: {e}")
                                break

                # Step 6: Build results
                for channel in channels_to_process:
                    channel_id = channel['id']
                    stats = channel.get('statistics', {})
                    subscriber_count = int(stats.get('subscriberCount', 0))

                    # Filter by minimum subscribers
                    if subscriber_count < min_subscribers:
                        continue

                    # Skip channels with no video data
                    if channel_id not in videos_data:
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

            # Prepare result with quota information
            result = {
                'keyword': keyword,
                'channels': kol_results,
                'total_channels': len(kol_results),
                'total_videos': sum(c['keyword_videos_count'] for c in kol_results),
                'timestamp': datetime.now().isoformat(),
                'api_key_used': f"#{self.current_key_index + 1} of {len(self.api_keys)}",
                'quota_used': self.quota_used_this_request,
                'max_pages': max_pages
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
