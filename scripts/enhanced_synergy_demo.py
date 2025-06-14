#!/usr/bin/env python3
"""
Enhanced MTG Card Synergy Detection Demo

This script demonstrates the comprehensive synergy detection system that analyzes
cards based on multiple dimensions including:
- Tribal synergies (creature types)
- Color synergies and color identity
- Keyword synergies and complementary abilities
- Archetype synergies (aggro, control, combo, etc.)
- Combo potential detection
- Type synergies (artifacts, enchantments, etc.)
- Mana curve compatibility
- Format legality overlap

The enhanced system provides detailed scoring and explanations for each synergy match.
"""
import os
import sys
import json
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.text_analysis import (
    analyze_card_text,
    calculate_synergy_score,
    find_synergy_candidates
)

# Enhanced sample cards with comprehensive data
SAMPLE_CARDS = [
    {
        "name": "Lightning Bolt",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "card_data": {
            "mana_cost": "{R}",
            "cmc": 1.0,
            "type_line": "Instant",
            "colors": ["R"],
            "color_identity": ["R"],
            "keywords": [],
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal",
                "pauper": "legal"
            },
            "rarity": "common"
        }
    },
    {
        "name": "Goblin Guide",
        "oracle_text": "Haste\nWhenever Goblin Guide attacks, defending player reveals the top card of their library. If it's a land card, that player puts it into their hand.",
        "card_data": {
            "mana_cost": "{R}",
            "cmc": 1.0,
            "type_line": "Creature — Goblin Berserker Warrior",
            "colors": ["R"],
            "color_identity": ["R"],
            "keywords": ["Haste"],
            "power": "2",
            "toughness": "2",
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Goblin King",
        "oracle_text": "Other Goblin creatures get +1/+1 and have mountainwalk. (They can't be blocked as long as defending player controls a Mountain.)",
        "card_data": {
            "mana_cost": "{1}{R}{R}",
            "cmc": 3.0,
            "type_line": "Creature — Goblin",
            "colors": ["R"],
            "color_identity": ["R"],
            "keywords": [],
            "power": "2",
            "toughness": "2",
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Llanowar Elves",
        "oracle_text": "{T}: Add {G}.",
        "card_data": {
            "mana_cost": "{G}",
            "cmc": 1.0,
            "type_line": "Creature — Elf Druid",
            "colors": ["G"],
            "color_identity": ["G"],
            "keywords": [],
            "power": "1",
            "toughness": "1",
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal",
                "pauper": "legal"
            },
            "rarity": "common"
        }
    },
    {
        "name": "Elvish Archdruid",
        "oracle_text": "Other Elf creatures you control get +1/+1.\n{T}: Add {G} for each Elf you control.",
        "card_data": {
            "mana_cost": "{1}{G}{G}",
            "cmc": 3.0,
            "type_line": "Creature — Elf Druid",
            "colors": ["G"],
            "color_identity": ["G"],
            "keywords": [],
            "power": "2",
            "toughness": "2",
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Counterspell",
        "oracle_text": "Counter target spell.",
        "card_data": {
            "mana_cost": "{U}{U}",
            "cmc": 2.0,
            "type_line": "Instant",
            "colors": ["U"],
            "color_identity": ["U"],
            "keywords": [],
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal",
                "pauper": "legal"
            },
            "rarity": "common"
        }
    },
    {
        "name": "Snapcaster Mage",
        "oracle_text": "Flash\nWhen Snapcaster Mage enters the battlefield, target instant or sorcery card in your graveyard gains flashback until end of turn. The flashback cost is equal to its mana cost.",
        "card_data": {
            "mana_cost": "{1}{U}",
            "cmc": 2.0,
            "type_line": "Creature — Human Wizard",
            "colors": ["U"],
            "color_identity": ["U"],
            "keywords": ["Flash", "Flashback"],
            "power": "2",
            "toughness": "1",
            "legalities": {
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Grindstone",
        "oracle_text": "{3}, {T}: Target player mills two cards. If two cards that share a color were milled this way, repeat this process.",
        "card_data": {
            "mana_cost": "{1}",
            "cmc": 1.0,
            "type_line": "Artifact",
            "colors": [],
            "color_identity": [],
            "keywords": [],
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Painter's Servant",
        "oracle_text": "As Painter's Servant enters the battlefield, choose a color.\nAll cards that aren't on the battlefield, spells, and permanents are the chosen color in addition to their other colors.",
        "card_data": {
            "mana_cost": "{2}",
            "cmc": 2.0,
            "type_line": "Artifact Creature — Scarecrow",
            "colors": [],
            "color_identity": [],
            "keywords": [],
            "power": "1",
            "toughness": "3",
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Entomb",
        "oracle_text": "Search your library for a card and put that card into your graveyard. Then shuffle your library.",
        "card_data": {
            "mana_cost": "{B}",
            "cmc": 1.0,
            "type_line": "Instant",
            "colors": ["B"],
            "color_identity": ["B"],
            "keywords": [],
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "rare"
        }
    },
    {
        "name": "Reanimate",
        "oracle_text": "Put target creature card from a graveyard onto the battlefield under your control. You lose life equal to its mana value.",
        "card_data": {
            "mana_cost": "{B}",
            "cmc": 1.0,
            "type_line": "Sorcery",
            "colors": ["B"],
            "color_identity": ["B"],
            "keywords": [],
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "uncommon"
        }
    },
    {
        "name": "Griselbrand",
        "oracle_text": "Flying, lifelink\nPay 7 life: Draw seven cards. Activate only once each turn.",
        "card_data": {
            "mana_cost": "{4}{B}{B}{B}{B}",
            "cmc": 8.0,
            "type_line": "Legendary Creature — Demon",
            "colors": ["B"],
            "color_identity": ["B"],
            "keywords": ["Flying", "Lifelink"],
            "power": "7",
            "toughness": "7",
            "legalities": {
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal"
            },
            "rarity": "mythic"
        }
    }
]

def analyze_enhanced_cards() -> List[Dict[str, Any]]:
    """
    Analyze all sample cards with enhanced analysis including card data.
    """
    analyzed_cards = []

    print("🔍 ANALYZING CARDS WITH ENHANCED SYSTEM")
    print("=" * 60)

    for card in SAMPLE_CARDS:
        print(f"\nAnalyzing: {card['name']}")

        analysis = analyze_card_text(card["oracle_text"], card["card_data"])

        analyzed_cards.append({
            "name": card["name"],
            "oracle_text": card["oracle_text"],
            "card_data": card["card_data"],
            "analysis": analysis
        })

        # Show key analysis results
        print(f"  Card Types: {', '.join(analysis.get('card_types', []))}")
        print(f"  Creature Types: {', '.join(analysis.get('creature_types', []))}")
        print(f"  Keywords: {', '.join(analysis.get('keywords', []))}")
        print(f"  Colors: {', '.join(analysis.get('colors', []))}")
        print(f"  Archetypes: {', '.join(analysis.get('synergy_vectors', {}).get('archetype', []))}")

    return analyzed_cards

def demonstrate_synergy_detection(cards: List[Dict[str, Any]]):
    """
    Demonstrate comprehensive synergy detection between cards.
    """
    print("\n\n🤝 COMPREHENSIVE SYNERGY DETECTION")
    print("=" * 60)

    # Focus on some interesting card pairs to demonstrate different types of synergies
    interesting_pairs = [
        ("Goblin Guide", "Goblin King"),       # Tribal synergy
        ("Llanowar Elves", "Elvish Archdruid"), # Tribal synergy
        ("Counterspell", "Snapcaster Mage"),   # Archetype synergy
        ("Grindstone", "Painter's Servant"),   # Combo synergy
        ("Entomb", "Reanimate"),              # Combo synergy
        ("Lightning Bolt", "Goblin Guide"),   # Aggro archetype
    ]

    card_lookup = {card["name"]: card for card in cards}

    for card1_name, card2_name in interesting_pairs:
        if card1_name in card_lookup and card2_name in card_lookup:
            card1 = card_lookup[card1_name]
            card2 = card_lookup[card2_name]

            print(f"\n🔗 SYNERGY: {card1_name} + {card2_name}")
            print("-" * 40)

            synergy = calculate_synergy_score(card1["analysis"], card2["analysis"])

            print(f"Total Synergy Score: {synergy['total_score']:.1f}")
            print("\nScore Breakdown:")
            print(f"  Tribal: {synergy['tribal_score']:.1f}")
            print(f"  Color: {synergy['color_score']:.1f}")
            print(f"  Keywords: {synergy['keyword_score']:.1f}")
            print(f"  Archetype: {synergy['archetype_score']:.1f}")
            print(f"  Combo: {synergy['combo_score']:.1f}")
            print(f"  Type: {synergy['type_score']:.1f}")
            print(f"  Mana Curve: {synergy['mana_curve_score']:.1f}")
            print(f"  Format: {synergy['format_score']:.1f}")

            if synergy['matches']:
                print("\nSynergy Matches:")
                for match in synergy['matches']:
                    print(f"  • {match}")

def demonstrate_collection_synergies(cards: List[Dict[str, Any]]):
    """
    Demonstrate finding synergies for each card against the entire collection.
    """
    print("\n\n📚 COLLECTION-WIDE SYNERGY ANALYSIS")
    print("=" * 60)

    for target_card in cards[:6]:  # Just show first few to keep output manageable
        print(f"\n🎯 Finding synergies for: {target_card['name']}")
        print("-" * 40)

        # Add the card name to the analysis for comparison
        target_analysis = target_card["analysis"].copy()
        target_analysis["name"] = target_card["name"]

        # Prepare collection analyses with names
        collection_analyses = []
        for card in cards:
            card_analysis = card["analysis"].copy()
            card_analysis["name"] = card["name"]
            collection_analyses.append(card_analysis)

        # Find synergies with other cards in collection
        synergies = find_synergy_candidates(target_analysis, collection_analyses, threshold=3.0)

        if synergies:
            print(f"Found {len(synergies)} synergistic cards:")
            for i, synergy in enumerate(synergies[:3], 1):  # Show top 3
                other_card_name = synergy["card"].get('name', 'Unknown')
                score = synergy["score"]
                matches = synergy["synergy"]["matches"]

                print(f"  {i}. {other_card_name} (Score: {score:.1f})")
                if matches:
                    print(f"     Matches: {', '.join(matches[:3])}")  # Show first 3 matches
                else:
                    print(f"     No specific matches found")
        else:
            print("  No significant synergies found.")

def save_analysis_results(cards: List[Dict[str, Any]]):
    """
    Save detailed analysis results to a JSON file for inspection.
    """
    output_file = "enhanced_synergy_analysis.json"

    # Create a clean version for JSON output
    clean_cards = []
    for card in cards:
        clean_card = {
            "name": card["name"],
            "oracle_text": card["oracle_text"],
            "card_data": card["card_data"],
            "analysis": card["analysis"]
        }
        clean_cards.append(clean_card)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_cards, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Detailed analysis saved to: {output_file}")

def main():
    """Run the enhanced synergy detection demo."""
    print("🚀 ENHANCED MTG CARD SYNERGY DETECTION DEMO")
    print("=" * 60)
    print("This demo showcases the comprehensive synergy detection system")
    print("that analyzes multiple dimensions of card interactions.\n")

    try:
        # Analyze all cards with enhanced system
        analyzed_cards = analyze_enhanced_cards()

        # Demonstrate detailed synergy detection
        demonstrate_synergy_detection(analyzed_cards)

        # Demonstrate collection-wide synergy finding
        demonstrate_collection_synergies(analyzed_cards)

        # Save results for detailed inspection
        save_analysis_results(analyzed_cards)

        print("\n\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("The enhanced synergy system successfully demonstrated:")
        print("• Comprehensive card data extraction")
        print("• Multi-dimensional synergy scoring")
        print("• Tribal, color, keyword, and archetype synergies")
        print("• Combo potential detection")
        print("• Collection-wide synergy analysis")
        print("\nCheck the saved JSON file for detailed analysis data!")

    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
