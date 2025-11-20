#!/usr/bin/env python
"""
YouTube Shorts 数据分析工具
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import func, and_

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db, Video, Channel
from src.utils import format_number, calculate_engagement_rate

class ShortsAnalyzer:
    """Shorts数据分析器"""
    
    def __init__(self):
        self.db = get_db()
    
    def analyze_shorts_performance(self, keyword=None):
        """分析Shorts vs 普通视频的表现"""
        session = self.db.get_session()
        
        try:
            # 基础查询
            query = session.query(Video)
            if keyword:
                query = query.filter(Video.keyword == keyword)
            
            videos = query.all()
            
            # 分离Shorts和普通视频
            shorts = [v for v in videos if v.is_short == 1]
            normal_videos = [v for v in videos if v.is_short == 0]
            
            print("\n" + "=" * 70)
            print(f"Shorts vs 普通视频性能对比 {'- ' + keyword if keyword else ''}")
            print("=" * 70)
            
            # 基础统计
            print("\n📊 基础统计:")
            print("-" * 40)
            print(f"Shorts数量: {len(shorts):,}")
            print(f"普通视频数量: {len(normal_videos):,}")
            print(f"Shorts占比: {len(shorts)/(len(videos))*100:.1f}%" if videos else "N/A")
            
            # 观看量对比
            if shorts and normal_videos:
                shorts_avg_views = sum(s.view_count for s in shorts) / len(shorts)
                normal_avg_views = sum(v.view_count for v in normal_videos) / len(normal_videos)
                
                shorts_avg_likes = sum(s.like_count for s in shorts) / len(shorts)
                normal_avg_likes = sum(v.like_count for v in normal_videos) / len(normal_videos)
                
                shorts_avg_comments = sum(s.comment_count for s in shorts) / len(shorts)
                normal_avg_comments = sum(v.comment_count for v in normal_videos) / len(normal_videos)
                
                print("\n📈 平均性能指标:")
                print("-" * 40)
                print(f"{'指标':<15} {'Shorts':>15} {'普通视频':>15} {'差异':>15}")
                print("-" * 60)
                
                # 观看量
                view_diff = ((shorts_avg_views - normal_avg_views) / normal_avg_views * 100) if normal_avg_views > 0 else 0
                print(f"{'平均观看量':<15} {format_number(int(shorts_avg_views)):>15} {format_number(int(normal_avg_views)):>15} {view_diff:>14.1f}%")
                
                # 点赞数
                like_diff = ((shorts_avg_likes - normal_avg_likes) / normal_avg_likes * 100) if normal_avg_likes > 0 else 0
                print(f"{'平均点赞数':<15} {format_number(int(shorts_avg_likes)):>15} {format_number(int(normal_avg_likes)):>15} {like_diff:>14.1f}%")
                
                # 评论数
                comment_diff = ((shorts_avg_comments - normal_avg_comments) / normal_avg_comments * 100) if normal_avg_comments > 0 else 0
                print(f"{'平均评论数':<15} {format_number(int(shorts_avg_comments)):>15} {format_number(int(normal_avg_comments)):>15} {comment_diff:>14.1f}%")
                
                # 参与率
                shorts_engagement = sum(calculate_engagement_rate(s.view_count, s.like_count, s.comment_count) for s in shorts) / len(shorts)
                normal_engagement = sum(calculate_engagement_rate(v.view_count, v.like_count, v.comment_count) for v in normal_videos) / len(normal_videos)
                engagement_diff = ((shorts_engagement - normal_engagement) / normal_engagement * 100) if normal_engagement > 0 else 0
                
                print(f"{'平均参与率':<15} {shorts_engagement:>14.2f}% {normal_engagement:>14.2f}% {engagement_diff:>14.1f}%")
            
        except Exception as e:
            print(f"分析错误: {e}")
        finally:
            session.close()
    
    def top_shorts_channels(self, keyword=None, limit=10):
        """找出Shorts表现最好的频道"""
        session = self.db.get_session()
        
        try:
            # 构建查询
            query = session.query(
                Video.channel_id,
                Video.channel_title,
                func.count(Video.video_id).label('shorts_count'),
                func.sum(Video.view_count).label('total_views'),
                func.avg(Video.view_count).label('avg_views'),
                func.sum(Video.like_count).label('total_likes'),
                func.sum(Video.comment_count).label('total_comments')
            ).filter(Video.is_short == 1)
            
            if keyword:
                query = query.filter(Video.keyword == keyword)
            
            results = query.group_by(
                Video.channel_id,
                Video.channel_title
            ).order_by(
                func.sum(Video.view_count).desc()
            ).limit(limit).all()
            
            print("\n" + "=" * 70)
            print(f"Top {limit} Shorts创作者 {'- ' + keyword if keyword else ''}")
            print("=" * 70)
            
            for i, (channel_id, channel_title, shorts_count, total_views, avg_views, total_likes, total_comments) in enumerate(results, 1):
                engagement_rate = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0
                
                print(f"\n{i}. {channel_title}")
                print(f"   频道ID: {channel_id}")
                print(f"   Shorts数量: {shorts_count}")
                print(f"   总观看量: {format_number(total_views)}")
                print(f"   平均观看量: {format_number(int(avg_views))}")
                print(f"   总点赞数: {format_number(total_likes)}")
                print(f"   参与率: {engagement_rate:.2f}%")
                print(f"   频道链接: https://youtube.com/channel/{channel_id}")
            
        except Exception as e:
            print(f"查询错误: {e}")
        finally:
            session.close()
    
    def shorts_trend_analysis(self, keyword=None, days=30):
        """分析Shorts的时间趋势"""
        session = self.db.get_session()
        
        try:
            # 计算时间范围
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 查询数据
            query = session.query(
                func.date(Video.published_at).label('date'),
                func.count(Video.video_id).label('count'),
                func.sum(Video.is_short).label('shorts_count')
            ).filter(
                Video.published_at >= start_date
            )
            
            if keyword:
                query = query.filter(Video.keyword == keyword)
            
            results = query.group_by(
                func.date(Video.published_at)
            ).order_by(
                func.date(Video.published_at)
            ).all()
            
            print("\n" + "=" * 70)
            print(f"Shorts发布趋势（最近{days}天）{'- ' + keyword if keyword else ''}")
            print("=" * 70)
            
            if results:
                # 转换为DataFrame便于分析
                df = pd.DataFrame(results, columns=['date', 'total', 'shorts'])
                df['normal'] = df['total'] - df['shorts']
                df['shorts_ratio'] = (df['shorts'] / df['total'] * 100).round(1)
                
                # 打印统计
                print("\n📅 每日统计:")
                print("-" * 60)
                print(f"{'日期':<12} {'总视频':>8} {'Shorts':>8} {'普通视频':>8} {'Shorts占比':>12}")
                print("-" * 60)
                
                for _, row in df.tail(10).iterrows():  # 显示最近10天
                    print(f"{str(row['date']):<12} {row['total']:>8} {row['shorts']:>8} {row['normal']:>8} {row['shorts_ratio']:>11.1f}%")
                
                # 趋势分析
                print("\n📊 趋势分析:")
                print("-" * 40)
                print(f"期间总视频数: {df['total'].sum():,}")
                print(f"期间Shorts数: {df['shorts'].sum():,}")
                print(f"平均每日Shorts: {df['shorts'].mean():.1f}")
                print(f"Shorts占比趋势: {'上升' if df.head(7)['shorts_ratio'].mean() < df.tail(7)['shorts_ratio'].mean() else '下降'}")
            else:
                print("该时间段内没有数据")
            
        except Exception as e:
            print(f"趋势分析错误: {e}")
        finally:
            session.close()
    
    def export_shorts_report(self, keyword=None, output_file=None):
        """导出Shorts分析报告到Excel"""
        session = self.db.get_session()
        
        try:
            # 准备数据
            query = session.query(Video).filter(Video.is_short == 1)
            if keyword:
                query = query.filter(Video.keyword == keyword)
            
            shorts = query.order_by(Video.view_count.desc()).all()
            
            # 创建DataFrame
            data = []
            for video in shorts:
                engagement_rate = calculate_engagement_rate(
                    video.view_count,
                    video.like_count,
                    video.comment_count
                )
                
                data.append({
                    'Video ID': video.video_id,
                    'Title': video.title,
                    'Channel': video.channel_title,
                    'Published': video.published_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Views': video.view_count,
                    'Likes': video.like_count,
                    'Comments': video.comment_count,
                    'Engagement Rate': f"{engagement_rate:.2f}%",
                    'Duration (seconds)': video.duration_seconds,
                    'Language': video.language,
                    'Keyword': video.keyword,
                    'URL': f"https://youtube.com/watch?v={video.video_id}"
                })
            
            df = pd.DataFrame(data)
            
            # 生成文件名
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                keyword_str = keyword.replace(' ', '_') if keyword else 'all'
                output_file = f"./data/shorts_report_{keyword_str}_{timestamp}.xlsx"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 导出到Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Shorts Videos', index=False)
                
                # 添加统计表
                stats_data = {
                    '指标': ['总Shorts数', '总观看量', '平均观看量', '总点赞数', '平均点赞数', '平均参与率'],
                    '值': [
                        len(shorts),
                        df['Views'].sum(),
                        df['Views'].mean(),
                        df['Likes'].sum(),
                        df['Likes'].mean(),
                        df['Engagement Rate'].apply(lambda x: float(x.replace('%', ''))).mean()
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            print(f"\n✅ 报告已导出到: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"导出错误: {e}")
            return None
        finally:
            session.close()

def main():
    """主函数"""
    analyzer = ShortsAnalyzer()
    
    print("=" * 70)
    print("YouTube Shorts 数据分析工具")
    print("=" * 70)
    
    # 获取用户输入
    keyword = input("\n请输入要分析的关键词（留空分析所有）: ").strip() or None
    
    print("\n开始分析...\n")
    
    # 执行分析
    analyzer.analyze_shorts_performance(keyword)
    analyzer.top_shorts_channels(keyword, limit=10)
    analyzer.shorts_trend_analysis(keyword, days=30)
    
    # 询问是否导出
    export = input("\n是否导出Shorts报告到Excel? (y/n): ").strip().lower()
    if export == 'y':
        analyzer.export_shorts_report(keyword)
    
    print("\n分析完成！")

if __name__ == "__main__":
    main()
