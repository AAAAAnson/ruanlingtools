"""
快速查看数据库中的数据
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db, Video, Channel
from sqlalchemy import func

def view_data():
    db = get_db()
    session = db.get_session()
    
    print("\n" + "="*60)
    print("  DATABASE CONTENT SUMMARY")
    print("="*60)
    
    # 统计视频
    total_videos = session.query(func.count(Video.video_id)).scalar()
    print(f"\n📹 Total Videos: {total_videos}")
    
    # 统计频道
    total_channels = session.query(func.count(Channel.channel_id)).scalar()
    print(f"📺 Total Channels: {total_channels}")
    
    # 按关键词统计
    print("\n🔍 Videos by Keyword:")
    keyword_stats = session.query(
        Video.keyword,
        func.count(Video.video_id).label('count'),
        func.min(Video.published_at).label('oldest'),
        func.max(Video.published_at).label('newest')
    ).group_by(Video.keyword).all()
    
    for stat in keyword_stats:
        print(f"  • {stat[0]}: {stat[1]} videos")
        print(f"    Date range: {stat[2].date()} to {stat[3].date()}")
    
    # 显示最新的5个视频
    print("\n📅 Latest 5 Videos:")
    latest_videos = session.query(Video).order_by(Video.captured_at.desc()).limit(5).all()
    
    for i, video in enumerate(latest_videos, 1):
        title = video.title[:60] + '...' if len(video.title) > 60 else video.title
        print(f"  {i}. {title}")
        print(f"     Channel: {video.channel_title}, Views: {video.view_count:,}")
        print(f"     Keyword: {video.keyword}, Published: {video.published_at.date()}")
    
    # 显示Top 5频道（按视频数）
    print("\n🏆 Top 5 Channels by Video Count:")
    top_channels = session.query(
        Video.channel_id,
        Video.channel_title,
        func.count(Video.video_id).label('video_count')
    ).group_by(
        Video.channel_id,
        Video.channel_title
    ).order_by(
        func.count(Video.video_id).desc()
    ).limit(5).all()
    
    for i, channel in enumerate(top_channels, 1):
        print(f"  {i}. {channel[1]}: {channel[2]} videos")
    
    session.close()
    print("\n" + "="*60)

if __name__ == "__main__":
    view_data()
