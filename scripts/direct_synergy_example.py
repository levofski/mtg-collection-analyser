#!/usr/bin/env python3
"""
Example script showing direct API usage for synergy queries.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.services.text_analysis import calculate_synergy_score
from main import create_app

def query_synergy_example():
    """Example of direct synergy querying."""
    app = create_app()

    with app.app_context():
        # Find specific cards
        card1 = CardInfo.query.filter(CardInfo.name.ilike('%Lightning Bolt%')).first()
        card2 = CardInfo.query.filter(CardInfo.name.ilike('%Goblin Guide%')).first()

        if card1 and card2:
            print(f"Analyzing synergy between '{card1.name}' and '{card2.name}'")

            # Calculate synergy
            result = calculate_synergy_score(
                card1.extracted_data or {},
                card2.extracted_data or {}
            )

            print(f"Total Score: {result['total_score']:.1f}")
            print(f"Matches: {result.get('matches', [])[:5]}")
        else:
            print("Cards not found in collection")

if __name__ == "__main__":
    query_synergy_example()
