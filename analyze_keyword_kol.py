"""
YouTube 关键词 KOL 分析工具
用法: python analyze_keyword_kol.py "关键词" [选项]
"""
import os
import sys
import argparse
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.kol_analyzer import KeywordKOLAnalyzer

load_dotenv()

def setup_logging(log_level: str = 'INFO'):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    os.makedirs('./logs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'./logs/kol_analysis_{timestamp}.log'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return log_file

def parse_date(date_str: str):
    for fmt in ['%Y-%m-%d', '%Y/%m/%d']:
        try:
            return pytz.UTC.localize(datetime.strptime(date_str, fmt))
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}")

def main():
    parser = argparse.ArgumentParser(description='YouTube 关键词 KOL 分析工具')
    parser.add_argument('keyword', help='要分析的关键词')
    parser.add_argument('--start-date', type=str, help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--start-year', type=int, help='开始年份')
    parser.add_argument('--end-date', type=str, help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--db-only', action='store_true', help='仅分析数据库数据')
    parser.add_argument('--get-latest-videos', action='store_true', help='获取最新视频')
    parser.add_argument('--no-crawl', action='store_true', help='不爬取新视频')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    log_file = setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("YouTube 关键词 KOL 分析工具".center(80))
    print("=" * 80)
    print(f"\n分析关键词: {args.keyword}")
    print(f"日志文件: {log_file}\n")
    
    try:
        analyzer = KeywordKOLAnalyzer(logger=logger)
        
        start_date = None
        if args.start_date:
            start_date = parse_date(args.start_date)
        elif args.start_year:
            start_date = datetime(args.start_year, 1, 1, tzinfo=pytz.UTC)
        
        end_date = parse_date(args.end_date) if args.end_date else None
        
        if args.db_only or args.no_crawl:
            logger.info("仅从数据库分析")
            results = analyzer._analyze_channels_from_db(args.keyword)
            if args.get_latest_videos:
                results = analyzer._fetch_latest_videos_for_channels(results)
            export_file = analyzer._export_results(args.keyword, results)
            
            print("\n" + "=" * 80)
            print("分析完成！".center(80))
            print("=" * 80)
            print(f"频道总数: {len(results)}")
            print(f"结果文件: {export_file}")
        else:
            result = analyzer.analyze_keyword(
                keyword=args.keyword,
                start_date=start_date,
                end_date=end_date,
                get_latest_videos=args.get_latest_videos
            )
            
            print("\n" + "=" * 80)
            print("分析完成！".center(80))
            print("=" * 80)
            print(f"总视频数: {result['stats']['total_videos_found']}")
            print(f"非Shorts视频数: {result['stats']['non_shorts_videos']}")
            print(f"频道总数: {result['stats']['total_channels']}")
            print(f"结果文件: {result['export_file']}")
        
        print("\n提示: 用 Excel 打开结果文件查看详细数据")
        
    except KeyboardInterrupt:
        print("\n\n分析已中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        print(f"\n\n错误: {e}")
        print(f"详细日志: {log_file}")
        sys.exit(1)

if __name__ == '__main__':
    main()
