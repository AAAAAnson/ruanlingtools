"""
数据分析和报告生成脚本
"""
import os
import sys
import argparse
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# 设置UTF-8编码，处理Windows控制台编码问题
import codecs
if sys.platform == 'win32':
    # Windows平台特殊处理
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db, Video, Channel
from src.exporter import DataExporter
from src.utils import format_number, format_duration
from sqlalchemy import func
import json

load_dotenv()

def safe_print(text):
    """安全打印函数，处理各种编码问题"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # 如果出现编码问题，尝试替换或忽略问题字符
        try:
            # 替换emoji和特殊字符为ASCII等效
            replacements = {
                '📊': '[Stats]',
                '📈': '[Chart]',
                '🏆': '[Top]',
                '🎬': '[Video]',
                '🌍': '[World]',
                '📅': '[Calendar]',
                '📺': '[TV]',
                '🔍': '[Search]',
                '📋': '[Report]',
                '📤': '[Export]',
                '✅': '[OK]',
                '❌': '[ERROR]',
                '•': '-',
                '█': '#'
            }
            for emoji, replacement in replacements.items():
                text = text.replace(emoji, replacement)
            print(text)
        except:
            # 最后的手段：移除所有非ASCII字符
            text = text.encode('ascii', 'ignore').decode('ascii')
            print(text)

def analyze_keyword(keyword: str):
    """分析特定关键词的数据"""
    db = get_db()
    session = db.get_session()
    
    safe_print(f"\n{'='*60}")
    safe_print(f"  Analysis Report for Keyword: {keyword}")
    safe_print(f"{'='*60}\n")
    
    # 基础统计
    video_count = session.query(func.count(Video.video_id)).filter(
        Video.keyword == keyword
    ).scalar()
    
    if video_count == 0:
        safe_print(f"No data found for keyword: {keyword}")
        session.close()
        return
    
    channel_count = session.query(func.count(func.distinct(Video.channel_id))).filter(
        Video.keyword == keyword
    ).scalar()
    
    total_views = session.query(func.sum(Video.view_count)).filter(
        Video.keyword == keyword
    ).scalar() or 0
    
    total_likes = session.query(func.sum(Video.like_count)).filter(
        Video.keyword == keyword
    ).scalar() or 0
    
    total_comments = session.query(func.sum(Video.comment_count)).filter(
        Video.keyword == keyword
    ).scalar() or 0
    
    # 时间范围
    date_range = session.query(
        func.min(Video.published_at),
        func.max(Video.published_at)
    ).filter(Video.keyword == keyword).first()
    
    safe_print("[Stats] Basic Statistics:")
    safe_print(f"  - Total Videos: {format_number(video_count)}")
    safe_print(f"  - Unique Channels: {format_number(channel_count)}")
    safe_print(f"  - Total Views: {format_number(total_views)}")
    safe_print(f"  - Total Likes: {format_number(total_likes)}")
    safe_print(f"  - Total Comments: {format_number(total_comments)}")
    if date_range[0] and date_range[1]:
        safe_print(f"  - Date Range: {date_range[0].date()} to {date_range[1].date()}")
    
    # 平均值
    avg_views = total_views / video_count if video_count > 0 else 0
    avg_likes = total_likes / video_count if video_count > 0 else 0
    avg_comments = total_comments / video_count if video_count > 0 else 0
    
    safe_print(f"\n[Chart] Average Metrics per Video:")
    safe_print(f"  - Average Views: {format_number(int(avg_views))}")
    safe_print(f"  - Average Likes: {format_number(int(avg_likes))}")
    safe_print(f"  - Average Comments: {format_number(int(avg_comments))}")
    if avg_views > 0:
        safe_print(f"  - Average Engagement Rate: {((avg_likes + avg_comments) / avg_views * 100):.2f}%")
    
    # Top 10 频道
    safe_print(f"\n[Top] Top 10 Channels by Total Views:")
    top_channels = session.query(
        Video.channel_id,
        Video.channel_title,
        func.count(Video.video_id).label('video_count'),
        func.sum(Video.view_count).label('total_views'),
        func.avg(Video.view_count).label('avg_views')
    ).filter(
        Video.keyword == keyword
    ).group_by(
        Video.channel_id,
        Video.channel_title
    ).order_by(
        func.sum(Video.view_count).desc()
    ).limit(10).all()
    
    for i, ch in enumerate(top_channels, 1):
        # 安全处理频道名称
        if ch[1]:
            channel_name = ch[1][:40] if len(ch[1]) > 40 else ch[1]
        else:
            channel_name = "Unknown"
        safe_print(f"  {i:2}. {channel_name:40} | Videos: {ch[2]:3} | Views: {format_number(ch[3] or 0):>10} | Avg: {format_number(int(ch[4] or 0)):>10}")
    
    # Top 10 视频
    safe_print(f"\n[Video] Top 10 Videos by Views:")
    top_videos = session.query(Video).filter(
        Video.keyword == keyword
    ).order_by(Video.view_count.desc()).limit(10).all()
    
    for i, video in enumerate(top_videos, 1):
        # 安全处理可能为None的标题
        if video.title:
            title = video.title[:50] + '...' if len(video.title) > 50 else video.title
        else:
            title = "[No Title]"
        safe_print(f"  {i:2}. {title:53} | Views: {format_number(video.view_count):>10}")
        # 安全处理频道标题
        if video.channel_title:
            channel_title = video.channel_title[:40] if len(video.channel_title) > 40 else video.channel_title
        else:
            channel_title = "Unknown"
        safe_print(f"      Channel: {channel_title:40} | Published: {video.published_at.date()}")
    
    # 语言分布
    safe_print(f"\n[World] Language Distribution:")
    language_dist = session.query(
        Video.language,
        func.count(Video.video_id).label('count')
    ).filter(
        Video.keyword == keyword,
        Video.language.isnot(None)
    ).group_by(Video.language).order_by(func.count(Video.video_id).desc()).limit(10).all()
    
    for lang in language_dist:
        percentage = (lang[1] / video_count) * 100
        safe_print(f"  - {(lang[0] or 'Unknown'):10} : {lang[1]:5} videos ({percentage:5.1f}%)")
    
    # 时间分布
    safe_print(f"\n[Calendar] Publishing Trend (by Year):")
    year_dist = session.query(
        func.strftime('%Y', Video.published_at).label('year'),
        func.count(Video.video_id).label('count')
    ).filter(
        Video.keyword == keyword
    ).group_by('year').order_by('year').all()
    
    if year_dist:
        max_count = max([y[1] for y in year_dist])
        for year_data in year_dist[-10:]:  # 最近10年
            bar_length = int(year_data[1] / max_count * 30) if max_count > 0 else 0
            bar = '#' * bar_length
            safe_print(f"  {year_data[0]}: {bar} {year_data[1]}")
    
    session.close()

def analyze_channel(channel_id: str):
    """分析特定频道的数据"""
    db = get_db()
    session = db.get_session()
    
    # 获取频道信息
    channel = session.query(Channel).filter(Channel.channel_id == channel_id).first()
    
    if not channel:
        safe_print(f"Channel not found: {channel_id}")
        session.close()
        return
    
    safe_print(f"\n{'='*60}")
    safe_print(f"  Channel Analysis: {channel.title}")
    safe_print(f"{'='*60}\n")
    
    safe_print("[TV] Channel Information:")
    safe_print(f"  - Channel ID: {channel.channel_id}")
    safe_print(f"  - Custom URL: {channel.custom_url or 'N/A'}")
    safe_print(f"  - Country: {channel.country or 'Unknown'}")
    safe_print(f"  - Language: {channel.detected_language or 'Unknown'}")
    safe_print(f"  - Subscribers: {format_number(channel.subscriber_count)}")
    safe_print(f"  - Total Videos: {format_number(channel.video_count)}")
    safe_print(f"  - Total Views: {format_number(channel.view_count)}")
    
    # 获取该频道的视频
    videos = session.query(Video).filter(Video.channel_id == channel_id).all()
    
    if videos:
        safe_print(f"\n[Stats] Video Statistics in Database:")
        safe_print(f"  - Videos Crawled: {len(videos)}")
        
        total_views = sum(v.view_count or 0 for v in videos)
        total_likes = sum(v.like_count or 0 for v in videos)
        total_comments = sum(v.comment_count or 0 for v in videos)
        
        safe_print(f"  - Total Views: {format_number(total_views)}")
        safe_print(f"  - Total Likes: {format_number(total_likes)}")
        safe_print(f"  - Total Comments: {format_number(total_comments)}")
        
        # 按关键词分组
        keyword_stats = session.query(
            Video.keyword,
            func.count(Video.video_id).label('count'),
            func.sum(Video.view_count).label('views')
        ).filter(
            Video.channel_id == channel_id
        ).group_by(Video.keyword).all()
        
        if keyword_stats:
            safe_print(f"\n[Search] Keywords Coverage:")
            for kw in keyword_stats:
                safe_print(f"  - {kw[0]:20} : {kw[1]:3} videos, {format_number(kw[2] or 0)} views")
    
    session.close()

def generate_report(output_format: str = 'json'):
    """生成完整报告"""
    exporter = DataExporter()
    
    safe_print("\n[Report] Generating comprehensive report...")
    
    # 生成汇总报告
    report = exporter.generate_summary_report()
    
    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'json':
        output_file = f"./data/report_{timestamp}.json"
        os.makedirs('./data', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        safe_print(f"[OK] Report saved to: {output_file}")
    
    # 打印摘要
    safe_print("\n[Stats] Summary:")
    safe_print(f"  - Total Videos: {format_number(report['statistics']['total_videos'])}")
    safe_print(f"  - Total Channels: {format_number(report['statistics']['total_channels'])}")
    safe_print(f"  - Total Keywords: {report['statistics'].get('total_keywords', 'N/A')}")
    
    if 'keywords' in report:
        safe_print("\n[Search] Keywords:")
        for kw in report['keywords']:
            safe_print(f"  - {kw['keyword']}: {kw['video_count']} videos")

def export_data(keyword: str = None, format: str = 'excel'):
    """导出数据"""
    exporter = DataExporter()
    
    safe_print(f"\n[Export] Exporting data (format: {format})...")
    
    try:
        if keyword:
            # 导出特定关键词的数据
            channels_file = exporter.export_channels_report(keyword, format)
            videos_file = exporter.export_videos_report(keyword, output_format=format)
            
            safe_print(f"[OK] Channels exported to: {channels_file}")
            safe_print(f"[OK] Videos exported to: {videos_file}")
        else:
            # 导出所有数据
            channels_file = exporter.export_channels_report(output_format=format)
            safe_print(f"[OK] All channels exported to: {channels_file}")
    except Exception as e:
        safe_print(f"[ERROR] Export failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='YouTube KOL Data Analyzer')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # 分析关键词
    keyword_parser = subparsers.add_parser('keyword', help='Analyze keyword data')
    keyword_parser.add_argument('keyword', help='Keyword to analyze')
    
    # 分析频道
    channel_parser = subparsers.add_parser('channel', help='Analyze channel data')
    channel_parser.add_argument('channel_id', help='Channel ID to analyze')
    
    # 生成报告
    report_parser = subparsers.add_parser('report', help='Generate comprehensive report')
    report_parser.add_argument('--format', default='json', choices=['json'], help='Output format')
    
    # 导出数据
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--keyword', help='Keyword to export (optional, exports all if not specified)')
    export_parser.add_argument('--format', default='excel', choices=['excel', 'csv', 'json'], help='Output format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'keyword':
            analyze_keyword(args.keyword)
        elif args.command == 'channel':
            analyze_channel(args.channel_id)
        elif args.command == 'report':
            generate_report(args.format)
        elif args.command == 'export':
            export_data(args.keyword, args.format)
    except Exception as e:
        safe_print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
