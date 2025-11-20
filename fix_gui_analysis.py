#!/usr/bin/env python
"""
修复GUI分析功能的错误
"""
import os
import sys

def fix_gui_analysis():
    """修复gui_fixed.py中的分析功能"""
    
    print("=" * 60)
    print("修复GUI分析功能")
    print("=" * 60)
    print()
    
    # 读取原文件
    gui_file = "gui_fixed.py"
    if not os.path.exists(gui_file):
        print(f"❌ 文件不存在: {gui_file}")
        return False
    
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换问题代码
    old_code = """                for line in result.stdout.split('\\n'):
                    if line.strip():
                        self.output_queue.put(line)"""
    
    new_code = """                # 安全处理输出（避免NoneType错误）
                if result.stdout:
                    for line in result.stdout.split('\\n'):
                        if line.strip():
                            self.output_queue.put(line)
                else:
                    self.output_queue.put("[WARNING] No output from analyzer")
                
                # 如果有错误输出，也显示
                if result.stderr:
                    for line in result.stderr.split('\\n'):
                        if line.strip():
                            self.output_queue.put(f"[ERROR] {line}")"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # 写回文件
        with open(gui_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 修复成功！")
        print()
        print("修复内容：")
        print("1. 添加了对None的检查")
        print("2. 添加了错误输出的显示")
        print("3. 改进了错误处理")
        print()
        print("现在可以重新启动GUI了。")
        return True
    else:
        print("⚠️ 未找到需要修复的代码，可能已经修复过了。")
        
        # 检查是否已经包含修复
        if "if result.stdout:" in content:
            print("✅ 代码已经包含修复。")
            return True
        else:
            print("❌ 代码结构与预期不同，需要手动检查。")
            return False

def create_safe_analyzer():
    """创建一个更安全的分析器包装"""
    safe_analyzer_content = '''#!/usr/bin/env python
"""
安全的分析器包装 - 处理各种错误情况
"""
import os
import sys
import traceback

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def safe_analyze(keyword):
    """安全地运行分析"""
    try:
        from analyzer import analyze_keyword
        analyze_keyword(keyword)
    except Exception as e:
        print(f"[ERROR] Analysis failed: {str(e)}")
        # 打印详细错误信息（用于调试）
        print("[DEBUG] Error details:")
        traceback.print_exc()
        
        # 提供基本统计（即使分析失败）
        try:
            from src.database import get_db, Video
            from sqlalchemy import func
            
            db = get_db()
            session = db.get_session()
            
            video_count = session.query(func.count(Video.video_id)).filter(
                Video.keyword == keyword
            ).scalar()
            
            if video_count > 0:
                print(f"\\n[INFO] Found {video_count} videos for '{keyword}' in database")
                print("[INFO] Basic analysis failed, but data is available")
                print("[INFO] Try exporting data to Excel for manual analysis")
            else:
                print(f"\\n[INFO] No data found for '{keyword}'")
                print("[INFO] Please run the crawler first to collect data")
            
            session.close()
            
        except Exception as e2:
            print(f"[ERROR] Database query failed: {str(e2)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        safe_analyze(keyword)
    else:
        print("[ERROR] Please provide a keyword")
        print("Usage: python safe_analyzer.py <keyword>")
'''
    
    with open("safe_analyzer.py", "w", encoding="utf-8") as f:
        f.write(safe_analyzer_content)
    
    print("✅ 创建了安全分析器: safe_analyzer.py")

if __name__ == "__main__":
    print("开始修复GUI分析功能...\n")
    
    # 执行修复
    success = fix_gui_analysis()
    
    # 创建安全分析器
    create_safe_analyzer()
    
    print()
    print("=" * 60)
    if success:
        print("✅ 修复完成！")
        print()
        print("下一步：")
        print("1. 重新启动GUI: python gui_fixed.py")
        print("2. 如果还有问题，使用安全分析器: python safe_analyzer.py AOMEI")
    else:
        print("⚠️ 自动修复失败，请手动检查代码。")
    
    print("=" * 60)
    
    input("\n按Enter键退出...")
