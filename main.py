"""
YouTube KOL爬虫主程序
"""
import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from typing import List

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.crawler import YouTubeKOLCrawler
from src.api_manager import YouTubeAPIManager
from src.database import get_db
from src.utils import get_pacific_time_now, format_duration

# 加载环境变量
load_dotenv()

def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """设置日志"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def parse_date(date_str: str) -> datetime:
    """解析日期字符串"""
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return pytz.UTC.localize(dt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='YouTube KOL Crawler')
    
    # 基础参数
    parser.add_argument('keywords', nargs='*', help='Keywords to search (not required for --status or --reset-quota)')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--start-year', type=int, help='Start year')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-results', type=int, help='Maximum results per keyword')
    
    # 高级参数
    parser.add_argument('--process-queue', action='store_true', help='Process fail queue')
    parser.add_argument('--estimate-only', action='store_true', help='Only estimate cost')
    parser.add_argument('--status', action='store_true', help='Show API status')
    parser.add_argument('--reset-quota', action='store_true', help='Reset daily quota')
    
    # 日志参数
    parser.add_argument('--log-level', default='INFO', help='Log level')
    parser.add_argument('--log-file', help='Log file path')
    
    # 分片参数
    parser.add_argument('--shard-id', type=int, help='Shard ID for parallel processing')
    parser.add_argument('--shard-count', type=int, help='Total number of shards')
    
    args = parser.parse_args()
    
    # 设置日志
    log_file = args.log_file or os.getenv('LOG_FILE', './logs/kol_crawler.log')
    setup_logging(args.log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("YouTube KOL Crawler started")
    
    # 覆盖环境变量中的分片设置
    if args.shard_id is not None:
        os.environ['SHARD_ID'] = str(args.shard_id)
    if args.shard_count is not None:
        os.environ['SHARD_COUNT'] = str(args.shard_count)
    
    try:
        # 创建爬虫实例
        crawler = YouTubeKOLCrawler(logger=logger)
        
        # 显示状态
        if args.status:
            status = crawler.api_manager.get_status_report()
            print("\n=== API Status Report ===")
            print(f"Total Keys: {status['total_keys']}")
            print(f"Active Keys: {status['active_keys']}")
            print(f"Total Remaining Quota: {status['total_remaining_quota']}")
            print("\nKey Details:")
            for key_info in status['keys']:
                print(f"  Key #{key_info['index']} ({key_info['prefix']}): "
                      f"Status={key_info['status']}, "
                      f"Usage={key_info['usage']}, "
                      f"Remaining={key_info['remaining']}")
            return
        
        # 重置配额
        if args.reset_quota:
            crawler.api_manager.reset_daily_quota()
            print("Daily quota reset for all keys")
            return
        
        # 检查是否需要keywords参数
        if not args.keywords:
            parser.error("keywords argument is required for crawling operations")
            return
        
        # 处理错误队列
        if args.process_queue:
            logger.info("Processing fail queue...")
            crawler.process_fail_queue()
            return
        
        # 解析日期
        start_date = None
        if args.start_date:
            start_date = parse_date(args.start_date)
        elif args.start_year:
            start_date = datetime(args.start_year, 1, 1, tzinfo=pytz.UTC)
        
        end_date = None
        if args.end_date:
            end_date = parse_date(args.end_date)
        else:
            end_date = datetime.now(pytz.UTC)
        
        # 成本估算
        if args.estimate_only:
            for keyword in args.keywords:
                logger.info(f"Estimating cost for keyword: {keyword}")
                cost = crawler._estimate_cost(keyword, start_date, end_date)
                print(f"Keyword '{keyword}': Estimated cost = {cost} units")
            return
        
        # 开始爬取
        start_time = datetime.now()
        
        for keyword in args.keywords:
            logger.info(f"Processing keyword: {keyword}")
            
            try:
                stats = crawler.crawl_keyword(
                    keyword=keyword,
                    start_date=start_date,
                    end_date=end_date,
                    max_results=args.max_results
                )
                
                # 输出统计
                print(f"\n=== Results for '{keyword}' ===")
                print(f"Videos fetched: {stats['videos_fetched']}")
                print(f"Videos inserted: {stats['videos_inserted']}")
                print(f"Channels found: {stats['channels_fetched']}")
                print(f"API calls: {stats['api_calls']}")
                print(f"API cost: {stats['api_cost']} units")
                print(f"Errors: {stats['errors']}")
                
            except Exception as e:
                logger.error(f"Error processing keyword '{keyword}': {e}", exc_info=True)
        
        # 总体统计
        elapsed = datetime.now() - start_time
        print(f"\n=== Total Execution Time ===")
        print(f"Duration: {format_duration(int(elapsed.total_seconds()))}")
        
    except KeyboardInterrupt:
        logger.info("Crawler interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
