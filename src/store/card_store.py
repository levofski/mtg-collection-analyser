from typing import List, Dict, Any, Optional, Tuple
import logging
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models.card import Card
from ..services.scryfall_service import scryfall

# Configure logging
logger = logging.getLogger(__name__)

def add_cards_to_collection(cards: List[Card]) -> None:
    """
    Adds a list of cards to the database collection.

    Args:
        cards: A list of Card objects to add to the collection.
    """
    try:
        db.session.add_all(cards)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        # In a real application, you might want to log this error
        raise e

def get_all_cards() -> List[Card]:
    """
    Retrieves all cards currently in the collection.

    Returns:
        A list of all Card objects in the collection.
    """
    return Card.query.all()

def get_card_by_id(card_id: int) -> Optional[Card]:
    """
    Retrieves a specific card by its ID.

    Args:
        card_id: The ID of the card to retrieve.

    Returns:
        The Card object if found, None otherwise.
    """
    return Card.query.get(card_id)

def update_card(card_id: int, updated_data: Dict[str, Any]) -> Optional[Card]:
    """
    Updates a card with new data.

    Args:
        card_id: The ID of the card to update.
        updated_data: Dictionary containing the fields to update.

    Returns:
        The updated Card object if found, None otherwise.
    """
    card = Card.query.get(card_id)
    if card:
        for key, value in updated_data.items():
            if hasattr(card, key):
                setattr(card, key, value)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            # In a real application, you might want to log this error
            raise e
    return card

def delete_card(card_id: int) -> bool:
    """
    Deletes a card from the collection.

    Args:
        card_id: The ID of the card to delete.

    Returns:
        True if successfully deleted, False if the card was not found.
    """
    card = Card.query.get(card_id)
    if card:
        try:
            db.session.delete(card)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            # In a real application, you might want to log this error
            raise e
    return False

def clear_collection() -> None:
    """
    Clears all cards from the collection.
    Useful for testing or resetting state.
    """
    try:
        Card.query.delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        # In a real application, you might want to log this error
        raise e

def enrich_card_with_scryfall_data(card_id: int) -> Tuple[Optional[Card], str]:
    """
    Enriches a card with data from the Scryfall API.

    Args:
        card_id: The ID of the card to enrich.

    Returns:
        A tuple containing:
        - The enriched Card object if found, None otherwise.
        - A message describing the result of the operation.
    """
    card = Card.query.get(card_id)
    if not card:
        return None, f"Card with ID {card_id} not found."

    try:
        # Convert card to dict for Scryfall service
        card_dict = {
            'Name': card.Name,
            'Edition_Code': card.Edition_Code,
            'Card_Number': card.Card_Number,
            'Scryfall_ID': card.scryfall_id  # Include the Scryfall ID if it was imported from CSV
        }

        # Fetch card data from Scryfall
        scryfall_data = scryfall.enrich_card(card_dict)

        # Update card with Scryfall data
        card.scryfall_id = scryfall_data.get('id')
        card.oracle_text = scryfall_data.get('oracle_text')
        card.mana_cost = scryfall_data.get('mana_cost')
        card.cmc = scryfall_data.get('cmc')
        card.type_line = scryfall_data.get('type_line')

        # Handle image URIs (using the property setter)
        card.image_uris = scryfall_data.get('image_uris')

        # Save to database
        db.session.commit()
        return card, "Card enriched successfully."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enriching card {card_id}: {str(e)}")
        return card, f"Error enriching card: {str(e)}"

def enrich_all_cards() -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Enriches all cards in the collection with data from the Scryfall API.

    Returns:
        A tuple containing:
        - Number of successfully enriched cards.
        - Total number of cards processed.
        - List of errors that occurred during enrichment.
    """
    cards = Card.query.all()
    total_cards = len(cards)
    successful = 0
    errors = []

    for card in cards:
        try:
            # Convert card to dict for Scryfall service
            card_dict = {
                'Name': card.Name,
                'Edition_Code': card.Edition_Code,
                'Card_Number': card.Card_Number,
                'Scryfall_ID': card.scryfall_id  # Include the Scryfall ID if it was imported from CSV
            }

            # Fetch card data from Scryfall
            scryfall_data = scryfall.enrich_card(card_dict)

            # Update card with Scryfall data
            card.scryfall_id = scryfall_data.get('id')
            card.oracle_text = scryfall_data.get('oracle_text')
            card.mana_cost = scryfall_data.get('mana_cost')
            card.cmc = scryfall_data.get('cmc')
            card.type_line = scryfall_data.get('type_line')

            # Handle image URIs (using the property setter)
            card.image_uris = scryfall_data.get('image_uris')

            successful += 1
        except Exception as e:
            errors.append({
                "card_id": card.id,
                "card_name": card.Name,
                "error": str(e)
            })
            logger.error(f"Error enriching card {card.id} ({card.Name}): {str(e)}")

    # Save all changes
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        errors.append({"error": f"Database error: {str(e)}"})
        logger.error(f"Database error when enriching cards: {str(e)}")

    return successful, total_cards, errors
