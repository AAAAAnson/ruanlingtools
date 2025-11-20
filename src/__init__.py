"""
YouTube KOL Crawler Source Module
"""

from .crawler import YouTubeKOLCrawler
from .api_manager import YouTubeAPIManager
from .database import get_db, Database, Video, Channel, FailQueue, ApiUsage
from .language_detector import LanguageDetector, detect_language, extract_country_from_text
from .utils import *

__version__ = '1.0.0'
__author__ = 'YouTube KOL Crawler'

__all__ = [
    'YouTubeKOLCrawler',
    'YouTubeAPIManager',
    'Database',
    'get_db',
    'Video',
    'Channel',
    'FailQueue',
    'ApiUsage',
    'LanguageDetector',
    'detect_language',
    'extract_country_from_text'
]
