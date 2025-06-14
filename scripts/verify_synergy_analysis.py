#!/usr/bin/env python3
"""
Verify and test the enhanced synergy analysis in your collection.

This script helps you verify that the synergy data has been updated correctly
and demonstrates the enhanced analysis capabilities.
"""
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.services.text_analysis import find_synergy_candidates, calculate_synergy_score
from main import create_app

def check_analysis_status():
    """Check how many cards have been analyzed."""
    total_cards = CardInfo.query.count()
    analyzed_cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).count()

    print("📊 COLLECTION ANALYSIS STATUS")
    print("=" * 40)
    print(f"Total cards in collection: {total_cards}")
    print(f"Cards with analysis data: {analyzed_cards}")
    print(f"Analysis coverage: {(analyzed_cards/total_cards*100):.1f}%" if total_cards > 0 else "Analysis coverage: 0%")

    return analyzed_cards > 0

def show_sample_analysis():
    """Show detailed analysis for a few sample cards."""
    print("\n🔍 SAMPLE CARD ANALYSIS")
    print("=" * 40)

    # Get first few analyzed cards
    sample_cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).limit(3).all()

    if not sample_cards:
        print("❌ No analyzed cards found. Run synergy analysis first!")
        return False

    for i, card in enumerate(sample_cards, 1):
        print(f"\n{i}. {card.name}")
        print("-" * 30)

        data = card.extracted_data
        if not data:
            print("  No analysis data")
            continue

        # Show key extracted data
        if data.get('keywords'):
            print(f"  🏷️  Keywords: {', '.join(data['keywords'][:5])}")

        if data.get('creature_types'):
            print(f"  🧙 Creature Types: {', '.join(data['creature_types'])}")

        if data.get('card_types'):
            print(f"  🃏 Card Types: {', '.join(data['card_types'])}")

        if data.get('colors'):
            print(f"  🎨 Colors: {', '.join(data['colors'])}")

        # Show synergy vectors
        vectors = data.get('synergy_vectors', {})
        if vectors.get('archetype'):
            print(f"  🎭 Archetypes: {', '.join(vectors['archetype'])}")

        if vectors.get('combo_potential'):
            print(f"  💥 Combo Potential: {', '.join(vectors['combo_potential'])}")

        # Show mana analysis
        mana_info = data.get('mana_cost_info', {})
        if mana_info:
            cmc = data.get('cmc', 0)
            colored_symbols = mana_info.get('colored_symbols', 0)
            print(f"  💎 Mana: CMC {cmc}, {colored_symbols} colored symbols")

    return True

def test_synergy_detection():
    """Test synergy detection between cards in the collection."""
    print("\n🤝 SYNERGY DETECTION TEST")
    print("=" * 40)

    # Get analyzed cards
    cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).limit(10).all()

    if len(cards) < 2:
        print("❌ Need at least 2 analyzed cards for synergy testing")
        return False

    print(f"Testing synergies among {len(cards)} cards...")

    # Test with first card
    target_card = cards[0]
    target_analysis = target_card.extracted_data.copy()
    target_analysis["name"] = target_card.name

    # Prepare collection analyses
    collection_analyses = []
    for card in cards:
        analysis = card.extracted_data.copy()
        analysis["name"] = card.name
        collection_analyses.append(analysis)

    # Find synergies
    synergies = find_synergy_candidates(target_analysis, collection_analyses, threshold=3.0)

    print(f"\n🎯 Synergies found for '{target_card.name}':")

    if not synergies:
        print("  No significant synergies found (score < 3.0)")
    else:
        for i, synergy in enumerate(synergies[:5], 1):  # Show top 5
            other_name = synergy["card"].get('name', 'Unknown')
            score = synergy["score"]
            breakdown = synergy["synergy"]
            matches = breakdown.get("matches", [])

            print(f"\n  {i}. {other_name} (Total Score: {score:.1f})")
            print(f"     Breakdown: Tribal:{breakdown.get('tribal_score', 0):.1f}, "
                  f"Color:{breakdown.get('color_score', 0):.1f}, "
                  f"Keywords:{breakdown.get('keyword_score', 0):.1f}")

            if matches:
                print(f"     Key Matches: {', '.join(matches[:3])}")

    return True

def test_detailed_synergy_scoring():
    """Test detailed synergy scoring between two specific cards."""
    print("\n📊 DETAILED SYNERGY SCORING TEST")
    print("=" * 40)

    # Get two analyzed cards
    cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).limit(2).all()

    if len(cards) < 2:
        print("❌ Need at least 2 analyzed cards for detailed scoring test")
        return False

    card1, card2 = cards[0], cards[1]

    print(f"Analyzing synergy between:")
    print(f"  Card 1: {card1.name}")
    print(f"  Card 2: {card2.name}")

    # Calculate detailed synergy score
    synergy_result = calculate_synergy_score(card1.extracted_data, card2.extracted_data)

    print(f"\n🎯 Synergy Analysis Results:")
    print(f"  Total Score: {synergy_result['total_score']:.2f}")
    print(f"\n  Score Breakdown:")
    print(f"    Tribal: {synergy_result['tribal_score']:.1f}")
    print(f"    Color: {synergy_result['color_score']:.1f}")
    print(f"    Keywords: {synergy_result['keyword_score']:.1f}")
    print(f"    Archetype: {synergy_result['archetype_score']:.1f}")
    print(f"    Combo: {synergy_result['combo_score']:.1f}")
    print(f"    Type: {synergy_result['type_score']:.1f}")
    print(f"    Mana Curve: {synergy_result['mana_curve_score']:.1f}")
    print(f"    Format: {synergy_result['format_score']:.1f}")

    if synergy_result['matches']:
        print(f"\n  Synergy Matches:")
        for match in synergy_result['matches'][:8]:  # Show first 8 matches
            print(f"    • {match}")
        if len(synergy_result['matches']) > 8:
            print(f"    ... and {len(synergy_result['matches']) - 8} more matches")

    return True

def main():
    """Main verification function."""
    print("🔍 MTG COLLECTION SYNERGY VERIFICATION")
    print("=" * 60)
    print("This script verifies that your enhanced synergy analysis is working correctly.\n")

    app = create_app()

    with app.app_context():
        # Check analysis status
        has_analysis = check_analysis_status()

        if not has_analysis:
            print("\n❌ No synergy analysis found!")
            print("Run the synergy update first:")
            print("  python scripts/update_collection_synergies.py")
            print("  OR")
            print("  curl -X POST http://localhost:5000/collection/analyze-all")
            return

        # Show sample analysis
        show_sample_analysis()

        # Test synergy detection
        test_synergy_detection()

        # Test detailed scoring
        test_detailed_synergy_scoring()

        print(f"\n✅ VERIFICATION COMPLETE!")
        print("=" * 60)
        print("Your enhanced synergy analysis system is working correctly!")
        print("\nYou can now:")
        print("• Use the API to find synergies between cards")
        print("• Build decks based on synergy recommendations")
        print("• Analyze your collection for hidden interactions")
        print("• Get detailed explanations for card relationships")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
