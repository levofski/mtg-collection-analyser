from typing import List

from ..models.card import Card

# In-memory store for the card collection
# This will be reset if the Flask application restarts.
_card_collection: List[Card] = []

def add_cards_to_collection(cards: List[Card]) -> None:
    """
    Adds a list of cards to the in-memory collection.

    Args:
        cards: A list of Card objects to add to the collection.
    """
    global _card_collection
    # For simplicity, we're appending. If duplicates matter based on certain fields,
    # more complex logic would be needed here (e.g., checking for existing cards
    # and updating counts or merging data).
    _card_collection.extend(cards)

def get_all_cards() -> List[Card]:
    """
    Retrieves all cards currently in the in-memory collection.

    Returns:
        A list of all Card objects in the collection.
    """
    global _card_collection
    return _card_collection

def clear_collection() -> None:
    """
    Clears all cards from the in-memory collection.
    Useful for testing or resetting state.
    """
    global _card_collection
    _card_collection = []
