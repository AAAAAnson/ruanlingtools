"""
清理项目中的临时文件
"""
import os

def cleanup_project():
    """删除不需要的临时文件"""
    
    # 要删除的文件列表
    files_to_delete = [
        'check_data.py',
        'fix_aggregation.py',
        'fix_and_check.bat',
        'quickfix.py',
        'view_imyfone_data.bat',
        'view_data_safe.bat',
        'solution.bat',
        'view_simple.py',
        'update_homepage_feature.py',
        'clean_project.py',
        'temp_clean.py.bak',
        'run_crawler copy.ps1',
        'CRAWL_SUCCESS_NOTE.md',
        'README_FIX.md',
        'SOLUTION_COMPLETE.md',
        'HOMEPAGE_UPDATE_SUCCESS.md'
    ]
    
    print("="*60)
    print("   YouTube KOL Crawler - Project Cleanup")
    print("="*60)
    print("\nCleaning temporary files...\n")
    
    deleted_count = 0
    
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  ✓ Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {file}: {e}")
    
    print(f"\n✅ Cleanup complete! Deleted {deleted_count} files.")
    print("\nProject is now clean and organized.")
    
    return deleted_count

if __name__ == "__main__":
    cleanup_project()
    print("\nPress Enter to continue...")
    input()
