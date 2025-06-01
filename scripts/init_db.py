#!/usr/bin/env python3
"""
Script to initialize the database structure for the MTG Collection Analyzer.
This script creates the necessary tables for the new schema with CardInfo and CardPrinting models.
"""
import os
import sys
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from sqlalchemy import inspect
from src.database import db
from src.models.card_info import CardInfo
from src.models.card_printing import CardPrinting

def init_db(drop_all=False):
    """
    Create a Flask app and initialize the database.

    Args:
        drop_all: If True, drops all tables before creating them
    """
    # Create the instance directory if it doesn't exist
    instance_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../instance"))
    os.makedirs(instance_dir, exist_ok=True)

    # Create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_dir, 'mtg_collection.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)

    # Create all tables
    with app.app_context():
        if drop_all:
            print("Dropping all tables...")
            db.drop_all()

        db.create_all()
        print(f"Database initialized at {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Check table counts for new schema
        card_info_count = db.session.query(db.func.count(CardInfo.id)).scalar()
        card_printing_count = db.session.query(db.func.count(CardPrinting.id)).scalar()

        print(f"Database contains:")
        print(f"  - {card_info_count} card infos (unique cards)")
        print(f"  - {card_printing_count} card printings (collection items)")

        # Check if the old cards table exists
        inspector = inspect(db.engine)
        if inspector.has_table('cards'):
            # The old table exists, but we don't import the model anymore
            try:
                from sqlalchemy import text
                result = db.session.execute(text("SELECT count(*) FROM cards")).scalar()
                if result is not None:
                    print(f"  - {result} cards (old schema)")
                    print("  - To migrate from old to new schema, run migrate_card_data.py")
            except Exception as e:
                print(f"  - Old 'cards' table exists but could not get count: {e}")
        else:
            print("  - No old schema tables found (this is normal for new installations)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize the MTG collection database.')
    parser.add_argument('--drop', action='store_true', help='Drop all tables before creating them')
    args = parser.parse_args()

    init_db(args.drop)
