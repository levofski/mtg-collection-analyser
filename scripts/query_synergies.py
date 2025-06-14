#!/usr/bin/env python3
"""
Interactive script to demonstrate synergy detection between specific cards.

This script shows you how to:
1. Find cards in your collection by name
2. Calculate synergy scores between cards
3. Get detailed explanations of why cards synergize
4. Explore different types of synergies
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.services.text_analysis import calculate_synergy_score
from main import create_app

def find_cards_by_name(search_term: str, limit: int = 10) -> List[CardInfo]:
    """Find cards by partial name match."""
    return CardInfo.query.filter(
        CardInfo.name.ilike(f'%{search_term}%')
    ).limit(limit).all()

def display_card_info(card: CardInfo):
    """Display detailed information about a card."""
    print(f"\n📋 {card.name}")
    print("-" * 50)
    print(f"🏷️  Type: {card.type_line or 'Unknown'}")
    print(f"💎 Mana Cost: {card.mana_cost or 'N/A'}")
    print(f"📖 Oracle Text: {(card.oracle_text[:100] + '...') if card.oracle_text and len(card.oracle_text) > 100 else card.oracle_text or 'N/A'}")

    if card.extracted_data:
        data = card.extracted_data
        if data.get('creature_types'):
            print(f"🦄 Creature Types: {', '.join(data['creature_types'][:3])}")
        if data.get('keywords'):
            print(f"⚡ Keywords: {', '.join(data['keywords'][:5])}")
        if data.get('synergy_vectors', {}).get('archetype'):
            archetypes = data['synergy_vectors']['archetype'][:3]
            print(f"🎭 Archetypes: {', '.join(archetypes)}")

def analyze_synergy_between_cards(card1: CardInfo, card2: CardInfo):
    """Analyze and display synergy between two cards."""
    print(f"\n🔗 SYNERGY ANALYSIS")
    print("=" * 60)
    print(f"Card 1: {card1.name}")
    print(f"Card 2: {card2.name}")
    print("-" * 60)    # Calculate synergy score
    synergy_result = calculate_synergy_score(
        card1.extracted_data or {},
        card2.extracted_data or {}
    )

    print(f"🎯 Total Synergy Score: {synergy_result['total_score']:.1f}/100")
    print("\n📊 Detailed Breakdown:")

    # Show breakdown of different synergy types
    synergy_types = [
        ("tribal_score", "Tribal Synergy"),
        ("color_score", "Color Synergy"),
        ("keyword_score", "Keyword Synergy"),
        ("archetype_score", "Archetype Synergy"),
        ("combo_score", "Combo Potential"),
        ("type_score", "Type Synergy"),
        ("mana_curve_score", "Mana Curve"),
        ("format_score", "Format Legality")
    ]

    for score_key, display_name in synergy_types:
        score = synergy_result.get(score_key, 0)
        if score > 0:
            print(f"  • {display_name}: {score:.1f}")

    # Show matching elements
    matches = synergy_result.get("matches", [])
    if matches:
        print(f"\n🔗 Synergy Matches:")
        for match in matches[:10]:  # Show first 10 matches
            print(f"  • {match}")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more matches")

    # Provide interpretation
    total_score = synergy_result.get('total_score', 0)
    if total_score >= 30:
        print(f"\n🔥 HIGH SYNERGY! These cards work very well together.")
    elif total_score >= 15:
        print(f"\n✨ GOOD SYNERGY! These cards complement each other nicely.")
    elif total_score >= 5:
        print(f"\n👍 MODERATE SYNERGY! Some shared elements or compatibility.")
    else:
        print(f"\n🤷 LOW SYNERGY! These cards don't have strong connections.")

def find_synergistic_cards(target_card: CardInfo, min_score: float = 10.0, limit: int = 10) -> List[tuple]:
    """Find cards that synergize well with the target card."""
    if not target_card.extracted_data:
        print(f"❌ {target_card.name} hasn't been analyzed yet.")
        return []

    print(f"\n🔍 Finding cards that synergize with '{target_card.name}'...")
    print(f"Minimum synergy score: {min_score}")

    # Get all analyzed cards
    all_cards = CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).limit(500).all()
    synergistic_cards = []

    for card in all_cards:
        if card.id == target_card.id:
            continue

        score_result = calculate_synergy_score(
            target_card.extracted_data,
            card.extracted_data or {}
        )

        score = score_result.get('total_score', 0)

        if score >= min_score:
            synergistic_cards.append((card, score))

    # Sort by synergy score (highest first)
    synergistic_cards.sort(key=lambda x: x[1], reverse=True)

    print(f"\n📋 Found {len(synergistic_cards)} synergistic cards:")
    for i, (card, score) in enumerate(synergistic_cards[:limit], 1):
        print(f"  {i}. {card.name} - Score: {score:.1f}")
        if card.type_line:
            print(f"     └─ {card.type_line}")

    return synergistic_cards[:limit]

def interactive_mode():
    """Interactive mode for exploring synergies."""
    print("🎮 INTERACTIVE SYNERGY EXPLORER")
    print("=" * 60)
    print("Enter card names to explore synergies!")
    print("Commands:")
    print("  • 'find <partial name>' - Search for cards")
    print("  • 'synergy <card1> | <card2>' - Compare two cards")
    print("  • 'matches <card name>' - Find synergistic partners")
    print("  • 'quit' - Exit")
    print()

    while True:
        try:
            command = input("🔍 Enter command: ").strip()

            if command.lower() == 'quit':
                break
            elif command.startswith('find '):
                search_term = command[5:].strip()
                cards = find_cards_by_name(search_term)
                if cards:
                    print(f"\n📋 Found {len(cards)} cards:")
                    for i, card in enumerate(cards, 1):
                        print(f"  {i}. {card.name}")
                else:
                    print(f"❌ No cards found matching '{search_term}'")

            elif ' | ' in command and command.startswith('synergy '):
                card_names = command[8:].split(' | ')
                if len(card_names) == 2:
                    card1_name, card2_name = [name.strip() for name in card_names]
                    card1 = CardInfo.query.filter(CardInfo.name.ilike(f'%{card1_name}%')).first()
                    card2 = CardInfo.query.filter(CardInfo.name.ilike(f'%{card2_name}%')).first()

                    if card1 and card2:
                        analyze_synergy_between_cards(card1, card2)
                    else:
                        if not card1:
                            print(f"❌ Card not found: {card1_name}")
                        if not card2:
                            print(f"❌ Card not found: {card2_name}")
                else:
                    print("❌ Use format: synergy <card1> | <card2>")

            elif command.startswith('matches '):
                card_name = command[8:].strip()
                card = CardInfo.query.filter(CardInfo.name.ilike(f'%{card_name}%')).first()
                if card:
                    find_synergistic_cards(card)
                else:
                    print(f"❌ Card not found: {card_name}")

            else:
                print("❌ Unknown command. Use 'find', 'synergy', 'matches', or 'quit'.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def demo_examples():
    """Show some demo examples of synergy detection."""
    print("🎯 SYNERGY DETECTION EXAMPLES")
    print("=" * 60)

    # Example searches
    examples = [
        ("goblin", "goblin"),  # Tribal synergy
        ("lightning", "bolt"),  # Similar effects
        ("counterspell", "mana leak"),  # Same archetype
        ("sol ring", "mana crypt"),  # Ramp synergy
    ]

    for search1, search2 in examples:
        card1 = CardInfo.query.filter(CardInfo.name.ilike(f'%{search1}%')).first()
        card2 = CardInfo.query.filter(CardInfo.name.ilike(f'%{search2}%')).first()

        if card1 and card2:
            analyze_synergy_between_cards(card1, card2)
            input("\nPress Enter to continue...")

def main():
    """Main function."""
    app = create_app()

    with app.app_context():
        print("🎯 MTG SYNERGY QUERY TOOL")
        print("=" * 60)
        print("This tool helps you explore synergies between cards in your collection.")
        print()

        # Check how many cards have analysis data
        total_cards = CardInfo.query.count()
        analyzed_cards = CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).count()

        print(f"📊 Collection Status:")
        print(f"  Total cards: {total_cards}")
        print(f"  Analyzed cards: {analyzed_cards}")
        print(f"  Analysis coverage: {(analyzed_cards/total_cards*100):.1f}%")

        if analyzed_cards == 0:
            print("❌ No cards have been analyzed yet!")
            print("Run the synergy analysis first: python scripts/update_collection_synergies.py")
            return

        while True:
            print("\n🎮 Choose an option:")
            print("  1. Interactive synergy explorer")
            print("  2. Demo examples")
            print("  3. Quit")

            choice = input("Enter choice (1-3): ").strip()

            if choice == '1':
                interactive_mode()
            elif choice == '2':
                demo_examples()
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
