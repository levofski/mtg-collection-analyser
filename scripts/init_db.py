#!/usr/bin/env python3
"""
Script to initialize the database structure.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from src.database import db
from src.models.card import Card
from src.models.card_info import CardInfo
from src.models.card_printing import CardPrinting

def init_db():
    """Create a Flask app and initialize the database."""
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
        db.create_all()
        print(f"Database initialized at {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == "__main__":
    init_db()
