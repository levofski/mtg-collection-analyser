#!/usr/bin/env python3
"""
Manual test script for the card text analysis functionality.
"""
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from src.database import db
from src.models.card_info import CardInfo
from src.services.text_analysis import analyze_card_text

# Sample card texts for testing
SAMPLE_CARDS = [
    {
        "name": "Lightning Bolt",
        "oracle_text": "Lightning Bolt deals 3 damage to any target."
    },
    {
        "name": "Birds of Paradise",
        "oracle_text": "Flying\nTap: Add one mana of any color."
    },
    {
        "name": "Swords to Plowshares",
        "oracle_text": "Exile target creature. Its controller gains life equal to its power."
    },
    {
        "name": "Cryptic Command",
        "oracle_text": "Choose two —\n• Counter target spell.\n• Return target permanent to its owner's hand.\n• Tap all creatures your opponents control.\n• Draw a card."
    },
    {
        "name": "Craterhoof Behemoth",
        "oracle_text": "Trample\nWhen Craterhoof Behemoth enters the battlefield, creatures you control gain trample and get +X/+X until end of turn, where X is the number of creatures you control."
    }
]

def test_text_analysis():
    """
    Test the text analysis functionality with sample card texts.
    """
    print("Testing card text analysis:")
    print("=" * 50)

    for card in SAMPLE_CARDS:
        print(f"\nAnalyzing: {card['name']}")
        print("-" * 50)
        print(f"Oracle text: {card['oracle_text']}")
        print("-" * 50)

        # Analyze the card text
        analysis_result = analyze_card_text(card['oracle_text'])

        # Print the analysis results in a readable format
        print("Analysis results:")
        for key, value in analysis_result.items():
            if value:
                print(f"  {key}:")
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            print(f"    - {json.dumps(item)}")
                        else:
                            print(f"    - {item}")
                else:
                    print(f"    {value}")
        print("=" * 50)

def test_database_integration():
    """
    Test the database integration for text analysis.
    """
    # Create a simplified version of the CardInfo model for testing purposes
    class TestCardInfo:
        def __init__(self, name, oracle_text):
            self.name = name
            self.oracle_text = oracle_text
            self.keywords = None
            self.extracted_data = None

    print("\nTesting database integration:")
    print("=" * 50)

    # Create test card info records
    card_infos = []
    for card in SAMPLE_CARDS:
        card_info = TestCardInfo(card['name'], card['oracle_text'])
        card_infos.append(card_info)

    # Analyze each card and store results
    for card_info in card_infos:
        analysis_result = analyze_card_text(card_info.oracle_text)
        card_info.keywords = analysis_result.get('keywords', [])
        card_info.extracted_data = analysis_result

    # Verify the results
    for card_info in card_infos:
        print(f"\nVerifying analysis for: {card_info.name}")
        print("-" * 50)
        print(f"Keywords: {card_info.keywords}")

        if card_info.extracted_data:
            print(f"Actions: {card_info.extracted_data.get('actions', [])}")
            print(f"Zones: {card_info.extracted_data.get('zones', [])}")

        print("-" * 50)

    print("=" * 50)

if __name__ == "__main__":
    test_text_analysis()
    test_database_integration()
