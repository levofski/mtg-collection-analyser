from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models.card import Card

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
