"""
工具函数模块
"""
import os
import re
import hashlib
from datetime import datetime, timedelta
import pytz
from typing import Optional, List, Tuple
import jump

# --- fallback for jump consistent hash (if package missing) ---
try:
    import jump  # pip install jump-consistent-hash
except Exception:
    # Pure-Python Jump Consistent Hash (Lamping & Veach, 2014)
    def _jump_hash(key: int, buckets: int) -> int:
        if buckets <= 0:
            raise ValueError("buckets must be > 0")
        b, j = -1, 0
        import math
        while j < buckets:
            b = j
            key = (key * 2862933555777941757 + 1) & ((1 << 64) - 1)
            j = int((b + 1) * (1 << 31) / ((key >> 33) + 1))
        return b

    class _JumpModule:
        @staticmethod
        def hash(key: int, buckets: int) -> int:
            return _jump_hash(key, buckets)

    jump = _JumpModule()

# --- weak country inference from free text / URLs / TLDs ---
from typing import Optional

_COUNTRY_KV = {
    "united states": "US", "usa": "US", "u.s.": "US", "america": "US",
    "united kingdom": "GB", "uk": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
    "canada": "CA", "australia": "AU", "new zealand": "NZ", "ireland": "IE",
    "china": "CN", "mainland china": "CN", "prc": "CN",
    "hong kong": "HK", "macau": "MO", "taiwan": "TW",
    "singapore": "SG", "malaysia": "MY", "philippines": "PH", "indonesia": "ID", "thailand": "TH",
    "vietnam": "VN", "india": "IN", "japan": "JP", "korea": "KR", "south korea": "KR",
    "germany": "DE", "france": "FR", "spain": "ES", "italy": "IT", "netherlands": "NL",
    "belgium": "BE", "sweden": "SE", "norway": "NO", "denmark": "DK", "finland": "FI",
    "poland": "PL", "austria": "AT", "switzerland": "CH", "portugal": "PT", "greece": "GR",
    "mexico": "MX", "brazil": "BR", "argentina": "AR", "chile": "CL", "colombia": "CO",
    "turkey": "TR", "uae": "AE", "saudi arabia": "SA", "south africa": "ZA",
}
_CITY_HINTS = {
    "nyc": "US", "los angeles": "US", "seattle": "US", "silicon valley": "US",
    "london": "GB", "manchester": "GB",
    "toronto": "CA", "vancouver": "CA",
    "sydney": "AU", "melbourne": "AU",
    "singapore": "SG", "hong kong": "HK",
    "tokyo": "JP", "osaka": "JP",
    "seoul": "KR",
    "mumbai": "IN", "delhi": "IN", "bangalore": "IN",
    "berlin": "DE", "munich": "DE",
    "paris": "FR",
    "madrid": "ES", "barcelona": "ES",
    "rome": "IT", "milan": "IT",
}
_TLD_TO_CC = {
    ".uk": "GB", ".de": "DE", ".fr": "FR", ".es": "ES", ".it": "IT", ".nl": "NL", ".be": "BE",
    ".se": "SE", ".no": "NO", ".dk": "DK", ".fi": "FI", ".pl": "PL", ".at": "AT", ".ch": "CH",
    ".pt": "PT", ".gr": "GR", ".ie": "IE",
    ".cn": "CN", ".hk": "HK", ".mo": "MO", ".tw": "TW", ".jp": "JP", ".kr": "KR", ".sg": "SG",
    ".my": "MY", ".id": "ID", ".th": "TH", ".vn": "VN", ".ph": "PH",
    ".in": "IN",
    ".ca": "CA", ".au": "AU", ".nz": "NZ",
    ".mx": "MX", ".br": "BR", ".ar": "AR", ".cl": "CL", ".co": "CO",
    ".tr": "TR", ".ae": "AE", ".sa": "SA", ".za": "ZA",
}

def extract_country_from_text(text: Optional[str]) -> Optional[str]:
    """从自由文本里做“弱推断”国家（ISO2），不确定返回 None。"""
    if not text:
        return None
    s = text.lower()

    # 1) 直接国家/别称
    for key, cc in _COUNTRY_KV.items():
        if f" {key} " in f" {s} ":
            return cc

    # 2) 城市提示
    for key, cc in _CITY_HINTS.items():
        if f" {key} " in f" {s} ":
            return cc

    # 3) 域名 TLD（邮箱/链接中）
    import re
    for m in re.finditer(r"([a-z0-9\-]+\.)+([a-z]{2,3})(?:\b|/)", s):
        tld = "." + m.group(2)
        if tld in _TLD_TO_CC:
            return _TLD_TO_CC[tld]

    return None

def format_iso8601_time(dt: datetime) -> str:
    """格式化时间为ISO 8601格式（YouTube API要求）"""
    if not dt.tzinfo:
        dt = pytz.UTC.localize(dt)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_iso8601_duration(duration_str: str) -> int:
    """解析ISO 8601持续时间格式（如PT4M13S）为秒数"""
    if not duration_str:
        return 0
    
    # 正则匹配ISO 8601持续时间
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds


def get_pacific_time_now() -> datetime:
    """获取当前太平洋时间"""
    pacific = pytz.timezone('America/Los_Angeles')
    return datetime.now(pacific)


def get_utc_midnight_pacific() -> datetime:
    """获取太平洋时间午夜对应的UTC时间（用于配额重置）"""
    pacific = pytz.timezone('America/Los_Angeles')
    now_pacific = datetime.now(pacific)
    midnight_pacific = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight_pacific.astimezone(pytz.UTC)


def extract_video_id_from_url(url: str) -> Optional[str]:
    """从YouTube URL中提取视频ID"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_channel_id_from_url(url: str) -> Optional[str]:
    """从YouTube URL中提取频道ID"""
    patterns = [
        r'youtube\.com\/channel\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/c\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/user\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/@([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def format_number(num: int) -> str:
    """格式化数字显示（如1.2K, 3.4M）"""
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    elif num < 1000000000:
        return f"{num/1000000:.1f}M"
    else:
        return f"{num/1000000000:.1f}B"


def calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
    """计算参与率"""
    if views == 0:
        return 0.0
    
    engagement = likes + comments
    return (engagement / views) * 100


def estimate_video_value(views: int, likes: int, comments: int, subscriber_count: int) -> float:
    """估算视频价值分数"""
    # 简单的价值评分算法
    engagement_rate = calculate_engagement_rate(views, likes, comments)
    
    # 基础分数
    score = views * 0.001  # 每1000次观看1分
    
    # 参与率加成
    if engagement_rate > 10:
        score *= 2
    elif engagement_rate > 5:
        score *= 1.5
    elif engagement_rate > 2:
        score *= 1.2
    
    # 订阅者数量加成
    if subscriber_count > 1000000:
        score *= 1.5
    elif subscriber_count > 100000:
        score *= 1.2
    
    return score


def get_shard_keywords(keywords: List[str], shard_id: int, shard_count: int) -> List[str]:
    """根据分片ID获取应处理的关键词列表"""
    if shard_count <= 1:
        return keywords
    
    sharded_keywords = []
    for keyword in keywords:
        # 使用Jump Consistent Hash
        keyword_hash = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        assigned_shard = jump.hash(keyword_hash, shard_count)
        
        if assigned_shard == shard_id:
            sharded_keywords.append(keyword)
    
    return sharded_keywords


def should_process_keyword(keyword: str, shard_id: int, shard_count: int) -> bool:
    """判断当前分片是否应该处理该关键词"""
    if shard_count <= 1:
        return True
    
    keyword_hash = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
    assigned_shard = jump.hash(keyword_hash, shard_count)
    
    return assigned_shard == shard_id


def split_time_window(start: datetime, end: datetime, max_days: int = 30) -> List[Tuple[datetime, datetime]]:
    """将时间范围切分成多个窗口"""
    windows = []
    current = start
    
    while current < end:
        window_end = min(current + timedelta(days=max_days), end)
        windows.append((current, window_end))
        current = window_end
    
    return windows


def merge_time_windows(windows: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    """合并重叠的时间窗口"""
    if not windows:
        return []
    
    # 排序
    sorted_windows = sorted(windows, key=lambda x: x[0])
    
    merged = [sorted_windows[0]]
    
    for current in sorted_windows[1:]:
        last_start, last_end = merged[-1]
        current_start, current_end = current
        
        # 如果有重叠或相邻，合并
        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append(current)
    
    return merged


def clean_text(text: str, max_length: int = None) -> str:
    """清理文本（移除特殊字符、限制长度等）"""
    if not text:
        return ''
    
    # 移除控制字符
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    # 移除多余空格
    text = ' '.join(text.split())
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + '...'
    
    return text


def extract_hashtags(text: str) -> List[str]:
    """从文本中提取hashtag"""
    if not text:
        return []
    
    hashtags = re.findall(r'#(\w+)', text)
    return list(set(hashtags))  # 去重


def extract_mentions(text: str) -> List[str]:
    """从文本中提取@提及"""
    if not text:
        return []
    
    mentions = re.findall(r'@(\w+)', text)
    return list(set(mentions))  # 去重


def extract_urls(text: str) -> List[str]:
    """从文本中提取URL"""
    if not text:
        return []
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # 去重


def is_valid_youtube_api_key(key: str) -> bool:
    """验证YouTube API Key格式"""
    if not key:
        return False
    
    # YouTube API Key通常是39个字符
    if len(key) != 39:
        return False
    
    # 只包含字母数字和连字符/下划线
    if not re.match(r'^[a-zA-Z0-9_-]+$', key):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """清理文件名（移除非法字符）"""
    # Windows文件名非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    
    # 替换非法字符为下划线
    clean_name = re.sub(illegal_chars, '_', filename)
    
    # 移除开头和结尾的空格和点
    clean_name = clean_name.strip(' .')
    
    # 限制长度（Windows路径限制）
    if len(clean_name) > 200:
        clean_name = clean_name[:200]
    
    return clean_name


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """创建ASCII进度条"""
    if total == 0:
        percent = 0
    else:
        percent = int((current / total) * 100)
    
    filled = int(width * current // total) if total > 0 else 0
    bar = '█' * filled + '░' * (width - filled)
    
    return f'[{bar}] {percent}% ({current}/{total})'


def format_duration(seconds: int) -> str:
    """格式化持续时间"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs}s"


def estimate_time_remaining(processed: int, total: int, elapsed_seconds: float) -> str:
    """估算剩余时间"""
    if processed == 0:
        return "Calculating..."
    
    rate = processed / elapsed_seconds
    remaining = total - processed
    
    if rate == 0:
        return "Unknown"
    
    eta_seconds = remaining / rate
    return format_duration(int(eta_seconds))


# 导出所有函数
__all__ = [
    'format_iso8601_time',
    'parse_iso8601_duration',
    'get_pacific_time_now',
    'get_utc_midnight_pacific',
    'extract_video_id_from_url',
    'extract_channel_id_from_url',
    'format_number',
    'calculate_engagement_rate',
    'estimate_video_value',
    'get_shard_keywords',
    'should_process_keyword',
    'split_time_window',
    'merge_time_windows',
    'clean_text',
    'extract_hashtags',
    'extract_mentions',
    'extract_urls',
    'is_valid_youtube_api_key',
    'sanitize_filename',
    'create_progress_bar',
    'format_duration',
    'estimate_time_remaining',
    'extract_country_from_text',
]

