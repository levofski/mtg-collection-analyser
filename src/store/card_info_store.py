"""
Store module for CardInfo model operations.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models.card_info import CardInfo

logger = logging.getLogger(__name__)

def get_or_create_card_info(name: str) -> Tuple[CardInfo, bool]:
    """
    Get an existing CardInfo by name or create a new one if it doesn't exist.

    Args:
        name: The name of the card.

    Returns:
        A tuple containing:
        - The CardInfo object
        - A boolean indicating if a new CardInfo was created (True) or an existing one was found (False)
    """
    # Look for existing card info with the same name
    card_info = CardInfo.query.filter_by(name=name).first()

    if card_info:
        return card_info, False

    # Create new card info
    card_info = CardInfo(name=name)
    db.session.add(card_info)

    try:
        db.session.commit()
        return card_info, True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating CardInfo: {str(e)}")
        raise e

def get_all_cards_info() -> List[CardInfo]:
    """
    Retrieves all unique cards.

    Returns:
        A list of all CardInfo objects.
    """
    return CardInfo.query.all()

def get_card_info_by_id(card_info_id: int) -> Optional[CardInfo]:
    """
    Retrieves a specific card info by its ID.

    Args:
        card_info_id: The ID of the card info to retrieve.

    Returns:
        The CardInfo object if found, None otherwise.
    """
    return CardInfo.query.get(card_info_id)

def get_card_info_by_name(name: str) -> Optional[CardInfo]:
    """
    Retrieves a specific card info by name.

    Args:
        name: The name of the card to retrieve.

    Returns:
        The CardInfo object if found, None otherwise.
    """
    return CardInfo.query.filter_by(name=name).first()

def update_card_info(card_info_id: int, updated_data: Dict[str, Any]) -> Optional[CardInfo]:
    """
    Updates a card info with new data.

    Args:
        card_info_id: The ID of the card info to update.
        updated_data: Dictionary containing the fields to update.

    Returns:
        The updated CardInfo object if found, None otherwise.
    """
    card_info = CardInfo.query.get(card_info_id)
    if card_info:
        for key, value in updated_data.items():
            if hasattr(card_info, key):
                setattr(card_info, key, value)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating CardInfo: {str(e)}")
            raise e
    return card_info

def delete_card_info(card_info_id: int) -> bool:
    """
    Deletes a card info and all associated printings.

    Args:
        card_info_id: The ID of the card info to delete.

    Returns:
        True if successfully deleted, False if the card info was not found.
    """
    card_info = CardInfo.query.get(card_info_id)
    if card_info:
        try:
            # The related card printings will be deleted by the database
            # if we set up CASCADE DELETE in the relationship
            db.session.delete(card_info)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting CardInfo: {str(e)}")
            raise e
    return False
