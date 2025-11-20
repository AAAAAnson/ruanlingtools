#!/usr/bin/env python
"""
GUI分析功能修复测试
"""
import os
import sys

def test_analyzer():
    """测试分析器是否正常工作"""
    print("=" * 60)
    print("测试分析器功能")
    print("=" * 60)
    print()
    
    # 检查数据库是否存在
    db_path = "data/youtube_kol.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库不存在: {db_path}")
        print("请先运行爬虫获取数据")
        return False
    
    print(f"✅ 找到数据库: {db_path}")
    
    # 获取一个可用的关键词
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询有数据的关键词
        cursor.execute("""
            SELECT keyword, COUNT(*) as count 
            FROM videos 
            GROUP BY keyword 
            ORDER BY count DESC 
            LIMIT 5
        """)
        keywords = cursor.fetchall()
        
        if not keywords:
            print("❌ 数据库中没有数据")
            return False
        
        print("\n找到以下关键词数据：")
        for kw, count in keywords:
            print(f"  - {kw}: {count} 个视频")
        
        # 测试第一个关键词
        test_keyword = keywords[0][0]
        print(f"\n测试关键词: {test_keyword}")
        print("-" * 40)
        
        # 运行分析
        import subprocess
        result = subprocess.run(
            ["python", "analyzer.py", "keyword", test_keyword],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 分析器运行成功")
            
            # 显示部分输出
            if result.stdout:
                lines = result.stdout.split('\n')[:20]  # 显示前20行
                print("\n分析结果（前20行）：")
                print("-" * 40)
                for line in lines:
                    if line.strip():
                        print(line)
            else:
                print("⚠️ 分析器没有输出")
        else:
            print(f"❌ 分析器运行失败 (返回码: {result.returncode})")
            if result.stderr:
                print("错误信息：")
                print(result.stderr)
        
        conn.close()
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_gui_fix():
    """检查GUI是否已修复"""
    print("\n" + "=" * 60)
    print("检查GUI修复状态")
    print("=" * 60)
    
    gui_file = "gui_fixed.py"
    if not os.path.exists(gui_file):
        print(f"❌ GUI文件不存在: {gui_file}")
        return False
    
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含修复代码
    if "if result.stdout:" in content:
        print("✅ GUI已包含NoneType修复")
        return True
    else:
        print("❌ GUI未包含修复，需要应用修复")
        return False

def main():
    print("\n" + "=" * 70)
    print("YouTube KOL Crawler - GUI分析功能诊断")
    print("=" * 70)
    print()
    
    # 1. 检查GUI修复
    gui_ok = check_gui_fix()
    
    # 2. 测试分析器
    analyzer_ok = test_analyzer()
    
    # 3. 总结
    print("\n" + "=" * 60)
    print("诊断结果")
    print("=" * 60)
    
    if gui_ok and analyzer_ok:
        print("✅ 所有功能正常！")
        print("\n您可以正常使用GUI的分析功能了。")
        print("\n启动GUI:")
        print("  python gui_fixed.py")
    elif gui_ok and not analyzer_ok:
        print("⚠️ GUI已修复，但分析器有问题")
        print("\n建议：")
        print("1. 检查数据库是否有数据")
        print("2. 确保所有依赖已安装")
        print("3. 尝试手动运行: python analyzer.py keyword <关键词>")
    elif not gui_ok and analyzer_ok:
        print("⚠️ 分析器正常，但GUI需要修复")
        print("\n运行修复：")
        print("  python fix_gui_analysis.py")
    else:
        print("❌ GUI和分析器都有问题")
        print("\n建议步骤：")
        print("1. 运行: python fix_gui_analysis.py")
        print("2. 确保数据库有数据")
        print("3. 检查所有依赖是否安装")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...")
