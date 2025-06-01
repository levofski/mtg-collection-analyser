#!/usr/bin/env python3
"""
Standalone demo script for the card text analysis functionality.
"""
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    },
    {
        "name": "Snapcaster Mage",
        "oracle_text": "Flash\nWhen Snapcaster Mage enters the battlefield, target instant or sorcery card in your graveyard gains flashback until end of turn. The flashback cost is equal to its mana cost."
    }
]

def main():
    """
    Run the text analysis on sample cards and display the results.
    """
    print("MTG Card Text Analysis Demo")
    print("==========================\n")

    for card in SAMPLE_CARDS:
        print(f"CARD: {card['name']}")
        print(f"TEXT: {card['oracle_text']}")
        print("-" * 60)

        # Analyze the card text
        analysis = analyze_card_text(card['oracle_text'])

        # Display the results in a readable format
        print("ANALYSIS RESULTS:")
        if analysis.get('keywords'):
            print(f"Keywords: {', '.join(analysis['keywords'])}")
        else:
            print("Keywords: None found")

        if analysis.get('actions'):
            print(f"Actions: {', '.join(analysis['actions'])}")

        if analysis.get('zones'):
            print(f"Zones: {', '.join(analysis['zones'])}")

        if analysis.get('mana_references'):
            print(f"Mana References: {', '.join(analysis['mana_references'])}")

        print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
