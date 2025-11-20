#!/usr/bin/env python
"""
更新现有数据库中的is_short字段
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db, Video
from src.utils import parse_iso8601_duration
from sqlalchemy import func

def update_shorts_field():
    """更新所有视频的is_short字段"""
    db = get_db()
    session = db.get_session()
    
    try:
        # 获取所有视频
        videos = session.query(Video).all()
        total = len(videos)
        updated = 0
        
        print(f"开始更新 {total} 个视频的Shorts标识...")
        print("-" * 60)
        
        for i, video in enumerate(videos, 1):
            # 解析时长
            duration_seconds = 0
            if video.duration:
                duration_seconds = parse_iso8601_duration(video.duration)
            
            # 更新duration_seconds字段
            video.duration_seconds = duration_seconds
            
            # 判断是否为Shorts
            old_is_short = video.is_short
            new_is_short = 0
            
            # 判断标准：
            # 1. 时长 <= 60秒
            # 2. 标题或描述包含 #shorts 标签
            if duration_seconds > 0 and duration_seconds <= 60:
                new_is_short = 1
            elif video.title and '#shorts' in video.title.lower():
                new_is_short = 1
            elif video.description and '#shorts' in video.description.lower():
                new_is_short = 1
            
            # 更新字段
            video.is_short = new_is_short
            
            # 记录更新
            if old_is_short != new_is_short:
                updated += 1
                print(f"[{i}/{total}] 更新: {video.title[:50]}...")
                print(f"  时长: {video.duration} ({duration_seconds}秒)")
                print(f"  状态: {'Normal' if old_is_short == 0 else 'Short'} -> {'Normal' if new_is_short == 0 else 'Short'}")
                print()
            
            # 每处理100个提交一次
            if i % 100 == 0:
                session.commit()
                print(f"进度: {i}/{total} ({i/total*100:.1f}%)")
        
        # 最后提交
        session.commit()
        
        # 统计结果
        print("=" * 60)
        print("更新完成！")
        print("-" * 60)
        
        # 查询统计
        total_videos = session.query(func.count(Video.video_id)).scalar()
        total_shorts = session.query(func.count(Video.video_id)).filter(Video.is_short == 1).scalar()
        
        print(f"总视频数: {total_videos}")
        print(f"Shorts数量: {total_shorts}")
        print(f"Shorts占比: {total_shorts/total_videos*100:.2f}%")
        print(f"更新记录数: {updated}")
        
        # 按关键词统计
        print("\n按关键词统计:")
        print("-" * 60)
        keyword_stats = session.query(
            Video.keyword,
            func.count(Video.video_id).label('total'),
            func.sum(Video.is_short).label('shorts_count')
        ).group_by(Video.keyword).all()
        
        for keyword, total, shorts_count in keyword_stats:
            if shorts_count is None:
                shorts_count = 0
            shorts_percentage = (shorts_count / total * 100) if total > 0 else 0
            print(f"{keyword:30} - 总数: {total:5} Shorts: {shorts_count:5} ({shorts_percentage:.1f}%)")
        
    except Exception as e:
        print(f"错误: {e}")
        session.rollback()
    finally:
        session.close()

def verify_shorts_detection():
    """验证Shorts检测的准确性"""
    db = get_db()
    session = db.get_session()
    
    try:
        print("\n验证Shorts检测准确性:")
        print("=" * 60)
        
        # 查找一些边界案例
        print("1. 时长刚好60秒的视频:")
        videos_60s = session.query(Video).filter(Video.duration_seconds == 60).limit(5).all()
        for video in videos_60s:
            print(f"  - {video.title[:50]}... [{'Short' if video.is_short else 'Normal'}]")
        
        print("\n2. 时长61秒的视频:")
        videos_61s = session.query(Video).filter(Video.duration_seconds == 61).limit(5).all()
        for video in videos_61s:
            print(f"  - {video.title[:50]}... [{'Short' if video.is_short else 'Normal'}]")
        
        print("\n3. 标题包含#shorts但时长>60秒的视频:")
        long_shorts = session.query(Video).filter(
            Video.duration_seconds > 60,
            Video.is_short == 1
        ).limit(5).all()
        for video in long_shorts:
            print(f"  - {video.title[:50]}...")
            print(f"    时长: {video.duration_seconds}秒")
            if video.title and '#shorts' in video.title.lower():
                print(f"    原因: 标题包含#shorts")
            elif video.description and '#shorts' in video.description.lower():
                print(f"    原因: 描述包含#shorts")
        
    except Exception as e:
        print(f"验证错误: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("YouTube Shorts 字段更新工具")
    print("=" * 60)
    print()
    
    # 执行更新
    update_shorts_field()
    
    # 验证结果
    verify_shorts_detection()
    
    print("\n处理完成！")
