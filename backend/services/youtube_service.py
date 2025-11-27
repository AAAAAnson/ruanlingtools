# -*- coding: utf-8 -*-
"""
Simple YouTube KOL Search Service
Supports multiple API keys with automatic rotation
"""
import logging
import json
import os
from typing import List, Dict, Any
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Data directory for storing API keys
DATA_DIR = Path(__file__).parent.parent / "data"
KEYS_FILE = DATA_DIR / "youtube_keys.json"


class YouTubeService:
    """Simple YouTube KOL search service with multi-key rotation"""

    def __init__(self):
        """Initialize service with API keys from storage"""
        self.api_keys = self._load_keys()
        if not self.api_keys:
            raise ValueError("No YouTube API keys configured")

        self.current_key_index = 0
        self.youtube = self._build_service()
        logger.info(f"YouTube service initialized with {len(self.api_keys)} key(s)")

    def _load_keys(self) -> List[str]:
        """Load API keys from JSON file"""
        if not KEYS_FILE.exists():
            return []

        try:
            with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('keys', [])
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return []

    @staticmethod
    def save_keys(keys: List[str]):
        """Save API keys to JSON file"""
        DATA_DIR.mkdir(exist_ok=True)

        with open(KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'keys': keys}, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(keys)} API key(s)")

    @staticmethod
    def get_all_keys() -> List[str]:
        """Get all stored API keys"""
        if not KEYS_FILE.exists():
            return []

        try:
            with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('keys', [])
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return []

    def _build_service(self):
        """Build YouTube API service with current key"""
        if self.current_key_index >= len(self.api_keys):
            raise Exception("All API keys exhausted")

        key = self.api_keys[self.current_key_index]
        return build('youtube', 'v3', developerKey=key)

    def _switch_key(self):
        """Switch to next API key"""
        self.current_key_index += 1

        if self.current_key_index >= len(self.api_keys):
            raise Exception("All API keys quota exhausted")

        self.youtube = self._build_service()
        logger.info(f"Switched to key #{self.current_key_index + 1}")

    def _api_call_with_retry(self, func):
        """Execute API call with automatic key rotation on quota errors"""
        max_attempts = len(self.api_keys)

        for attempt in range(max_attempts):
            try:
                return func(self.youtube)
            except HttpError as e:
                error_reason = e.error_details[0].get('reason', '') if e.error_details else ''

                # Quota exceeded - try next key
                if error_reason in ['quotaExceeded', 'dailyLimitExceeded', 'rateLimitExceeded']:
                    logger.warning(f"Key #{self.current_key_index + 1} quota exceeded")

                    if attempt < max_attempts - 1:
                        self._switch_key()
                        continue
                    else:
                        raise Exception("All API keys quota exhausted")
                else:
                    # Other errors
                    raise

    async def search_kols(self, keyword: str, max_results: int = 20, min_subscribers: int = 10000) -> Dict[str, Any]:
        """
        Search for YouTube KOLs by keyword

        Args:
            keyword: Search keyword
            max_results: Maximum number of results (1-50)
            min_subscribers: Minimum subscriber count filter

        Returns:
            Dictionary with search results and statistics
        """
        logger.info(f"Searching KOLs: keyword='{keyword}', max={max_results}, min_subs={min_subscribers}")

        # Step 1: Search for videos
        def search_videos(yt):
            return yt.search().list(
                part='snippet',
                q=keyword,
                type='video',
                maxResults=min(max_results, 50),
                order='relevance',
                relevanceLanguage='en'
            ).execute()

        search_response = self._api_call_with_retry(search_videos)

        if not search_response.get('items'):
            return {
                'keyword': keyword,
                'channels': [],
                'total_channels': 0
            }

        # Step 2: Extract unique channel IDs
        channel_ids = list(set([
            item['snippet']['channelId']
            for item in search_response['items']
        ]))

        # Step 3: Get channel statistics
        def get_channels_stats(yt):
            return yt.channels().list(
                part='snippet,statistics',
                id=','.join(channel_ids)
            ).execute()

        channels_response = self._api_call_with_retry(get_channels_stats)

        # Step 4: Process and filter channels
        kol_channels = []

        for channel in channels_response.get('items', []):
            stats = channel['statistics']
            subscriber_count = int(stats.get('subscriberCount', 0))

            # Filter by minimum subscribers
            if subscriber_count < min_subscribers:
                continue

            video_count = int(stats.get('videoCount', 0))
            view_count = int(stats.get('viewCount', 0))

            # Calculate average views per video
            avg_views = view_count / video_count if video_count > 0 else 0

            kol_channels.append({
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', '')[:200],
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'custom_url': channel['snippet'].get('customUrl', ''),
                'subscriber_count': subscriber_count,
                'video_count': video_count,
                'view_count': view_count,
                'avg_views_per_video': int(avg_views),
                'url': f"https://www.youtube.com/channel/{channel['id']}"
            })

        # Sort by subscriber count
        kol_channels.sort(key=lambda x: x['subscriber_count'], reverse=True)

        logger.info(f"Found {len(kol_channels)} KOL channels")

        return {
            'keyword': keyword,
            'channels': kol_channels,
            'total_channels': len(kol_channels)
        }
