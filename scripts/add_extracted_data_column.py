#!/usr/bin/env python3
"""
Migration script to add the extracted_data column to the card_info table.

This column is required for the enhanced synergy analysis system.
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import create_app
from src.database import db

def check_column_exists(cursor, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def add_extracted_data_column():
    """Add the extracted_data column to the card_info table if it doesn't exist."""
    print("🔧 DATABASE MIGRATION: Adding extracted_data column")
    print("=" * 60)

    # Try to find the existing database
    possible_paths = [
        os.path.join(os.getcwd(), 'instance', 'mtg_collection.db'),
        os.path.join(os.getcwd(), 'mtg_collection.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("❌ No existing database found!")
        print("Please ensure you have cards in your collection first.")
        print("Run 'python main.py' and import some cards via the API.")
        return

    print(f"📂 Found database: {db_path}")

    # Connect directly to SQLite to add the column
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if extracted_data column exists
        if check_column_exists(cursor, 'card_info', 'extracted_data'):
            print("✅ extracted_data column already exists!")
            return

        print("➕ Adding extracted_data column to card_info table...")

        # Add the column (SQLite doesn't support adding columns with constraints in one statement)
        cursor.execute("ALTER TABLE card_info ADD COLUMN extracted_data TEXT")
        conn.commit()

        print("✅ Successfully added extracted_data column!")

        # Verify the column was added
        if check_column_exists(cursor, 'card_info', 'extracted_data'):
            print("✅ Column addition verified!")
        else:
            print("❌ Column addition failed!")
            return

        # Show current table schema
        cursor.execute("PRAGMA table_info(card_info)")
        columns = cursor.fetchall()
        print(f"\n📋 Current card_info table structure:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")

        # Show how many cards are in the collection
        cursor.execute("SELECT COUNT(*) FROM card_info")
        card_count = cursor.fetchone()[0]
        print(f"\n📊 Found {card_count} cards in your collection ready for synergy analysis!")

    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """Main function."""
    try:
        add_extracted_data_column()
        print("\n🎉 Migration completed successfully!")
        print("You can now run the synergy analysis on your collection.")
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
