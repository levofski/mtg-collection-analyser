#!/usr/bin/env python3
"""
Script to demonstrate card text analysis with data from the actual database.
"""
import os
import sys
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from src.database import db
from src.models.card_info import CardInfo
from src.services.text_analysis import analyze_card_text
from src.services.card_analysis import analyze_card, analyze_all_cards

def setup_app():
    """Create and configure a Flask app for the demonstration."""
    # Create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/mtg_collection.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)
    return app

def demo_analyze_single_card(card_id=None, card_name=None):
    """
    Analyze a single card by ID or name.

    Args:
        card_id: The ID of the card to analyze
        card_name: The name of the card to analyze (used if card_id is None)
    """
    app = setup_app()

    with app.app_context():
        if card_id:
            card_info = CardInfo.query.get(card_id)
        elif card_name:
            card_info = CardInfo.query.filter(CardInfo.name.ilike(f"%{card_name}%")).first()
        else:
            # Get a random card with oracle text
            card_info = CardInfo.query.filter(CardInfo.oracle_text.isnot(None)).order_by(db.func.random()).first()

        if not card_info:
            print("No card found to analyze.")
            return

        print(f"Analyzing card: {card_info.name}")
        print(f"Oracle text: {card_info.oracle_text}")
        print("-" * 60)

        # Analyze the card
        updated_card, message = analyze_card(card_info.id)
        print(f"Analysis result: {message}")

        if updated_card and updated_card.keywords:
            print(f"Keywords: {updated_card.keywords}")
        if updated_card and updated_card.extracted_data:
            data = updated_card.extracted_data
            print("\nExtracted information:")
            if data.get("actions"):
                print(f"Actions: {data.get('actions')}")
            if data.get("zones"):
                print(f"Zones: {data.get('zones')}")
            if data.get("mana_references"):
                print(f"Mana References: {data.get('mana_references')}")
            if data.get("noun_phrases"):
                print(f"Noun phrases: {data.get('noun_phrases')[:5]}...")

def demo_analyze_batch(limit=10):
    """
    Analyze a batch of cards.

    Args:
        limit: Maximum number of cards to analyze
    """
    app = setup_app()

    with app.app_context():
        # Get cards that haven't been analyzed yet (no keywords)
        cards = CardInfo.query.filter(
            CardInfo.oracle_text.isnot(None),
            CardInfo._keywords.is_(None)
        ).limit(limit).all()

        if not cards:
            print(f"No cards found that need analysis. Picking random cards instead.")
            cards = CardInfo.query.filter(
                CardInfo.oracle_text.isnot(None)
            ).order_by(db.func.random()).limit(limit).all()

        print(f"Analyzing {len(cards)} cards...")

        for idx, card in enumerate(cards, 1):
            print(f"\n{idx}. {card.name}")
            print(f"Oracle text: {card.oracle_text}")

            # Analyze the card
            updated_card, message = analyze_card(card.id)
            print(f"Analysis result: {message}")

            if updated_card and updated_card.keywords:
                print(f"Keywords: {updated_card.keywords}")

            print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Demonstrate card text analysis.')
    parser.add_argument('--id', type=int, help='Analyze a card by ID')
    parser.add_argument('--name', type=str, help='Analyze a card by name (case insensitive, partial match)')
    parser.add_argument('--batch', type=int, help='Analyze a batch of cards (specify count)')

    args = parser.parse_args()

    if args.batch:
        demo_analyze_batch(args.batch)
    else:
        demo_analyze_single_card(args.id, args.name)
