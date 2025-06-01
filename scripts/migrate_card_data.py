"""
Migration script to transfer data from the old Card model to the new CardInfo and CardPrinting models.
"""
import logging
from typing import Dict, Any, Set, Tuple
import sys
import os
import pathlib

# Add the project root to the Python path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from src.database import db
from src.models.card import Card
from src.models.card_info import CardInfo
from src.models.card_printing import CardPrinting

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create a minimal Flask app for database operations."""
    # Ensure instance folder exists
    instance_path = pathlib.Path("instance")
    instance_path.mkdir(exist_ok=True)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/mtg_collection.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def migrate_data() -> Tuple[int, int]:
    """
    Migrate data from the old Card model to CardInfo and CardPrinting models.

    Returns:
        A tuple with:
        - The number of unique cards migrated to CardInfo
        - The number of printings migrated to CardPrinting
    """
    # Track unique cards by name to avoid duplicates
    unique_cards: Dict[str, CardInfo] = {}

    # Get all existing cards from the old model
    old_cards = Card.query.all()
    logger.info(f"Found {len(old_cards)} cards to migrate")

    for old_card in old_cards:
        # First, see if we already have a CardInfo for this card name
        if old_card.Name in unique_cards:
            card_info = unique_cards[old_card.Name]
        else:
            # Create a new CardInfo instance
            card_info = CardInfo(
                name=old_card.Name,
                oracle_text=old_card.oracle_text,
                mana_cost=old_card.mana_cost,
                cmc=old_card.cmc,
                type_line=old_card.type_line
            )
            db.session.add(card_info)
            unique_cards[old_card.Name] = card_info

        # Create a CardPrinting instance linked to the CardInfo
        card_printing = CardPrinting(
            card_info=card_info,
            Count=old_card.Count,
            Tradelist_Count=old_card.Tradelist_Count,
            Edition=old_card.Edition,
            Edition_Code=old_card.Edition_Code,
            Card_Number=old_card.Card_Number,
            Condition=old_card.Condition,
            Language=old_card.Language,
            Foil=old_card.Foil,
            Signed=old_card.Signed,
            Artist_Proof=old_card.Artist_Proof,
            Altered_Art=old_card.Altered_Art,
            Misprint=old_card.Misprint,
            Promo=old_card.Promo,
            Textless=old_card.Textless,
            Printing_Id=old_card.Printing_Id,
            Printing_Note=old_card.Printing_Note,
            Tags=old_card.Tags,
            My_Price=old_card.My_Price,
            scryfall_id=old_card.scryfall_id,
        )

        # Set image_uris if available
        if old_card.image_uris:
            card_printing.image_uris = old_card.image_uris

        db.session.add(card_printing)

    # Commit all changes
    db.session.commit()
    logger.info(f"Migration completed: {len(unique_cards)} unique cards and {len(old_cards)} printings")
    return len(unique_cards), len(old_cards)

def main():
    """Main entry point for the migration script."""
    app = create_app()

    with app.app_context():
        # Create the new tables if they don't exist
        db.create_all()

        # Check if there's data to migrate
        old_count = db.session.query(db.func.count(Card.id)).scalar()
        if old_count == 0:
            logger.info("No cards to migrate. The old cards table is empty.")
            return

        # Check if we've already migrated data
        info_count = db.session.query(db.func.count(CardInfo.id)).scalar()
        printing_count = db.session.query(db.func.count(CardPrinting.id)).scalar()

        if info_count > 0 or printing_count > 0:
            logger.warning("It looks like a migration has already been performed.")
            logger.warning(f"Found {info_count} card info entries and {printing_count} printing entries.")
            response = input("Do you want to proceed anyway? This might create duplicates. (y/N): ")
            if response.lower() != 'y':
                logger.info("Migration aborted by user.")
                return

        try:
            # Perform the migration
            unique_count, printing_count = migrate_data()
            logger.info(f"Successfully migrated {unique_count} unique cards and {printing_count} card printings.")
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == "__main__":
    main()
