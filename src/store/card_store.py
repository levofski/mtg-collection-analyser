from typing import List, Dict, Any

# In-memory store for the card collection
# This will be reset if the Flask application restarts.
_card_collection: List[Dict[str, Any]] = []

def add_cards_to_collection(cards: List[Dict[str, Any]]) -> None:
    """
    Adds a list of cards to the in-memory collection.

    Args:
        cards: A list of dictionaries, where each dictionary represents a card.
    """
    global _card_collection
    # For simplicity, we're appending. If duplicates matter based on certain fields,
    # more complex logic would be needed here (e.g., checking for existing cards
    # and updating counts or merging data).
    _card_collection.extend(cards)

def get_all_cards() -> List[Dict[str, Any]]:
    """
    Retrieves all cards currently in the in-memory collection.

    Returns:
        A list of all cards in the collection.
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
