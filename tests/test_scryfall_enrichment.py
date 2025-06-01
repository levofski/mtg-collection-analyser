"""
Test script for the Scryfall enrichment functionality.

This script tests the enrichment functionality by:
1. Creating a Flask test client
2. Adding some test cards to the collection
3. Enriching them with Scryfall data
4. Verifying the enriched data
"""
import os
import sys
import unittest
from flask import Flask

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.card import Card
from src.services.scryfall_service import scryfall
from main import create_app


class TestScryfallEnrichment(unittest.TestCase):
    """Test case for Scryfall enrichment functionality."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            # Import here to avoid circular imports
            from src.database import db
            db.create_all()

            # Add test cards
            self._add_test_cards()

    def _add_test_cards(self):
        """Add test cards to the database."""
        from src.database import db

        cards = [
            Card(
                Name="Lightning Bolt",
                Count=4,
                Edition="Masters 25",
                Edition_Code="a25",
                Card_Number="141"
            ),
            Card(
                Name="Black Lotus",
                Count=1,
                Edition="Alpha",
                Edition_Code="lea",
                Card_Number="232"
            ),
            Card(
                Name="Birds of Paradise",
                Count=2,
                Edition="Ravnica Allegiance: Guild Kits",
                Edition_Code="gk2",
                Card_Number="82"
            )
        ]

        db.session.add_all(cards)
        db.session.commit()

    def test_enriching_single_card(self):
        """Test enriching a single card."""
        # Enrich the first card (ID 1)
        response = self.client.post('/collection/cards/1/enrich')
        self.assertEqual(response.status_code, 200)

        # Check if the card was enriched with Scryfall data
        response = self.client.get('/collection/cards/1')
        self.assertEqual(response.status_code, 200)

        card_data = response.get_json()
        self.assertIn('scryfall_id', card_data)
        self.assertIn('oracle_text', card_data)
        self.assertIn('mana_cost', card_data)
        self.assertEqual(card_data['mana_cost'], '{R}')

    def test_enriching_all_cards(self):
        """Test enriching all cards in the collection."""
        # Enrich all cards
        response = self.client.post('/collection/enrich-all')
        self.assertEqual(response.status_code, 200)

        # Check if all cards were enriched
        response = self.client.get('/collection/cards')
        self.assertEqual(response.status_code, 200)

        cards = response.get_json()['cards']
        self.assertEqual(len(cards), 3)

        # Check that all cards have Scryfall data
        for card in cards:
            self.assertIn('scryfall_id', card)
            self.assertIn('oracle_text', card)
            self.assertIn('mana_cost', card)

if __name__ == '__main__':
    unittest.main()
