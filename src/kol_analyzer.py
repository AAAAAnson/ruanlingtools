"""
YouTube 关键词 KOL 分析模块
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from sqlalchemy import func, desc

from .crawler import YouTubeKOLCrawler
from .database import get_db, Video, Channel
from .utils import parse_iso8601_duration, format_number

class KeywordKOLAnalyzer:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.crawler = YouTubeKOLCrawler(logger=self.logger)
        self.api_manager = self.crawler.api_manager
        self.db = get_db()
        self.stats = {
            'total_videos_found': 0,
            'non_shorts_videos': 0,
            'total_channels': 0,
            'api_calls': 0,
            'errors': 0
        }
    
    def calculate_engagement_rate(self, like_count: int, comment_count: int, view_count: int) -> float:
        """
        计算互动率
        互动率 = (点赞数 + 评论数) / 播放量 * 100
        """
        if view_count == 0:
            return 0.0
        return ((like_count + comment_count) / view_count) * 100
    
    def analyze_keyword(self, keyword: str, start_date: datetime = None, 
                       end_date: datetime = None, get_latest_videos: bool = True):
        self.logger.info(f"开始分析关键词: {keyword}")
        
        # Step 1: 爬取所有视频
        self.logger.info("=" * 60)
        self.logger.info("Step 1: 爬取关键词下的所有视频")
        self.logger.info("=" * 60)
        
        crawl_stats = self.crawler.crawl_keyword(
            keyword=keyword, start_date=start_date, end_date=end_date
        )
        self.stats['total_videos_found'] = crawl_stats['videos_fetched']
        self.logger.info(f"爬取完成，共获取 {self.stats['total_videos_found']} 个视频")
        
        # Step 2: 从数据库提取非Shorts视频
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Step 2: 提取非Shorts视频并按频道汇总")
        self.logger.info("=" * 60)
        
        results = self._analyze_channels_from_db(keyword)
        
        # Step 3: 获取最新视频（可选）
        if get_latest_videos:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Step 3: 获取每个频道的最新10个非Shorts视频")
            self.logger.info("=" * 60)
            results = self._fetch_latest_videos_for_channels(results)
        
        # Step 4: 导出结果
        export_file = self._export_results(keyword, results)
        
        self.logger.info("\n分析完成")
        return {'results': results, 'export_file': export_file, 'stats': self.stats}
    
    def _analyze_channels_from_db(self, keyword: str):
        session = self.db.get_session()
        try:
            channel_summary = session.query(
                Video.channel_id, Video.channel_title,
                func.count(Video.video_id).label('video_count'),
                func.sum(Video.view_count).label('total_views'),
                func.avg(Video.view_count).label('avg_views')
            ).filter(
                Video.keyword == keyword, Video.is_short == 0
            ).group_by(
                Video.channel_id, Video.channel_title
            ).order_by(func.sum(Video.view_count).desc()).all()
            
            self.stats['total_channels'] = len(channel_summary)
            self.logger.info(f"找到 {self.stats['total_channels']} 个频道")
            
            results = []
            for i, (channel_id, channel_title, video_count, total_views, avg_views) in enumerate(channel_summary, 1):
                self.logger.info(f"处理频道 {i}/{self.stats['total_channels']}: {channel_title}")
                
                channel = session.query(Channel).filter_by(channel_id=channel_id).first()
                if not channel:
                    self.logger.warning(f"频道 {channel_id} 信息缺失")
                    continue
                
                # 获取数据库中的最新10条视频（包含互动数据）
                db_latest_videos = session.query(Video).filter(
                    Video.channel_id == channel_id,
                    Video.keyword == keyword,
                    Video.is_short == 0
                ).order_by(desc(Video.published_at)).limit(10).all()
                
                self.stats['non_shorts_videos'] += len(db_latest_videos)
                
                # 计算数据库视频的互动率
                db_videos_data = []
                for v in db_latest_videos:
                    engagement_rate = self.calculate_engagement_rate(
                        v.like_count or 0,
                        v.comment_count or 0,
                        v.view_count or 0
                    )
                    db_videos_data.append({
                        'video_id': v.video_id,
                        'title': v.title,
                        'view_count': v.view_count or 0,
                        'like_count': v.like_count or 0,
                        'comment_count': v.comment_count or 0,
                        'engagement_rate': engagement_rate,
                        'published_at': v.published_at,
                        'url': f"https://youtube.com/watch?v={v.video_id}"
                    })
                
                # 计算数据库视频的平均互动率
                db_avg_engagement = sum(v['engagement_rate'] for v in db_videos_data) / len(db_videos_data) if db_videos_data else 0
                
                results.append({
                    'channel_id': channel_id,
                    'channel_title': channel_title,
                    'homepage_url': channel.homepage_url or f"https://youtube.com/channel/{channel_id}",
                    'youtube_handle': channel.youtube_handle or '',
                    'subscriber_count': channel.subscriber_count,
                    'subscriber_count_display': format_number(channel.subscriber_count),
                    'related_videos_count': video_count,
                    'total_views_in_keyword': int(total_views or 0),
                    'avg_views_in_keyword': int(avg_views or 0),
                    'db_latest_videos': db_videos_data,
                    'db_avg_engagement_rate': db_avg_engagement,
                    'api_latest_videos': []
                })
            return results
        finally:
            session.close()
    
    def _fetch_latest_videos_for_channels(self, channels: List[Dict]):
        total = len(channels)
        self.logger.info(f"开始为 {total} 个频道获取最新视频...")
        
        for i, channel in enumerate(channels, 1):
            self.logger.info(f"[{i}/{total}] {channel['channel_title']}")
            try:
                latest = self._get_channel_latest_videos(channel['channel_id'], 10)
                channel['api_latest_videos'] = latest
                
                # 计算API获取的视频平均播放量
                channel['api_latest_avg_views'] = int(sum(v['view_count'] for v in latest) / len(latest)) if latest else 0
                
                # 计算API获取的视频平均互动率
                channel['api_latest_avg_engagement'] = sum(v['engagement_rate'] for v in latest) / len(latest) if latest else 0
                
            except Exception as e:
                self.logger.error(f"获取失败: {e}")
                self.stats['errors'] += 1
                channel['api_latest_videos'] = []
                channel['api_latest_avg_views'] = 0
                channel['api_latest_avg_engagement'] = 0
        return channels
    
    def _get_channel_latest_videos(self, channel_id: str, limit: int = 10):
        all_videos = []
        page_token = None
        
        for page in range(3):
            try:
                response = self._search_channel_videos(channel_id, page_token, 50)
                self.stats['api_calls'] += 1
                
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                if not video_ids:
                    break
                
                details = self.api_manager.get_videos_details(video_ids)
                self.stats['api_calls'] += 1
                
                for item in details['items']:
                    duration = parse_iso8601_duration(item.get('contentDetails', {}).get('duration', ''))
                    if duration > 60:  # 非Shorts视频
                        stats = item.get('statistics', {})
                        view_count = int(stats.get('viewCount', 0))
                        like_count = int(stats.get('likeCount', 0))
                        comment_count = int(stats.get('commentCount', 0))
                        
                        # 计算互动率
                        engagement_rate = self.calculate_engagement_rate(like_count, comment_count, view_count)
                        
                        all_videos.append({
                            'video_id': item['id'],
                            'title': item['snippet']['title'],
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'engagement_rate': engagement_rate,
                            'published_at': item['snippet']['publishedAt'],
                            'duration_seconds': duration,
                            'url': f"https://youtube.com/watch?v={item['id']}"
                        })
                        if len(all_videos) >= limit:
                            break
                
                if len(all_videos) >= limit:
                    break
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            except Exception as e:
                self.logger.error(f"搜索失败: {e}")
                break
        
        return all_videos[:limit]
    
    def _search_channel_videos(self, channel_id: str, page_token: str = None, max_results: int = 50):
        params = {
            'part': 'id,snippet',
            'channelId': channel_id,
            'type': 'video',
            'order': 'date',
            'maxResults': min(max_results, 50)
        }
        if page_token:
            params['pageToken'] = page_token
        
        request = self.api_manager.youtube.search().list(**params)
        return request.execute()
    
    def _export_results(self, keyword: str, results: List[Dict]):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('./data', exist_ok=True)
        filename = f'./data/kol_analysis_{keyword}_{timestamp}.xlsx'
        
        # Sheet 1: 频道概览
        channels_data = []
        for r in results:
            # 优先使用API获取的数据，否则使用数据库数据
            latest_videos = r.get('api_latest_videos') or r.get('db_latest_videos', [])
            
            # 平均播放量
            avg_latest_views = r.get('api_latest_avg_views') or (
                sum(v['view_count'] for v in latest_videos) / len(latest_videos) if latest_videos else 0
            )
            
            # 平均互动率
            avg_engagement = r.get('api_latest_avg_engagement') or r.get('db_avg_engagement_rate', 0)
            
            channels_data.append({
                '频道ID': r['channel_id'],
                '频道名称': r['channel_title'],
                '主页链接': r['homepage_url'],
                'YouTube Handle': r['youtube_handle'],
                '粉丝数': r['subscriber_count_display'],
                '粉丝数（原始）': r['subscriber_count'],
                f'相关视频数（{keyword}）': r['related_videos_count'],
                f'总播放量（{keyword}）': format_number(r['total_views_in_keyword']),
                f'平均播放量（{keyword}）': format_number(r['avg_views_in_keyword']),
                '最新10视频数量': len(latest_videos),
                '最新10视频平均播放': format_number(int(avg_latest_views)),
                '最新10视频平均互动率(%)': f"{avg_engagement:.2f}%"
            })
        
        channels_df = pd.DataFrame(channels_data)
        
        # Sheet 2: 视频详情（包含互动数据）
        videos_data = []
        for r in results:
            videos = r.get('api_latest_videos') or r.get('db_latest_videos', [])
            for i, v in enumerate(videos, 1):
                videos_data.append({
                    '频道名称': r['channel_title'],
                    '频道粉丝数': r['subscriber_count_display'],
                    '视频序号': i,
                    '视频标题': v['title'],
                    '视频链接': v['url'],
                    '播放量': v['view_count'],
                    '播放量（格式化）': format_number(v['view_count']),
                    '点赞数': v.get('like_count', 0),
                    '评论数': v.get('comment_count', 0),
                    '互动率(%)': f"{v.get('engagement_rate', 0):.2f}%",
                    '发布时间': v['published_at'] if isinstance(v['published_at'], str) else v['published_at'].strftime('%Y-%m-%d %H:%M:%S')
                })
        
        videos_df = pd.DataFrame(videos_data)
        
        # Sheet 3: 汇总
        summary_data = {
            '指标': ['分析关键词', '分析时间', '总视频数', '非Shorts视频数', '频道总数', 'API调用次数', '错误次数'],
            '数值': [keyword, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.stats['total_videos_found'], self.stats['non_shorts_videos'],
                    self.stats['total_channels'], self.stats['api_calls'], self.stats['errors']]
        }
        summary_df = pd.DataFrame(summary_data)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
            channels_df.to_excel(writer, sheet_name='频道概览', index=False)
            videos_df.to_excel(writer, sheet_name='视频详情', index=False)
        
        self.logger.info(f"结果已导出到: {filename}")
        return filename
