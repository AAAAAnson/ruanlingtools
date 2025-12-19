# -*- coding: utf-8 -*-
"""
Reddit Keyword Search Service

Searches Reddit posts by keyword and exports to Excel
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import praw
from praw.models import Submission

logger = logging.getLogger(__name__)


class RedditService:
    """Reddit API service for keyword search"""

    def __init__(self, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """
        Initialize Reddit service

        Args:
            client_id: Reddit application client ID
            client_secret: Reddit application client secret
            user_agent: User agent string
        """
        # Import here to avoid circular dependency
        from services.settings_service import get_settings_service

        if client_id and client_secret and user_agent:
            self.client_id = client_id
            self.client_secret = client_secret
            self.user_agent = user_agent
        else:
            # Load from settings service
            settings_service = get_settings_service()
            reddit_config = settings_service.get_reddit_config()

            if not reddit_config:
                raise ValueError("No Reddit API credentials configured")

            self.client_id = reddit_config.get('client_id')
            self.client_secret = reddit_config.get('client_secret')
            self.user_agent = reddit_config.get('user_agent')

        if not all([self.client_id, self.client_secret, self.user_agent]):
            raise ValueError("Reddit API credentials are incomplete")

        # Initialize Reddit instance
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            check_for_async=False
        )

        logger.info("Reddit service initialized successfully")

    def _is_promoted_post(self, submission: Submission) -> bool:
        """
        Check if a post is a promoted/advertisement post

        Args:
            submission: Reddit submission object

        Returns:
            True if post is promoted, False otherwise
        """
        # Check if post is distinguished (mod/admin posts)
        if submission.distinguished:
            return True

        # Check if post is stickied
        if submission.stickied:
            return True

        # Check if post is promoted (Reddit ads)
        if hasattr(submission, 'promoted') and submission.promoted:
            return True

        # Check for common promotional indicators in title
        promo_keywords = ['[ad]', '[sponsored]', '[promotion]', '[promo]']
        title_lower = submission.title.lower()
        if any(keyword in title_lower for keyword in promo_keywords):
            return True

        return False

    def _filter_by_time_range(self, created_utc: float, years: int = 3) -> bool:
        """
        Check if post is within the specified time range

        Args:
            created_utc: Post creation timestamp (UTC)
            years: Number of years to look back

        Returns:
            True if post is within range, False otherwise
        """
        cutoff_date = datetime.now() - timedelta(days=years * 365)
        post_date = datetime.fromtimestamp(created_utc)
        return post_date >= cutoff_date

    async def search_posts(
        self,
        keyword: str,
        subreddit: str = "all",
        limit: int = 100,
        min_comments: int = 0,
        min_score: int = 0,
        time_range_years: int = 3
    ) -> Dict[str, Any]:
        """
        Search Reddit posts by keyword

        Args:
            keyword: Search keyword
            subreddit: Subreddit name (default: "all" for site-wide search)
            limit: Maximum number of results to return
            min_comments: Minimum number of comments filter
            min_score: Minimum score (upvotes) filter
            time_range_years: Filter posts within this many years (default: 3)

        Returns:
            Dictionary containing search results
        """
        try:
            logger.info(f"Searching Reddit for keyword: {keyword}")

            # Search in specified subreddit
            target_subreddit = self.reddit.subreddit(subreddit)

            # Search posts sorted by relevance
            # Note: Reddit API doesn't support exact time range, so we'll filter manually
            search_results = target_subreddit.search(
                query=keyword,
                sort='relevance',
                time_filter='all',  # Get all, then filter by our custom time range
                limit=limit * 3  # Get more to account for filtering
            )

            posts_data = []
            processed_count = 0

            for submission in search_results:
                # Stop if we have enough results
                if len(posts_data) >= limit:
                    break

                processed_count += 1

                # Filter: Skip promoted posts
                if self._is_promoted_post(submission):
                    logger.debug(f"Skipping promoted post: {submission.id}")
                    continue

                # Filter: Check time range (last 3 years)
                if not self._filter_by_time_range(submission.created_utc, time_range_years):
                    logger.debug(f"Skipping old post: {submission.id}")
                    continue

                # Filter: Minimum comments
                if submission.num_comments < min_comments:
                    continue

                # Filter: Minimum score
                if submission.score < min_score:
                    continue

                # Get post data
                post_data = self._extract_post_data(submission)
                posts_data.append(post_data)

            logger.info(f"Found {len(posts_data)} posts (processed {processed_count} total)")

            return {
                'keyword': keyword,
                'subreddit': subreddit,
                'posts': posts_data,
                'total': len(posts_data),
                'filters': {
                    'min_comments': min_comments,
                    'min_score': min_score,
                    'time_range_years': time_range_years,
                    'exclude_promoted': True
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}", exc_info=True)
            raise Exception(f"Failed to search Reddit: {str(e)}")

    def _extract_post_data(self, submission: Submission) -> Dict[str, Any]:
        """
        Extract relevant data from Reddit submission

        Args:
            submission: Reddit submission object

        Returns:
            Dictionary containing post data
        """
        # Format creation time
        created_time = datetime.fromtimestamp(submission.created_utc)

        # Get author name (handle deleted accounts)
        author_name = str(submission.author) if submission.author else "[deleted]"

        # Get post URL
        post_url = f"https://reddit.com{submission.permalink}"

        # Get post content (for text posts)
        post_content = ""
        if submission.is_self:
            post_content = submission.selftext[:1000]  # Limit to 1000 chars

        return {
            'id': submission.id,
            'title': submission.title,
            'url': post_url,
            'author': author_name,
            'subreddit': submission.subreddit.display_name,
            'subreddit_subscribers': submission.subreddit.subscribers,
            'created_time': created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'created_timestamp': created_time.isoformat(),
            'score': submission.score,
            'upvote_ratio': round(submission.upvote_ratio * 100, 2),
            'num_comments': submission.num_comments,
            'num_awards': submission.total_awards_received,
            'is_text_post': submission.is_self,
            'is_video': submission.is_video,
            'post_content': post_content,
            'domain': submission.domain,
            'link_flair_text': submission.link_flair_text if submission.link_flair_text else "",
            'over_18': submission.over_18
        }

    def format_for_export(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format search results for Excel export

        Args:
            results: Search results from search_posts()

        Returns:
            List of dictionaries formatted for Excel export
        """
        export_data = []

        for post in results['posts']:
            export_data.append({
                '标题 (Title)': post['title'],
                '链接 (URL)': post['url'],
                '发布时间 (Published)': post['created_time'],
                '评论数 (Comments)': post['num_comments'],
                '点赞数 (Score)': post['score'],
                '点赞率 (Upvote %)': f"{post['upvote_ratio']}%",
                '奖励数 (Awards)': post['num_awards'],
                '作者 (Author)': post['author'],
                'Subreddit': post['subreddit'],
                'Subreddit订阅数 (Subscribers)': post['subreddit_subscribers'],
                '类型 (Type)': 'Text' if post['is_text_post'] else ('Video' if post['is_video'] else 'Link'),
                '域名 (Domain)': post['domain'],
                '标签 (Flair)': post['link_flair_text'],
                'NSFW': 'Yes' if post['over_18'] else 'No'
            })

        return export_data
