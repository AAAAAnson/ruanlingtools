#!/usr/bin/env python
"""
测试YouTube Shorts检测功能
"""
import os
import sys
from datetime import datetime
import pytz

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db, Video
from src.utils import parse_iso8601_duration
from sqlalchemy import func

def test_duration_parsing():
    """测试时长解析"""
    test_cases = [
        ('PT15S', 15, True),    # 15秒，是Short
        ('PT45S', 45, True),    # 45秒，是Short
        ('PT1M', 60, True),     # 60秒，是Short
        ('PT1M1S', 61, False),  # 61秒，不是Short
        ('PT2M30S', 150, False), # 2分30秒，不是Short
        ('PT10M', 600, False),  # 10分钟，不是Short
    ]
    
    print("测试时长解析和Shorts判断：")
    print("-" * 50)
    for duration_str, expected_seconds, expected_is_short in test_cases:
        seconds = parse_iso8601_duration(duration_str)
        is_short = seconds > 0 and seconds <= 60
        status = "✅" if (seconds == expected_seconds and is_short == expected_is_short) else "❌"
        print(f"{status} {duration_str:10} -> {seconds:4}秒 -> {'Short' if is_short else 'Normal'}")
    print()

def check_database_shorts():
    """检查数据库中的Shorts统计"""
    db = get_db()
    session = db.get_session()
    
    try:
        # 统计总数
        total_videos = session.query(func.count(Video.video_id)).scalar()
        total_shorts = session.query(func.count(Video.video_id)).filter(Video.is_short == 1).scalar()
        
        if total_videos > 0:
            percentage = (total_shorts / total_videos) * 100
            print(f"数据库统计：")
            print("-" * 50)
            print(f"总视频数：{total_videos}")
            print(f"Shorts数量：{total_shorts}")
            print(f"Shorts占比：{percentage:.2f}%")
            print()
            
            # 查看一些Shorts样例
            shorts_samples = session.query(Video).filter(Video.is_short == 1).limit(5).all()
            if shorts_samples:
                print("Shorts样例：")
                print("-" * 50)
                for video in shorts_samples:
                    print(f"标题：{video.title[:50]}...")
                    print(f"时长：{video.duration} ({video.duration_seconds}秒)")
                    print(f"URL：https://youtube.com/watch?v={video.video_id}")
                    print()
            
            # 按关键词统计
            keyword_stats = session.query(
                Video.keyword,
                func.count(Video.video_id).label('total'),
                func.sum(Video.is_short).label('shorts_count')
            ).group_by(Video.keyword).all()
            
            if keyword_stats:
                print("按关键词统计Shorts：")
                print("-" * 50)
                for keyword, total, shorts_count in keyword_stats:
                    shorts_percentage = (shorts_count / total * 100) if total > 0 else 0
                    print(f"{keyword:30} - 总数：{total:5} Shorts：{shorts_count:5} ({shorts_percentage:.1f}%)")
        else:
            print("数据库中还没有视频数据")
            
    except Exception as e:
        print(f"查询错误：{e}")
    finally:
        session.close()

def test_single_video_detection():
    """测试单个视频的Shorts检测"""
    print("\n测试视频Shorts检测逻辑：")
    print("-" * 50)
    
    test_videos = [
        {
            'title': 'Amazing trick in 30 seconds',
            'description': 'Quick tutorial',
            'duration': 'PT30S',
            'expected': True
        },
        {
            'title': 'Full tutorial - 10 minutes',
            'description': 'Complete guide',
            'duration': 'PT10M',
            'expected': False
        },
        {
            'title': 'Check this out #shorts',
            'description': 'Cool video',
            'duration': 'PT2M',
            'expected': True  # 虽然超过60秒，但有#shorts标签
        },
        {
            'title': 'Regular video',
            'description': 'This is a #Shorts video',
            'duration': 'PT5M',
            'expected': True  # 虽然超过60秒，但描述有#Shorts
        }
    ]
    
    for video in test_videos:
        duration_seconds = parse_iso8601_duration(video['duration'])
        
        # 判断是否为Shorts
        is_short = False
        if duration_seconds > 0 and duration_seconds <= 60:
            is_short = True
        elif '#shorts' in video['title'].lower() or '#shorts' in video['description'].lower():
            is_short = True
        
        status = "✅" if is_short == video['expected'] else "❌"
        print(f"{status} 标题：{video['title'][:30]}")
        print(f"   时长：{video['duration']} ({duration_seconds}秒)")
        print(f"   检测结果：{'Short' if is_short else 'Normal'}")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Shorts 检测功能测试")
    print("=" * 60)
    print()
    
    # 运行测试
    test_duration_parsing()
    test_single_video_detection()
    check_database_shorts()
    
    print("\n测试完成！")
