#!/usr/bin/env python
"""
数据库迁移脚本 - 添加Shorts相关字段
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db, Base
from sqlalchemy import text, inspect
import sqlite3

def add_shorts_fields():
    """为videos表添加Shorts相关字段"""
    db = get_db()
    
    # 获取数据库路径
    db_path = os.getenv('DB_PATH', './data/youtube_kol.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行爬虫创建数据库，或者创建一个新的数据库。")
        return False
    
    print(f"数据库路径: {db_path}")
    
    try:
        # 使用sqlite3直接操作（更可靠）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='videos'")
        if not cursor.fetchone():
            print("❌ videos表不存在，需要先运行爬虫创建数据库结构")
            
            # 创建数据库表
            print("正在创建数据库表...")
            from src.database import Base
            Base.metadata.create_all(db.engine)
            print("✅ 数据库表创建成功")
            conn.close()
            return True
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(videos)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("\n当前videos表的字段:")
        print("-" * 50)
        for col in column_names:
            print(f"  - {col}")
        
        # 添加缺失的字段
        fields_to_add = []
        
        if 'duration_seconds' not in column_names:
            fields_to_add.append(('duration_seconds', 'INTEGER DEFAULT 0'))
            
        if 'is_short' not in column_names:
            fields_to_add.append(('is_short', 'INTEGER DEFAULT 0'))
        
        if fields_to_add:
            print("\n添加缺失的字段:")
            print("-" * 50)
            
            for field_name, field_type in fields_to_add:
                try:
                    sql = f"ALTER TABLE videos ADD COLUMN {field_name} {field_type}"
                    cursor.execute(sql)
                    print(f"✅ 添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️ 字段 {field_name} 已存在")
                    else:
                        print(f"❌ 添加字段 {field_name} 失败: {e}")
            
            conn.commit()
            print("\n✅ 数据库字段添加完成")
        else:
            print("\n✅ 所有必需的字段都已存在")
        
        # 验证字段
        cursor.execute("PRAGMA table_info(videos)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("\n更新后的字段列表:")
        print("-" * 50)
        shorts_fields = ['duration', 'duration_seconds', 'is_short']
        for col in column_names:
            if col in shorts_fields:
                print(f"  - {col} ✅")
            else:
                print(f"  - {col}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def create_empty_database():
    """创建空的数据库和表结构"""
    print("\n创建新的数据库...")
    
    # 确保data目录存在
    os.makedirs('./data', exist_ok=True)
    
    # 创建数据库表
    db = get_db()
    from src.database import Base
    
    try:
        Base.metadata.create_all(db.engine)
        print("✅ 数据库和表结构创建成功")
        
        # 添加Shorts字段（如果需要）
        add_shorts_fields()
        
        return True
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def main():
    print("=" * 60)
    print("YouTube Shorts 数据库迁移工具")
    print("=" * 60)
    print()
    
    # 检查数据库是否存在
    db_path = os.getenv('DB_PATH', './data/youtube_kol.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        
        choice = input("\n是否创建新的数据库? (y/n): ").strip().lower()
        if choice == 'y':
            if create_empty_database():
                print("\n✅ 数据库创建成功！现在可以运行Shorts功能了。")
            else:
                print("\n❌ 数据库创建失败")
        else:
            print("\n请先运行爬虫创建数据库：")
            print("  python main.py \"your keyword\"")
    else:
        print(f"找到数据库: {db_path}")
        
        # 执行迁移
        if add_shorts_fields():
            print("\n✅ 迁移成功！")
            print("\n现在您可以运行：")
            print("  python test_shorts_detection.py   # 测试Shorts检测")
            print("  python update_shorts_field.py      # 更新现有数据的Shorts标识")
            print("  python shorts_analyzer.py          # 分析Shorts数据")
        else:
            print("\n❌ 迁移失败")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...")
