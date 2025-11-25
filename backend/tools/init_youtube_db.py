#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Database Initialization Tool

Initializes the YouTube KOL crawler database schema
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def init_database(db_path: str = None):
    """
    Initialize YouTube database with schema

    Args:
        db_path: Path to SQLite database file (default: ./data/youtube_kol.db)
    """
    if db_path is None:
        # Default path
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / 'data' / 'youtube_kol.db'
    else:
        db_path = Path(db_path)

    # Create data directory if not exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📁 Database path: {db_path}")

    # Check if database exists
    db_exists = db_path.exists()
    if db_exists:
        print(f"⚠️  Database already exists at {db_path}")
        response = input("Do you want to continue? This will create tables if they don't exist (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return False

    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("📝 Loading schema...")

    # Load schema SQL
    schema_path = Path(__file__).parent.parent / 'database' / 'youtube_schema.sql'
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Execute schema
    print("🔨 Creating tables...")
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Database schema created successfully!")

        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")

        return True

    except sqlite3.Error as e:
        print(f"❌ Error creating schema: {e}")
        return False

    finally:
        conn.close()


def main():
    """Main function"""
    print("=" * 60)
    print("  YouTube KOL Database Initialization")
    print("=" * 60)
    print()

    # Check if custom path provided
    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    success = init_database(db_path)

    if success:
        print("\n✨ Database initialization complete!")
        print("\nYou can now use the YouTube KOL crawler with database persistence.")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
