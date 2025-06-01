from typing import List, Dict, Any, Optional, Tuple
import logging
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models.card_printing import CardPrinting
from ..models.card_info import CardInfo
from ..services.scryfall_service import scryfall
from ..store.card_info_store import get_card_info_by_id, update_card_info

# Configure logging
logger = logging.getLogger(__name__)

def add_cards_to_collection(printings: List[CardPrinting]) -> None:
    """
    Adds a list of card printings to the database collection.

    Args:
        printings: A list of CardPrinting objects to add to the collection.
    """
    try:
        db.session.add_all(printings)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error adding cards to collection: {str(e)}")
        raise e

def get_all_cards() -> List[CardPrinting]:
    """
    Retrieves all card printings currently in the collection.

    Returns:
        A list of all CardPrinting objects in the collection.
    """
    return CardPrinting.query.all()

def get_card_by_id(card_id: int) -> Optional[CardPrinting]:
    """
    Retrieves a specific card printing by its ID.

    Args:
        card_id: The ID of the card printing to retrieve.

    Returns:
        The CardPrinting object if found, None otherwise.
    """
    return CardPrinting.query.get(card_id)

def update_card(card_id: int, updated_data: Dict[str, Any]) -> Optional[CardPrinting]:
    """
    Updates a card printing with new data.

    Args:
        card_id: The ID of the card printing to update.
        updated_data: Dictionary containing the fields to update.

    Returns:
        The updated CardPrinting object if found, None otherwise.
    """
    card_printing = CardPrinting.query.get(card_id)
    if card_printing:
        # Determine which fields should update the CardInfo vs CardPrinting
        card_info_fields = ['name', 'oracle_text', 'mana_cost', 'cmc', 'type_line', 'oracle_id']
        card_info_updates = {}

        for key, value in updated_data.items():
            if key.lower() in card_info_fields:
                # This field should update the CardInfo
                card_info_updates[key.lower()] = value
            elif hasattr(card_printing, key):
                # This field should update the CardPrinting
                setattr(card_printing, key, value)

        # Update CardInfo if needed
        if card_info_updates:
            update_card_info(card_printing.card_info_id, card_info_updates)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating card: {str(e)}")
            raise e
    return card_printing

def delete_card(card_id: int) -> bool:
    """
    Deletes a card printing from the collection.

    Args:
        card_id: The ID of the card printing to delete.

    Returns:
        True if successfully deleted, False if the card was not found.
    """
    card_printing = CardPrinting.query.get(card_id)
    if card_printing:
        try:
            db.session.delete(card_printing)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting card: {str(e)}")
            raise e
    return False

def clear_collection() -> None:
    """
    Clears all card printings from the collection.
    Useful for testing or resetting state.
    """
    try:
        CardPrinting.query.delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error clearing collection: {str(e)}")
        raise e

def enrich_card_with_scryfall_data(card_id: int) -> Tuple[Optional[CardPrinting], str]:
    """
    Enriches a card printing and its associated card info with data from the Scryfall API.

    Args:
        card_id: The ID of the card printing to enrich.

    Returns:
        A tuple containing:
        - The enriched CardPrinting object if found, None otherwise.
        - A message describing the result of the operation.
    """
    card_printing = CardPrinting.query.get(card_id)
    if not card_printing:
        return None, f"Card with ID {card_id} not found."

    try:
        # Get the associated card info
        card_info = card_printing.card_info

        # Convert card to dict for Scryfall service
        card_dict = {
            'Name': card_info.name,
            'Edition_Code': card_printing.Edition_Code,
            'Card_Number': card_printing.Card_Number,
            'scryfall_id': card_printing.scryfall_id  # Include the Scryfall ID if it was imported from CSV
        }

        # Fetch card data from Scryfall
        scryfall_data = scryfall.enrich_card(card_dict)

        # Update card printing with Scryfall data
        card_printing.scryfall_id = scryfall_data.get('id')

        # Update card info with shared Scryfall data
        card_info.oracle_text = scryfall_data.get('oracle_text')
        card_info.mana_cost = scryfall_data.get('mana_cost')
        card_info.cmc = scryfall_data.get('cmc')
        card_info.type_line = scryfall_data.get('type_line')
        card_info.oracle_id = scryfall_data.get('oracle_id')

        # Handle image URIs (using the property setter)
        card_printing.image_uris = scryfall_data.get('image_uris')

        # Save to database
        db.session.commit()
        return card_printing, "Card enriched successfully."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enriching card {card_id}: {str(e)}")
        return card_printing, f"Error enriching card: {str(e)}"

def enrich_all_cards() -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Enriches all cards in the collection with data from the Scryfall API.
    Commits changes to the database after each successful card enrichment.

    Returns:
        A tuple containing:
        - Number of successfully enriched cards.
        - Total number of cards processed.
        - List of errors that occurred during enrichment.
    """
    card_printings = CardPrinting.query.all()
    total_cards = len(card_printings)
    successful = 0
    errors = []

    for card_printing in card_printings:
        try:
            card_info = card_printing.card_info

            # Convert card to dict for Scryfall service
            card_dict = {
                'Name': card_info.name,
                'Edition_Code': card_printing.Edition_Code,
                'Card_Number': card_printing.Card_Number,
                'scryfall_id': card_printing.scryfall_id
            }

            # Fetch card data from Scryfall
            scryfall_data = scryfall.enrich_card(card_dict)

            # Update card printing with Scryfall data
            card_printing.scryfall_id = scryfall_data.get('id')

            # Update card info with shared Scryfall data
            card_info.oracle_text = scryfall_data.get('oracle_text')
            card_info.mana_cost = scryfall_data.get('mana_cost')
            card_info.cmc = scryfall_data.get('cmc')
            card_info.type_line = scryfall_data.get('type_line')
            card_info.oracle_id = scryfall_data.get('oracle_id')

            # Handle image URIs (using the property setter)
            card_printing.image_uris = scryfall_data.get('image_uris')

            # Commit changes immediately after each card
            try:
                db.session.commit()
                successful += 1
                logger.info(f"Successfully enriched card {card_printing.id} ({card_info.name})")
            except SQLAlchemyError as db_err:
                db.session.rollback()
                error_msg = f"Database error when saving card {card_printing.id}: {str(db_err)}"
                errors.append({
                    "card_id": card_printing.id,
                    "card_name": card_info.name,
                    "error": error_msg
                })
                logger.error(error_msg)

        except Exception as e:
            # Rollback any pending changes for this card
            db.session.rollback()
            errors.append({
                "card_id": card_printing.id,
                "card_name": card_printing.card_info.name,
                "error": str(e)
            })
            logger.error(f"Error enriching card {card_printing.id} ({card_printing.card_info.name}): {str(e)}")

    return successful, total_cards, errors
