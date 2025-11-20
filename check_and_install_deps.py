#!/usr/bin/env python
"""
自动检测并安装缺失的依赖包
"""
import subprocess
import sys
import importlib.util

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_package(package_name):
    """安装包"""
    try:
        print(f"正在安装 {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package_name} 安装失败，尝试使用国内镜像...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                package_name
            ])
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 安装失败")
            return False

def main():
    print("=" * 60)
    print("YouTube KOL Crawler - 依赖检测和安装工具")
    print("=" * 60)
    print()
    
    # 定义所有需要的包
    packages = [
        ("tenacity", "tenacity"),
        ("google-api-python-client", "googleapiclient"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("sqlalchemy", "sqlalchemy"),
        ("pymysql", "pymysql"),
        ("python-dotenv", "dotenv"),
        ("pytz", "pytz"),
        ("jump-consistent-hash", "jump"),
        ("emoji", "emoji"),
        ("langid", "langid"),
        ("langdetect", "langdetect"),
        ("colorama", "colorama"),
        ("tqdm", "tqdm"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("numpy", "numpy"),
    ]
    
    missing_packages = []
    installed_packages = []
    
    # 检查每个包
    print("检查已安装的包...")
    print("-" * 40)
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            print(f"✅ {package_name:<30} 已安装")
            installed_packages.append(package_name)
        else:
            print(f"❌ {package_name:<30} 未安装")
            missing_packages.append((package_name, import_name))
    
    print()
    print(f"已安装: {len(installed_packages)} 个包")
    print(f"缺失: {len(missing_packages)} 个包")
    
    if missing_packages:
        print()
        print("=" * 60)
        print("开始安装缺失的包...")
        print("=" * 60)
        
        failed_packages = []
        
        for package_name, import_name in missing_packages:
            if install_package(package_name):
                print(f"✅ {package_name} 安装成功")
            else:
                failed_packages.append(package_name)
        
        print()
        print("=" * 60)
        print("安装结果")
        print("=" * 60)
        
        if failed_packages:
            print(f"⚠️ 以下包安装失败：")
            for package in failed_packages:
                print(f"  - {package}")
            print()
            print("请手动安装：")
            print(f"  pip install {' '.join(failed_packages)}")
        else:
            print("✅ 所有缺失的包已成功安装！")
    else:
        print()
        print("✅ 所有必需的包都已安装！")
    
    # 测试导入
    print()
    print("=" * 60)
    print("测试核心功能...")
    print("=" * 60)
    
    try:
        from src.utils import parse_iso8601_duration
        print("✅ 工具函数模块正常")
        print(f"   测试: PT45S = {parse_iso8601_duration('PT45S')} 秒")
    except ImportError as e:
        print(f"❌ 工具函数导入失败: {e}")
    
    try:
        from src.language_detector import LanguageDetector
        print("✅ 语言检测模块正常")
    except ImportError as e:
        print(f"❌ 语言检测模块导入失败: {e}")
    
    try:
        from src.database import get_db, Video
        print("✅ 数据库模块正常")
    except ImportError as e:
        print(f"❌ 数据库模块导入失败: {e}")
    
    print()
    print("=" * 60)
    print("检测完成！")
    
    if not missing_packages and not failed_packages:
        print()
        print("现在您可以运行：")
        print("  python test_shorts_detection.py   # 测试Shorts检测")
        print("  python update_shorts_field.py      # 更新数据库")
        print("  python shorts_analyzer.py          # 分析Shorts数据")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...")
