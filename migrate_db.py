"""
数据库迁移脚本 - 添加主页链接字段
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from src.database import get_db, Channel

def add_homepage_columns():
    """为现有数据库添加主页链接相关字段"""
    db = get_db()
    
    print("🔄 Starting database migration...")
    
    try:
        with db.engine.connect() as conn:
            # 检查是否已经有这些字段
            result = conn.execute(text("PRAGMA table_info(channels)"))
            columns = [row[1] for row in result]
            
            # 添加homepage_url字段
            if 'homepage_url' not in columns:
                print("Adding homepage_url column...")
                conn.execute(text("""
                    ALTER TABLE channels 
                    ADD COLUMN homepage_url VARCHAR(255)
                """))
                conn.commit()
                print("✅ Added homepage_url column")
            else:
                print("⚠️ homepage_url column already exists")
            
            # 添加youtube_handle字段
            if 'youtube_handle' not in columns:
                print("Adding youtube_handle column...")
                conn.execute(text("""
                    ALTER TABLE channels 
                    ADD COLUMN youtube_handle VARCHAR(100)
                """))
                conn.commit()
                print("✅ Added youtube_handle column")
            else:
                print("⚠️ youtube_handle column already exists")
            
            # 为现有数据生成主页链接
            print("\n🔗 Generating homepage URLs for existing channels...")
            session = db.get_session()
            
            channels = session.query(Channel).all()
            updated_count = 0
            
            for channel in channels:
                if not channel.homepage_url:
                    # 生成主页URL
                    if channel.custom_url:
                        # 处理不同格式的custom_url
                        custom_url = channel.custom_url
                        
                        # 如果是@开头的handle
                        if custom_url.startswith('@'):
                            channel.homepage_url = f"https://youtube.com/{custom_url}"
                            channel.youtube_handle = custom_url
                        # 如果是UC开头的channel ID格式
                        elif custom_url.startswith('UC'):
                            channel.homepage_url = f"https://youtube.com/channel/{channel.channel_id}"
                        # 如果是普通的自定义URL
                        else:
                            # 清理custom_url
                            if custom_url.startswith('/'):
                                custom_url = custom_url[1:]
                            if custom_url.startswith('c/'):
                                channel.homepage_url = f"https://youtube.com/{custom_url}"
                            elif custom_url.startswith('user/'):
                                channel.homepage_url = f"https://youtube.com/{custom_url}"
                            else:
                                channel.homepage_url = f"https://youtube.com/c/{custom_url}"
                    else:
                        # 使用channel_id生成标准URL
                        channel.homepage_url = f"https://youtube.com/channel/{channel.channel_id}"
                    
                    updated_count += 1
            
            session.commit()
            session.close()
            
            print(f"✅ Updated {updated_count} channels with homepage URLs")
            
            # 显示一些示例
            session = db.get_session()
            sample_channels = session.query(Channel).limit(5).all()
            print("\n📊 Sample channels with homepage URLs:")
            for ch in sample_channels:
                print(f"  • {ch.title[:30]:30} → {ch.homepage_url}")
            session.close()
            
            print("\n✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    add_homepage_columns()
