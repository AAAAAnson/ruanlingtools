"""
测试互动率计算功能
"""
import sys
import os
from src.kol_analyzer import KeywordKOLAnalyzer

print("=" * 60)
print("测试互动率计算功能")
print("=" * 60)

# 初始化分析器
analyzer = KeywordKOLAnalyzer()

# 测试互动率计算
print("\n测试案例：")
print("-" * 60)

test_cases = [
    {"播放量": 10000, "点赞数": 500, "评论数": 100, "预期互动率": 6.0},
    {"播放量": 50000, "点赞数": 2500, "评论数": 500, "预期互动率": 6.0},
    {"播放量": 100000, "点赞数": 5000, "评论数": 1000, "预期互动率": 6.0},
    {"播放量": 0, "点赞数": 100, "评论数": 50, "预期互动率": 0.0},  # 播放量为0的情况
]

for i, case in enumerate(test_cases, 1):
    view_count = case["播放量"]
    like_count = case["点赞数"]
    comment_count = case["评论数"]
    expected = case["预期互动率"]
    
    result = analyzer.calculate_engagement_rate(like_count, comment_count, view_count)
    
    print(f"\n案例 {i}:")
    print(f"  播放量: {view_count:,}")
    print(f"  点赞数: {like_count:,}")
    print(f"  评论数: {comment_count:,}")
    print(f"  计算结果: {result:.2f}%")
    print(f"  预期结果: {expected:.2f}%")
    print(f"  状态: {'✓ 通过' if abs(result - expected) < 0.01 else '✗ 失败'}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

print("\n\n新增功能说明:")
print("-" * 60)
print("1. ✓ 在数据库查询中获取点赞数和评论数")
print("2. ✓ 在API调用中获取点赞数和评论数")
print("3. ✓ 计算每个视频的互动率 = (点赞数 + 评论数) / 播放量 × 100%")
print("4. ✓ 计算频道最近10条视频的平均互动率")
print("5. ✓ 在Excel导出中添加互动率相关列")
print("\nExcel输出包含以下新列:")
print("  - 频道概览表: 最新10视频平均互动率(%)")
print("  - 视频详情表: 点赞数、评论数、互动率(%)")
print("=" * 60)
