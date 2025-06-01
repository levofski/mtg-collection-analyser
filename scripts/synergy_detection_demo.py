#!/usr/bin/env python3
"""
Demonstrates synergy detection between MTG cards using text analysis.
"""
import os
import sys
from typing import List, Dict, Any, Set

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.text_analysis import analyze_card_text, find_synergy_candidates

# Sample cards for synergy detection
SAMPLE_CARDS = [
    {
        "name": "Reanimate",
        "oracle_text": "Put target creature card from a graveyard onto the battlefield under your control. You lose life equal to its converted mana cost."
    },
    {
        "name": "Entomb",
        "oracle_text": "Search your library for a card and put that card into your graveyard. Then shuffle your library."
    },
    {
        "name": "Griselbrand",
        "oracle_text": "Flying, lifelink\nPay 7 life: Draw seven cards. Activate only once each turn."
    },
    {
        "name": "Exhume",
        "oracle_text": "Each player puts a creature card from their graveyard onto the battlefield."
    },
    {
        "name": "Animate Dead",
        "oracle_text": "Enchant creature card in a graveyard\nWhen Animate Dead enters the battlefield, if it's on the battlefield, it loses \"enchant creature card in a graveyard\" and gains \"enchant creature put onto the battlefield with Animate Dead.\" Return enchanted creature card to the battlefield under your control and attach Animate Dead to it. When Animate Dead leaves the battlefield, that creature's controller sacrifices it."
    },
    {
        "name": "Grafdigger's Cage",
        "oracle_text": "Creature cards in graveyards and libraries can't enter the battlefield.\nPlayers can't cast spells from graveyards or libraries."
    }
]

def analyze_cards() -> List[Dict[str, Any]]:
    """
    Analyze all sample cards and return their analyzed data.
    """
    analyzed_cards = []

    for card in SAMPLE_CARDS:
        analysis = analyze_card_text(card["oracle_text"])
        analyzed_cards.append({
            "name": card["name"],
            "oracle_text": card["oracle_text"],
            "analysis": analysis
        })

    return analyzed_cards

def detect_synergies(cards: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Detect potential synergies between cards.

    Args:
        cards: List of analyzed card data

    Returns:
        Dictionary mapping card names to lists of synergistic card names
    """
    synergies = {}

    # Extract relevant keywords from all cards
    collection_keywords: Set[str] = set()
    for card in cards:
        # Add all card names as keywords
        collection_keywords.add(card["name"].lower())

        # Add zones, actions, and explicit keywords
        analysis = card["analysis"]
        for category in ["zones", "actions", "keywords"]:
            collection_keywords.update(analysis.get(category, []))

    # Find synergies for each card
    for card in cards:
        synergy_matches = []

        # Find cards that synergize with this card's text
        for other_card in cards:
            if other_card["name"] == card["name"]:
                continue

            # Check if this card's text mentions zones/actions that other cards use
            for category in ["zones", "actions", "keywords"]:
                for keyword in other_card["analysis"].get(category, []):
                    if keyword in card["oracle_text"].lower():
                        if other_card["name"] not in synergy_matches:
                            synergy_matches.append(other_card["name"])

        synergies[card["name"]] = synergy_matches

    return synergies

def main():
    """Run the synergy detection demo."""
    print("MTG Card Synergy Detection Demo")
    print("==============================\n")

    # Analyze all cards
    analyzed_cards = analyze_cards()

    # Display card analyses
    for card in analyzed_cards:
        print(f"CARD: {card['name']}")
        print(f"TEXT: {card['oracle_text'][:100]}..." if len(card['oracle_text']) > 100 else card['oracle_text'])

        analysis = card["analysis"]
        print("ANALYSIS:")
        for category, items in analysis.items():
            if items and category in ["keywords", "actions", "zones", "mana_references"]:
                print(f"- {category}: {', '.join(items)}")
        print()

    # Detect synergies between cards
    synergies = detect_synergies(analyzed_cards)

    # Display synergies
    print("SYNERGIES DETECTED:")
    print("==================\n")

    for card_name, matches in synergies.items():
        if matches:
            print(f"{card_name} synergizes with: {', '.join(matches)}")
        else:
            print(f"{card_name}: No synergies detected")

    print("\nDone!")

if __name__ == "__main__":
    main()
