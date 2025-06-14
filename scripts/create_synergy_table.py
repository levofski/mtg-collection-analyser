#!/usr/bin/env python3
"""
Migration script to create the card_synergy table for storing synergy scores.

This table will store pre-computed synergy scores between all card pairs,
allowing for fast querying of synergies without re-analysis.
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import create_app
from src.database import db
from src.models.card_synergy import CardSynergy

def check_table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists in the database."""
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def create_synergy_table():
    """Create the card_synergy table."""
    print("🔧 DATABASE MIGRATION: Creating card_synergy table")
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
        return

    print(f"📂 Found database: {db_path}")

    # Connect directly to SQLite to check and create table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table already exists
        if check_table_exists(cursor, 'card_synergy'):
            print("✅ card_synergy table already exists!")

            # Show current row count
            cursor.execute("SELECT COUNT(*) FROM card_synergy")
            count = cursor.fetchone()[0]
            print(f"📊 Current synergy records: {count}")
            return

        print("➕ Creating card_synergy table...")

        # Create the table with all necessary columns and indexes
        cursor.execute("""
            CREATE TABLE card_synergy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card1_id INTEGER NOT NULL,
                card2_id INTEGER NOT NULL,
                total_score REAL NOT NULL,
                synergy_breakdown TEXT,
                tribal_score REAL DEFAULT 0,
                color_score REAL DEFAULT 0,
                keyword_score REAL DEFAULT 0,
                archetype_score REAL DEFAULT 0,
                combo_score REAL DEFAULT 0,
                type_score REAL DEFAULT 0,
                mana_curve_score REAL DEFAULT 0,
                format_score REAL DEFAULT 0,
                analysis_version VARCHAR(20) DEFAULT '1.0',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card1_id) REFERENCES card_info (id),
                FOREIGN KEY (card2_id) REFERENCES card_info (id),
                UNIQUE (card1_id, card2_id)
            )
        """)

        # Create indexes for fast querying
        indexes = [
            "CREATE INDEX idx_synergy_score ON card_synergy (total_score)",
            "CREATE INDEX idx_tribal_synergy ON card_synergy (tribal_score)",
            "CREATE INDEX idx_combo_synergy ON card_synergy (combo_score)",
            "CREATE INDEX idx_archetype_synergy ON card_synergy (archetype_score)",
            "CREATE INDEX idx_card1_synergies ON card_synergy (card1_id)",
            "CREATE INDEX idx_card2_synergies ON card_synergy (card2_id)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        conn.commit()

        print("✅ Successfully created card_synergy table!")
        print("✅ All indexes created for fast querying!")

        # Show table schema
        cursor.execute("PRAGMA table_info(card_synergy)")
        columns = cursor.fetchall()
        print(f"\n📋 card_synergy table structure:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")

        # Show how many cards are available for synergy analysis
        cursor.execute("SELECT COUNT(*) FROM card_info WHERE extracted_data IS NOT NULL")
        analyzed_count = cursor.fetchone()[0]
        total_pairs = (analyzed_count * (analyzed_count - 1)) // 2

        print(f"\n📊 Synergy Analysis Potential:")
        print(f"  Analyzed cards: {analyzed_count}")
        print(f"  Possible synergy pairs: {total_pairs:,}")
        print(f"  Ready for bulk synergy computation!")

    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """Main function."""
    try:
        create_synergy_table()
        print("\n🎉 Migration completed successfully!")
        print("You can now run bulk synergy computation to populate the table.")
        print("Next step: python scripts/compute_all_synergies.py")
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
