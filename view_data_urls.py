"""
快速查看数据库中的数据（包含主页链接）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db, Video, Channel
from sqlalchemy import func

def view_data():
    db = get_db()
    session = db.get_session()
    
    print("\n" + "="*80)
    print("  DATABASE CONTENT SUMMARY (with Homepage URLs)")
    print("="*80)
    
    # 统计视频
    total_videos = session.query(func.count(Video.video_id)).scalar()
    print(f"\n📹 Total Videos: {total_videos}")
    
    # 统计频道
    total_channels = session.query(func.count(Channel.channel_id)).scalar()
    print(f"📺 Total Channels: {total_channels}")
    
    # 统计有主页链接的频道
    channels_with_url = session.query(func.count(Channel.channel_id)).filter(
        Channel.homepage_url.isnot(None)
    ).scalar()
    print(f"🔗 Channels with Homepage URL: {channels_with_url}")
    
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
    
    # 显示最新的5个频道（包含主页链接）
    print("\n🏆 Latest 5 Channels with Homepage URLs:")
    latest_channels = session.query(Channel).order_by(Channel.captured_at.desc()).limit(5).all()
    
    for i, channel in enumerate(latest_channels, 1):
        print(f"  {i}. {channel.title[:30]:30}")
        print(f"     📺 Homepage: {channel.homepage_url or 'N/A'}")
        if channel.youtube_handle:
            print(f"     📝 Handle: {channel.youtube_handle}")
        print(f"     👥 Subscribers: {channel.subscriber_count:,}")
        print(f"     🌍 Country: {channel.country or 'Unknown'}")
    
    # 显示Top 5频道（按订阅者数）
    print("\n🌟 Top 5 Channels by Subscribers:")
    top_channels = session.query(Channel).filter(
        Channel.subscriber_count > 0
    ).order_by(Channel.subscriber_count.desc()).limit(5).all()
    
    for i, channel in enumerate(top_channels, 1):
        print(f"  {i}. {channel.title[:25]:25} - {channel.subscriber_count:,} subs")
        print(f"     🔗 {channel.homepage_url or 'N/A'}")
    
    # 显示样本频道链接
    print("\n📌 Sample Channel URLs:")
    sample_channels = session.query(Channel).filter(
        Channel.homepage_url.isnot(None)
    ).limit(10).all()
    
    for channel in sample_channels[:5]:
        print(f"  • {channel.title[:30]:30}")
        print(f"    → {channel.homepage_url}")
    
    session.close()
    print("\n" + "="*80)
    print("\n💡 Tip: Use 'tools.bat' → Option 2 to export all data to Excel with homepage URLs!")

if __name__ == "__main__":
    view_data()
