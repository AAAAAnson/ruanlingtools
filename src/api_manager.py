"""
YouTube API管理模块
实现多Key轮换、配额管理、错误处理
"""
import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# API配额成本
API_COSTS = {
    'search': 100,
    'videos': 1,
    'channels': 1,
    'commentThreads': 1,
    'comments': 1
}

class YouTubeAPIManager:
    """YouTube API管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.key_usage = {}  # 每个Key的使用量
        self.key_status = {}  # Key状态（active, cooling, dead）
        self.per_key_budget = int(os.getenv('PER_KEY_BUDGET', '9800'))
        self.youtube = None
        self._init_key_tracking()
        self._build_service()
        
    def _load_api_keys(self) -> List[str]:
        """加载API Keys"""
        keys_str = os.getenv('YOUTUBE_API_KEYS', '')
        keys = [k.strip() for k in keys_str.split(',') if k.strip()]
        if not keys:
            raise ValueError("No YouTube API keys found in .env file")
        return keys
    
    def _init_key_tracking(self):
        """初始化Key追踪"""
        for i, key in enumerate(self.api_keys):
            self.key_usage[i] = 0
            self.key_status[i] = 'active'
    
    def _build_service(self):
        """构建YouTube服务实例"""
        if not self._has_active_key():
            raise Exception("No active API keys available")
        
        current_key = self.api_keys[self.current_key_index]
        self.youtube = build('youtube', 'v3', developerKey=current_key)
        self.logger.info(f"Using API key #{self.current_key_index} (***{current_key[-6:]})")
    
    def _has_active_key(self) -> bool:
        """检查是否有可用的Key"""
        return any(status == 'active' for status in self.key_status.values())
    
    def _switch_key(self, force=False):
        """切换到下一个可用的Key"""
        if not force and self.key_status[self.current_key_index] == 'active':
            return
        
        # 找下一个可用的Key
        start_index = self.current_key_index
        attempts = 0
        
        while attempts < len(self.api_keys):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            if self.key_status[self.current_key_index] == 'active':
                if self.key_usage[self.current_key_index] < self.per_key_budget:
                    self._build_service()
                    self.logger.info(f"Switched to API key #{self.current_key_index}")
                    return
                else:
                    self.key_status[self.current_key_index] = 'exhausted'
            
            attempts += 1
        
        # 没有可用的Key了
        raise Exception("All API keys exhausted or in cooling period")
    
    def _track_usage(self, endpoint: str, units: int = 1):
        """追踪API使用量"""
        cost = API_COSTS.get(endpoint, 1) * units
        self.key_usage[self.current_key_index] += cost
        
        # 检查是否超出预算
        if self.key_usage[self.current_key_index] >= self.per_key_budget:
            self.logger.warning(f"API key #{self.current_key_index} exhausted ({self.key_usage[self.current_key_index]}/{self.per_key_budget})")
            self.key_status[self.current_key_index] = 'exhausted'
            self._switch_key(force=True)
        
        return cost
    
    def _handle_api_error(self, error: HttpError, endpoint: str) -> bool:
        """处理API错误，返回是否应该重试"""
        try:
            error_content = json.loads(error.content.decode('utf-8'))
            error_reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason', '')
            error_code = error.resp.status
            
            self.logger.error(f"API Error on {endpoint}: {error_code} - {error_reason}")
            
            if error_code == 403:
                if error_reason in ['quotaExceeded', 'rateLimitExceeded']:
                    # 配额超限，标记Key并切换
                    self.key_status[self.current_key_index] = 'exhausted'
                    self._switch_key(force=True)
                    return True
                elif error_reason in ['ipRefererBlocked', 'keyInvalid', 'forbidden']:
                    # Key无效，标记为死亡
                    self.key_status[self.current_key_index] = 'dead'
                    self.logger.error(f"API key #{self.current_key_index} marked as dead")
                    self._switch_key(force=True)
                    return True
            
            elif error_code == 429:
                # 速率限制，等待后重试
                self.logger.warning("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return True
            
            elif error_code >= 500:
                # 服务器错误，等待后重试
                self.logger.warning(f"Server error {error_code}, waiting 30 seconds...")
                time.sleep(30)
                return True
                
        except Exception as e:
            self.logger.error(f"Error parsing API error: {e}")
        
        return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def search_videos(self, 
                     q: str,
                     published_after: str = None,
                     published_before: str = None,
                     page_token: str = None,
                     max_results: int = 50,
                     order: str = 'date',
                     region_code: str = None,
                     relevance_language: str = None) -> Dict[str, Any]:
        """搜索视频"""
        try:
            # 追踪使用量
            self._track_usage('search')
            
            # 构建请求参数
            params = {
                'q': q,
                'part': 'id,snippet',
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            if published_after:
                params['publishedAfter'] = published_after
            if published_before:
                params['publishedBefore'] = published_before
            if page_token:
                params['pageToken'] = page_token
            if region_code:
                params['regionCode'] = region_code
            if relevance_language:
                params['relevanceLanguage'] = relevance_language
            
            # 执行请求
            request = self.youtube.search().list(**params)
            response = request.execute()
            
            return response
            
        except HttpError as e:
            if self._handle_api_error(e, 'search'):
                # 重试
                return self.search_videos(q, published_after, published_before, 
                                        page_token, max_results, order, 
                                        region_code, relevance_language)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def get_videos_details(self, video_ids: List[str]) -> Dict[str, Any]:
        """批量获取视频详情"""
        if not video_ids:
            return {'items': []}
        
        try:
            # 追踪使用量（按批次数计算）
            batch_count = (len(video_ids) + 49) // 50
            self._track_usage('videos', batch_count)
            
            # YouTube API允许一次最多50个ID
            all_items = []
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(batch_ids)
                )
                response = request.execute()
                all_items.extend(response.get('items', []))
            
            return {'items': all_items}
            
        except HttpError as e:
            if self._handle_api_error(e, 'videos'):
                return self.get_videos_details(video_ids)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(HttpError)
    )
    def get_channels_details(self, channel_ids: List[str]) -> Dict[str, Any]:
        """批量获取频道详情"""
        if not channel_ids:
            return {'items': []}
        
        try:
            # 去重
            unique_ids = list(set(channel_ids))
            
            # 追踪使用量
            batch_count = (len(unique_ids) + 49) // 50
            self._track_usage('channels', batch_count)
            
            # 批量获取
            all_items = []
            for i in range(0, len(unique_ids), 50):
                batch_ids = unique_ids[i:i+50]
                
                request = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings,contentDetails',
                    id=','.join(batch_ids)
                )
                response = request.execute()
                all_items.extend(response.get('items', []))
            
            return {'items': all_items}
            
        except HttpError as e:
            if self._handle_api_error(e, 'channels'):
                return self.get_channels_details(channel_ids)
            raise
    
    def estimate_cost(self, operation: str, count: int) -> int:
        """估算API成本"""
        unit_cost = API_COSTS.get(operation, 1)
        if operation in ['videos', 'channels']:
            # 批量操作，每50个一批
            batch_count = (count + 49) // 50
            return unit_cost * batch_count
        else:
            return unit_cost * count
    
    def get_remaining_quota(self) -> int:
        """获取剩余配额"""
        total_remaining = 0
        for i, status in self.key_status.items():
            if status == 'active':
                remaining = self.per_key_budget - self.key_usage[i]
                total_remaining += max(0, remaining)
        return total_remaining
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        report = {
            'total_keys': len(self.api_keys),
            'active_keys': sum(1 for s in self.key_status.values() if s == 'active'),
            'current_key': self.current_key_index,
            'total_remaining_quota': self.get_remaining_quota(),
            'keys': []
        }
        
        for i, key in enumerate(self.api_keys):
            key_info = {
                'index': i,
                'prefix': f"***{key[-6:]}",
                'status': self.key_status[i],
                'usage': self.key_usage[i],
                'remaining': max(0, self.per_key_budget - self.key_usage[i])
            }
            report['keys'].append(key_info)
        
        return report
    
    def reset_daily_quota(self):
        """重置每日配额（太平洋时间午夜）"""
        self.logger.info("Resetting daily quota for all keys")
        for i in range(len(self.api_keys)):
            self.key_usage[i] = 0
            if self.key_status[i] == 'exhausted':
                self.key_status[i] = 'active'
