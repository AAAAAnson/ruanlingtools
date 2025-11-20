"""
快速测试脚本 - 验证所有修复是否正常
"""
import subprocess
import sys
import os

def test_fixes():
    """测试所有修复"""
    
    print("="*60)
    print("  YouTube KOL Crawler - Fix Verification")
    print("="*60)
    
    # 设置Python路径
    if os.path.exists("venv\\Scripts\\python.exe"):
        python_exe = "venv\\Scripts\\python.exe"
    else:
        python_exe = "python"
    
    tests_passed = 0
    tests_failed = 0
    
    # 测试1: API状态检查（不需要keywords）
    print("\n[TEST 1] API Status Check (without keywords)...")
    try:
        result = subprocess.run(
            [python_exe, "main.py", "--status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "API Status Report" in result.stdout or result.returncode == 0:
            print("[PASS] API status check works without keywords")
            tests_passed += 1
        else:
            print(f"[FAIL] API status check failed: {result.stderr}")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] API status check error: {e}")
        tests_failed += 1
    
    # 测试2: 分析功能（测试编码）
    print("\n[TEST 2] Analysis Function (encoding test)...")
    try:
        result = subprocess.run(
            [python_exe, "analyzer.py", "keyword", "movavi"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        if result.returncode == 0 and "Analysis Report" in result.stdout:
            print("[PASS] Analysis function works correctly")
            tests_passed += 1
        else:
            print(f"[FAIL] Analysis failed: {result.stderr}")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Analysis error: {e}")
        tests_failed += 1
    
    # 测试3: 导出功能（测试编码）
    print("\n[TEST 3] Export Function (encoding test)...")
    try:
        result = subprocess.run(
            [python_exe, "analyzer.py", "export", "--keyword", "movavi", "--format", "csv"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        # 检查是否成功创建文件
        import glob
        csv_files = glob.glob("data/*movavi*.csv")
        if csv_files:
            print(f"[PASS] Export function works, file created: {csv_files[0]}")
            tests_passed += 1
        else:
            print(f"[FAIL] Export failed: No CSV file created")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Export error: {e}")
        tests_failed += 1
    
    # 总结
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n[SUCCESS] All fixes are working correctly!")
    else:
        print(f"\n[WARNING] {tests_failed} test(s) failed. Please check the errors above.")
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_fixes()
    print("\nPress Enter to continue...")
    input()
    sys.exit(0 if success else 1)
