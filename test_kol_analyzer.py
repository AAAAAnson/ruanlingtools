"""
KOL分析器测试脚本
用于验证安装和配置是否正确
"""
import os
import sys

print("=" * 80)
print("YouTube KOL 分析器 - 安装测试".center(80))
print("=" * 80)
print()

# 测试1: Python版本
print("[测试1] 检查Python版本...")
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 8:
    print(f"  ✓ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"  ✗ Python版本过低: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("    需要Python 3.8或更高版本")
    sys.exit(1)

# 测试2: 必需的库
print("\n[测试2] 检查必需的Python库...")
required_packages = {
    'sqlalchemy': 'SQLAlchemy',
    'pandas': 'Pandas',
    'openpyxl': 'OpenPyXL',
    'googleapiclient': 'Google API Client',
    'dotenv': 'python-dotenv',
    'pytz': 'pytz'
}

missing_packages = []
for package, display_name in required_packages.items():
    try:
        __import__(package)
        print(f"  ✓ {display_name}")
    except ImportError:
        print(f"  ✗ {display_name} - 未安装")
        missing_packages.append(package)

if missing_packages:
    print(f"\n  请安装缺失的库:")
    print(f"  pip install {' '.join(missing_packages)}")
    sys.exit(1)

# 测试3: 目录结构
print("\n[测试3] 检查目录结构...")
required_dirs = ['src', 'data', 'logs']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"  ✓ {dir_name}/ 目录存在")
    else:
        print(f"  ! {dir_name}/ 目录不存在，正在创建...")
        os.makedirs(dir_name, exist_ok=True)

# 测试4: 核心文件
print("\n[测试4] 检查核心文件...")
required_files = {
    'analyze_keyword_kol.py': 'KOL分析主程序',
    'src/kol_analyzer.py': 'KOL分析器模块',
    'src/crawler.py': '爬虫模块',
    'src/api_manager.py': 'API管理器',
    'src/database.py': '数据库模块',
    '.env': '环境配置文件'
}

missing_critical = False
for file_path, description in required_files.items():
    if os.path.exists(file_path):
        print(f"  ✓ {description} ({file_path})")
    else:
        if file_path == '.env':
            print(f"  ! {description} ({file_path}) - 不存在")
            print(f"    请从 .env.example 复制并配置API密钥")
        else:
            print(f"  ✗ {description} ({file_path}) - 缺失")
            if file_path in ['analyze_keyword_kol.py', 'src/kol_analyzer.py']:
                missing_critical = True

if missing_critical:
    print("\n⚠️  关键文件缺失，请确保所有新文件都已创建")
    sys.exit(1)

# 测试5: 环境配置
print("\n[测试5] 检查环境配置...")
if os.path.exists('.env'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys_str = os.getenv('YOUTUBE_API_KEYS', '')
        if api_keys_str:
            api_keys = [k.strip() for k in api_keys_str.split(',') if k.strip()]
            print(f"  ✓ 找到 {len(api_keys)} 个API密钥")
            
            for i, key in enumerate(api_keys, 1):
                if len(key) == 39:
                    print(f"    密钥#{i}: ***{key[-6:]} (格式正确)")
                else:
                    print(f"    密钥#{i}: ***{key[-6:]} (长度异常: {len(key)})")
        else:
            print("  ✗ 未配置YOUTUBE_API_KEYS")
            print("    请在.env文件中添加: YOUTUBE_API_KEYS=your_key_here")
    except Exception as e:
        print(f"  ✗ 读取.env失败: {e}")
else:
    print("  ! 未找到.env文件")
    print("    请从.env.example复制并配置")

# 测试6: 数据库连接
print("\n[测试6] 检查数据库...")
try:
    sys.path.insert(0, 'src')
    from database import get_db
    
    db = get_db()
    session = db.get_session()
    session.close()
    
    print(f"  ✓ 数据库连接正常")
    
    db_type = os.getenv('DB_TYPE', 'sqlite')
    if db_type == 'sqlite':
        db_path = os.getenv('DB_PATH', './data/youtube_kol.db')
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"    数据库文件: {db_path} ({size_mb:.2f} MB)")
        else:
            print(f"    数据库文件: {db_path} (新建)")
    else:
        print(f"    数据库类型: {db_type}")
        
except Exception as e:
    print(f"  ✗ 数据库连接失败: {e}")

# 总结
print("\n" + "=" * 80)
print("测试完成！".center(80))
print("=" * 80)

if missing_packages:
    print("\n⚠️  发现缺失的库，请先安装后再使用")
elif missing_critical:
    print("\n⚠️  关键文件缺失，请检查文件是否正确创建")
elif not os.path.exists('.env') or not os.getenv('YOUTUBE_API_KEYS'):
    print("\n⚠️  请配置API密钥后再使用")
    print("\n快速配置步骤:")
    print("  1. 复制 .env.example 为 .env")
    print("  2. 在 .env 中添加你的 YouTube API 密钥")
    print("  3. 重新运行此测试脚本")
else:
    print("\n✅ 所有检查通过！可以开始使用KOL分析器")
    print("\n使用示例:")
    print("  run_kol_analyzer.bat \"AI technology\" --db-only")
    print("\n详细文档:")
    print("  KOL_ANALYZER_QUICKSTART.md")

print()
