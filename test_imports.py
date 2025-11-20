"""
测试模块导入是否正常
"""
import sys
import os

print("=" * 60)
print("测试模块导入")
print("=" * 60)

try:
    print("\n[1/3] 测试导入 src.kol_analyzer...")
    from src.kol_analyzer import KeywordKOLAnalyzer
    print("✓ src.kol_analyzer 导入成功")
    
    print("\n[2/3] 测试导入 src.crawler...")
    from src.crawler import YouTubeKOLCrawler
    print("✓ src.crawler 导入成功")
    
    print("\n[3/3] 测试导入 src.database...")
    from src.database import get_db, Video, Channel
    print("✓ src.database 导入成功")
    
    print("\n" + "=" * 60)
    print("✓ 所有模块导入测试通过!")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
