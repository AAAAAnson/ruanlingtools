"""
YouTube KOL爬虫核心模块
实现全时间窗视频抓取和频道信息汇总
"""
import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict
import pytz
from dotenv import load_dotenv

from .database import get_db, Video, Channel, FailQueue, ApiUsage
from .api_manager import YouTubeAPIManager
from .language_detector import LanguageDetector
from .utils import (
    format_iso8601_time,
    parse_iso8601_duration,
    extract_country_from_text,
    get_shard_keywords,
    should_process_keyword
)

load_dotenv()

class YouTubeKOLCrawler:
    """YouTube KOL爬虫"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.api_manager = YouTubeAPIManager(logger=self.logger)
        self.db = get_db()
        self.language_detector = LanguageDetector()
        
        # 配置
        self.sample_size = int(os.getenv('SAMPLE_SIZE', '100'))
        self.auto_expand = os.getenv('AUTO_EXPAND_KEYS', '0') == '1'
        self.shard_id = int(os.getenv('SHARD_ID', '0'))
        self.shard_count = int(os.getenv('SHARD_COUNT', '1'))
        
        # 统计
        self.stats = {
            'videos_fetched': 0,
            'videos_inserted': 0,
            'channels_fetched': 0,
            'channels_inserted': 0,
            'errors': 0,
            'api_calls': 0,
            'api_cost': 0
        }
    
    def crawl_keyword(self, 
                      keyword: str,
                      start_date: datetime = None,
                      end_date: datetime = None,
                      max_results: int = None) -> Dict[str, Any]:
        """爬取指定关键词的视频"""
        
        # 检查是否应该处理这个关键词（分片）
        if not should_process_keyword(keyword, self.shard_id, self.shard_count):
            self.logger.info(f"Skipping keyword '{keyword}' (not in shard {self.shard_id})")
            return self.stats
        
        self.logger.info(f"Starting crawl for keyword: {keyword}")
        
        # 设置时间范围
        if not start_date:
            start_date = datetime(2005, 4, 23, tzinfo=pytz.UTC)  # YouTube创立日期
        if not end_date:
            end_date = datetime.now(pytz.UTC)
        
        # 先进行成本预估
        if self.auto_expand:
            estimated_cost = self._estimate_cost(keyword, start_date, end_date)
            if not self._check_and_expand_keys(estimated_cost):
                self.logger.error("Insufficient API quota and auto-expansion failed")
                return self.stats
        
        # 时间窗口切分爬取
        self._crawl_time_windows(keyword, start_date, end_date, max_results)
        
        # 汇总频道信息
        self._aggregate_channels(keyword)
        
        self.logger.info(f"Crawl completed for keyword: {keyword}")
        self.logger.info(f"Stats: {self.stats}")
        
        return self.stats
    
    def _estimate_cost(self, keyword: str, start_date: datetime, end_date: datetime) -> int:
        """估算API成本"""
        self.logger.info("Estimating API cost...")
        
        # 采样几个时间窗口
        sample_windows = self._generate_sample_windows(start_date, end_date, 5)
        total_videos = 0
        
        for window_start, window_end in sample_windows:
            try:
                response = self.api_manager.search_videos(
                    q=keyword,
                    published_after=format_iso8601_time(window_start),
                    published_before=format_iso8601_time(window_end),
                    max_results=1
                )
                
                # 获取总结果数（注意：这只是估算）
                total_results = response.get('pageInfo', {}).get('totalResults', 0)
                total_videos += min(total_results, 500)  # YouTube API最多返回500个结果
                
            except Exception as e:
                self.logger.warning(f"Error during cost estimation: {e}")
        
        # 根据采样推算总量
        days_sampled = sum((end - start).days for start, end in sample_windows)
        total_days = (end_date - start_date).days
        estimated_total = int(total_videos * total_days / max(days_sampled, 1))
        
        # 计算API成本
        search_calls = (estimated_total + 49) // 50
        video_calls = (estimated_total + 49) // 50
        channel_calls = (estimated_total * 0.8 + 49) // 50  # 假设80%是不同的频道
        
        total_cost = (search_calls * 100) + video_calls + channel_calls
        
        self.logger.info(f"Estimated videos: {estimated_total}")
        self.logger.info(f"Estimated API cost: {total_cost} units")
        
        return total_cost
    
    def _generate_sample_windows(self, start_date: datetime, end_date: datetime, count: int) -> List[Tuple[datetime, datetime]]:
        """生成采样时间窗口"""
        windows = []
        total_duration = end_date - start_date
        window_size = total_duration / (count + 1)
        
        for i in range(count):
            window_start = start_date + window_size * i
            window_end = window_start + timedelta(days=7)  # 7天窗口
            if window_end > end_date:
                window_end = end_date
            windows.append((window_start, window_end))
        
        return windows
    
    def _check_and_expand_keys(self, required_cost: int) -> bool:
        """检查配额并自动扩容"""
        remaining = self.api_manager.get_remaining_quota()
        
        if remaining >= required_cost:
            return True
        
        if not self.auto_expand:
            self.logger.warning(f"Insufficient quota: need {required_cost}, have {remaining}")
            return False
        
        # TODO: 实现自动创建新的API Key逻辑
        # 这里需要调用外部脚本或API来创建新的Google Cloud项目和Key
        self.logger.warning("Auto-expansion not implemented yet")
        return False
    
    def _crawl_time_windows(self, 
                           keyword: str,
                           start_date: datetime,
                           end_date: datetime,
                           max_results: int = None):
        """按时间窗口爬取"""
        
        # 初始时间窗口大小（天）
        window_sizes = [365, 180, 90, 30, 7, 1]
        current_window_index = 0
        
        current_start = start_date
        total_fetched = 0
        
        while current_start < end_date:
            if max_results and total_fetched >= max_results:
                break
            
            # 计算窗口结束时间
            window_size = window_sizes[min(current_window_index, len(window_sizes) - 1)]
            current_end = min(current_start + timedelta(days=window_size), end_date)
            
            # 爬取当前窗口
            window_results = self._crawl_single_window(
                keyword, 
                current_start, 
                current_end,
                max_results - total_fetched if max_results else None
            )
            
            total_fetched += window_results
            
            # 动态调整窗口大小
            if window_results >= 450:  # 接近API限制，缩小窗口
                current_window_index = min(current_window_index + 1, len(window_sizes) - 1)
            elif window_results < 50 and current_window_index > 0:  # 结果太少，扩大窗口
                current_window_index -= 1
            
            # 移动到下一个窗口
            current_start = current_end
            
            # 进度输出（供PowerShell解析）
            self._output_progress()
    
    def _crawl_single_window(self,
                            keyword: str,
                            start_date: datetime,
                            end_date: datetime,
                            max_results: int = None) -> int:
        """爬取单个时间窗口"""
        
        self.logger.info(f"Crawling window: {start_date.date()} to {end_date.date()}")
        
        page_token = None
        window_fetched = 0
        
        while True:
            try:
                # 搜索视频
                response = self.api_manager.search_videos(
                    q=keyword,
                    published_after=format_iso8601_time(start_date),
                    published_before=format_iso8601_time(end_date),
                    page_token=page_token,
                    max_results=50,
                    order='date'
                )
                
                self.stats['api_calls'] += 1
                
                # 提取视频ID
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                if video_ids:
                    # 获取视频详情
                    self._fetch_and_save_videos(video_ids, keyword)
                    window_fetched += len(video_ids)
                
                # 检查是否有下一页
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                
                # 检查是否达到限制
                if max_results and window_fetched >= max_results:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in window crawl: {e}")
                self._add_to_fail_queue(
                    'search',
                    keyword,
                    f"{start_date.isoformat()}|{end_date.isoformat()}",
                    page_token,
                    str(e)
                )
                break
        
        return window_fetched
    
    def _fetch_and_save_videos(self, video_ids: List[str], keyword: str):
        """获取并保存视频详情"""
        try:
            # 获取视频详情
            response = self.api_manager.get_videos_details(video_ids)
            self.stats['api_calls'] += 1
            
            session = self.db.get_session()
            channel_ids = []
            
            for item in response.get('items', []):
                try:
                    # 提取视频信息
                    video_data = self._extract_video_data(item, keyword)
                    
                    # 保存到数据库
                    existing = session.query(Video).filter_by(video_id=video_data['video_id']).first()
                    
                    if existing:
                        # 更新现有记录
                        for key, value in video_data.items():
                            setattr(existing, key, value)
                    else:
                        # 创建新记录
                        video = Video(**video_data)
                        session.add(video)
                        self.stats['videos_inserted'] += 1
                    
                    self.stats['videos_fetched'] += 1
                    
                    # 收集频道ID
                    channel_ids.append(item['snippet']['channelId'])
                    
                except Exception as e:
                    self.logger.error(f"Error saving video {item.get('id')}: {e}")
                    self.stats['errors'] += 1
            
            session.commit()
            session.close()
            
            # 获取频道详情
            if channel_ids:
                self._fetch_and_save_channels(channel_ids)
                
        except Exception as e:
            self.logger.error(f"Error fetching video details: {e}")
            self._add_to_fail_queue('videos', keyword, None, None, str(e))
    
    def _extract_video_data(self, item: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """提取视频数据"""
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        
        # 检测语言
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        detected_lang = self.language_detector.detect_language(f"{title} {description}")
        
        # 解析视频时长
        duration_str = content_details.get('duration', '')
        duration_seconds = parse_iso8601_duration(duration_str)
        
        # 判断是否为YouTube Shorts
        # 标准：1. 时长<=60秒 2. 标题或描述包含#Shorts
        is_short = 0
        if duration_seconds > 0 and duration_seconds <= 60:
            is_short = 1
        elif '#shorts' in title.lower() or '#shorts' in description.lower():
            is_short = 1
        elif '\n#shorts' in description.lower() or ' #shorts' in description.lower():
            is_short = 1
        
        return {
            'video_id': item['id'],
            'keyword': keyword,
            'title': title,
            'description': description[:5000],  # 限制长度
            'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
            'channel_id': snippet['channelId'],
            'channel_title': snippet.get('channelTitle'),
            'stats_json': statistics,
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration': duration_str,
            'duration_seconds': duration_seconds,
            'is_short': is_short,  # 添加Shorts判断
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            'tags': snippet.get('tags', [])[:50],  # 限制标签数量
            'category_id': snippet.get('categoryId'),
            'language': detected_lang,
            'etag': item.get('etag'),
            'captured_at': datetime.utcnow()
        }
    
    def _fetch_and_save_channels(self, channel_ids: List[str]):
        """获取并保存频道详情"""
        try:
            # 去重
            unique_ids = list(set(channel_ids))
            
            # 获取频道详情
            response = self.api_manager.get_channels_details(unique_ids)
            self.stats['api_calls'] += 1
            
            session = self.db.get_session()
            
            for item in response.get('items', []):
                try:
                    # 提取频道信息
                    channel_data = self._extract_channel_data(item)
                    
                    # 保存到数据库
                    existing = session.query(Channel).filter_by(channel_id=channel_data['channel_id']).first()
                    
                    if existing:
                        # 更新现有记录
                        for key, value in channel_data.items():
                            setattr(existing, key, value)
                    else:
                        # 创建新记录
                        channel = Channel(**channel_data)
                        session.add(channel)
                        self.stats['channels_inserted'] += 1
                    
                    self.stats['channels_fetched'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error saving channel {item.get('id')}: {e}")
                    self.stats['errors'] += 1
            
            session.commit()
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error fetching channel details: {e}")
    
    def _extract_channel_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取频道数据（包含主页链接）"""
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        branding = item.get('brandingSettings', {})
        
        # 提取国家信息
        country = snippet.get('country', '')
        if not country:
            # 尝试从描述中推断
            description = snippet.get('description', '')
            country = extract_country_from_text(description)
        
        # 检测语言
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        detected_lang = self.language_detector.detect_language(f"{title} {description}")
        
        # 提取自定义URL
        custom_url = snippet.get('customUrl', '')
        if not custom_url and branding.get('channel'):
            custom_url = branding['channel'].get('unsubscribedTrailer', '')
        
        # 生成主页URL和YouTube handle
        channel_id = item['id']
        homepage_url = ''
        youtube_handle = ''
        
        if custom_url:
            # 处理不同格式的custom_url
            if custom_url.startswith('@'):
                # @handle格式 (YouTube的新格式)
                homepage_url = f"https://youtube.com/{custom_url}"
                youtube_handle = custom_url
            elif custom_url.startswith('/'):
                # 移除开头的斜杠
                custom_url = custom_url[1:]
                if custom_url.startswith('@'):
                    homepage_url = f"https://youtube.com/{custom_url}"
                    youtube_handle = custom_url
                elif custom_url.startswith('c/'):
                    homepage_url = f"https://youtube.com/{custom_url}"
                elif custom_url.startswith('user/'):
                    homepage_url = f"https://youtube.com/{custom_url}"
                else:
                    homepage_url = f"https://youtube.com/c/{custom_url}"
            elif custom_url.startswith('UC'):  # Channel ID格式
                homepage_url = f"https://youtube.com/channel/{custom_url}"
            else:
                # 普通自定义URL
                homepage_url = f"https://youtube.com/c/{custom_url}"
        else:
            # 使用channel_id生成标准URL
            homepage_url = f"https://youtube.com/channel/{channel_id}"
        
        return {
            'channel_id': item['id'],
            'title': title,
            'description': description[:5000],
            'custom_url': custom_url,
            'homepage_url': homepage_url,  # 新增：主页链接
            'youtube_handle': youtube_handle,  # 新增：@handle
            'country': country,
            'detected_country': country,  # TODO: 实现更复杂的国家检测
            'detected_language': detected_lang,
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'view_count': int(statistics.get('viewCount', 0)),
            'branding_json': branding,
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            'banner_url': branding.get('image', {}).get('bannerExternalUrl', ''),
            'created_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')) if snippet.get('publishedAt') else None,
            'etag': item.get('etag'),
            'captured_at': datetime.utcnow()
        }
    
    def _aggregate_channels(self, keyword: str):
        """汇总频道信息"""
        session = self.db.get_session()
        
        try:
            # 统计每个频道在该关键词下的视频数
            from sqlalchemy import func
            query = session.query(
                Video.channel_id,
                Video.channel_title,
                func.count(Video.video_id).label('video_count')
            ).filter(
                Video.keyword == keyword
            ).group_by(
                Video.channel_id,
                Video.channel_title
            )
            
            results = query.all()
            
            self.logger.info(f"Found {len(results)} unique channels for keyword: {keyword}")
            
        except Exception as e:
            self.logger.error(f"Error in channel aggregation: {e}")
        finally:
            session.close()
    
    def _add_to_fail_queue(self, task_type: str, keyword: str, time_window: str, page_token: str, error: str):
        """添加到错误队列"""
        session = self.db.get_session()
        
        fail_task = FailQueue(
            task_type=task_type,
            keyword=keyword,
            time_window=time_window,
            page_token=page_token,
            error_reason=error,
            status='pending',
            next_retry_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        session.add(fail_task)
        session.commit()
        session.close()
    
    def process_fail_queue(self):
        """处理错误队列"""
        session = self.db.get_session()
        
        # 获取待处理的任务
        pending_tasks = session.query(FailQueue).filter(
            FailQueue.status == 'pending',
            FailQueue.retry_count < FailQueue.max_retries,
            FailQueue.next_retry_at <= datetime.utcnow()
        ).all()
        
        self.logger.info(f"Processing {len(pending_tasks)} failed tasks")
        
        for task in pending_tasks:
            try:
                task.status = 'retrying'
                task.retry_count += 1
                session.commit()
                
                # 根据任务类型重试
                if task.task_type == 'search' and task.time_window:
                    start_str, end_str = task.time_window.split('|')
                    start_date = datetime.fromisoformat(start_str)
                    end_date = datetime.fromisoformat(end_str)
                    
                    self._crawl_single_window(task.keyword, start_date, end_date)
                    
                    task.status = 'done'
                else:
                    task.status = 'dead'
                
            except Exception as e:
                self.logger.error(f"Failed to process task {task.id}: {e}")
                task.error_reason = str(e)
                task.next_retry_at = datetime.utcnow() + timedelta(hours=task.retry_count * 2)
                
                if task.retry_count >= task.max_retries:
                    task.status = 'dead'
                else:
                    task.status = 'pending'
            
            session.commit()
        
        session.close()
    
    def _output_progress(self):
        """输出进度信息（供PowerShell解析）"""
        progress_str = (
            f"[stats] "
            f"fetched={self.stats['videos_fetched']} "
            f"inserted={self.stats['videos_inserted']} "
            f"channels={self.stats['channels_fetched']} "
            f"errors={self.stats['errors']} "
            f"api_calls={self.stats['api_calls']} "
            f"api_cost={self.stats['api_cost']}"
        )
        print(progress_str, flush=True)
