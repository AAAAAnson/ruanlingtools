"""
快速验证互动率功能是否正常
"""
import sys
import os

print("=" * 80)
print("快速验证 - 互动率功能")
print("=" * 80)
print()

# 测试 1: 模块导入
print("[1/4] 测试模块导入...")
try:
    from src.kol_analyzer import KeywordKOLAnalyzer
    from src.database import Video, Channel, get_db
    print("  ✓ 模块导入成功")
except ImportError as e:
    print(f"  ✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试 2: 创建分析器实例
print("\n[2/4] 测试创建分析器实例...")
try:
    analyzer = KeywordKOLAnalyzer()
    print("  ✓ 分析器创建成功")
except Exception as e:
    print(f"  ✗ 分析器创建失败: {e}")
    sys.exit(1)

# 测试 3: 测试互动率计算函数
print("\n[3/4] 测试互动率计算...")
test_cases = [
    (500, 100, 10000, 6.0),   # 正常情况
    (0, 0, 0, 0.0),           # 全为0
    (100, 50, 1000, 15.0),    # 高互动率
]

all_passed = True
for like, comment, view, expected in test_cases:
    result = analyzer.calculate_engagement_rate(like, comment, view)
    if abs(result - expected) < 0.01:
        print(f"  ✓ 测试通过: 点赞{like} 评论{comment} 播放{view} = {result:.2f}%")
    else:
        print(f"  ✗ 测试失败: 期望{expected}% 但得到{result:.2f}%")
        all_passed = False

if not all_passed:
    sys.exit(1)

# 测试 4: 检查数据库字段
print("\n[4/4] 检查数据库字段...")
try:
    db = get_db()
    session = db.get_session()
    
    # 检查 Video 表是否有所需字段
    video = session.query(Video).first()
    if video:
        # 尝试访问字段
        _ = video.like_count
        _ = video.comment_count
        _ = video.view_count
        print("  ✓ Video 表字段完整")
    else:
        print("  ⚠ 数据库为空，无法验证字段（这是正常的）")
    
    session.close()
except Exception as e:
    print(f"  ✗ 数据库字段检查失败: {e}")
    sys.exit(1)

# 全部测试通过
print()
print("=" * 80)
print("✅ 所有测试通过！互动率功能已就绪")
print("=" * 80)
print()
print("下一步:")
print("  1. 运行 GUI: python gui_with_kol_analysis.py")
print("  2. 或运行命令行: python analyze_keyword_kol.py \"关键词\" --get-latest-videos")
print("  3. 查看演示: python demo_engagement_rate.bat")
print()
print("详细文档: ENGAGEMENT_RATE_GUIDE.md")
print("=" * 80)
