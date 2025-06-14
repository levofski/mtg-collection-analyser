#!/usr/bin/env python3
"""
Update synergy data for the entire MTG collection.

This script updates all cards in your collection with enhanced synergy analysis,
including tribal synergies, archetype detection, combo potential, and more.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.card_analysis import analyze_all_cards
from src.models.card_info import CardInfo
from src.database import db
from main import create_app

def show_collection_stats():
    """Show current collection analysis statistics."""
    total_cards = CardInfo.query.count()
    analyzed_cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).count()

    print(f"📊 Collection Statistics:")
    print(f"  Total cards: {total_cards}")
    print(f"  Already analyzed: {analyzed_cards}")
    print(f"  Need analysis: {total_cards - analyzed_cards}")

    return total_cards, analyzed_cards

def update_collection_synergy_data():
    """Update synergy data for all cards in the collection."""
    print("🚀 MTG COLLECTION SYNERGY DATA UPDATER")
    print("=" * 60)
    print("This will update your entire collection with enhanced synergy analysis.")
    print("Features included:")
    print("  • 200+ creature types for tribal synergies")
    print("  • 100+ keywords and abilities")
    print("  • Archetype detection (aggro, control, combo, etc.)")
    print("  • Combo potential identification")
    print("  • Color and format compatibility")
    print("  • Mana curve analysis")
    print("  • Multi-dimensional synergy vectors")
    print()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Show current stats
        total_cards, analyzed_cards = show_collection_stats()

        if total_cards == 0:
            print("❌ No cards found in collection. Import some cards first!")
            return

        if analyzed_cards == total_cards:
            print("✅ All cards are already analyzed!")
            response = input("Do you want to re-analyze all cards? (y/N): ")
            if response.lower() != 'y':
                print("Exiting without changes.")
                return

        print(f"\n🔍 Starting enhanced analysis of {total_cards} cards...")
        print("This may take a moment for large collections...")
        print("-" * 60)

        # Analyze all cards with enhanced system
        successful, total, errors = analyze_all_cards()

        print(f"\n✅ ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📈 Results:")
        print(f"  Successfully analyzed: {successful}/{total} cards")
        print(f"  Success rate: {(successful/total*100):.1f}%" if total > 0 else "  Success rate: 0%")

        if errors:
            print(f"\n❌ Errors encountered ({len(errors)} cards):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  • {error['card_name']}: {error['error'][:80]}...")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
            print(f"\nTip: Errors are often due to missing oracle text. Try enriching")
            print(f"     your collection with Scryfall data first.")

        if successful > 0:
            print(f"\n🎯 Your collection now has enhanced synergy data!")
            print("  You can now:")
            print("  • Find tribal synergies between creatures")
            print("  • Discover combo potential in your cards")
            print("  • Identify archetype-based relationships")
            print("  • Get weighted synergy scores with explanations")
            print("  • Analyze collection-wide synergy patterns")

            # Show a quick example if we have analyzed cards
            try:
                sample_card = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).first()
                if sample_card and sample_card.extracted_data:
                    data = sample_card.extracted_data
                    print(f"\n📋 Example analysis for '{sample_card.name}':")
                    if data.get('creature_types'):
                        print(f"  🏷️  Creature Types: {', '.join(data.get('creature_types', [])[:3])}")
                    if data.get('keywords'):
                        print(f"  ⚡ Keywords: {', '.join(data.get('keywords', [])[:3])}")
                    archetypes = data.get('synergy_vectors', {}).get('archetype', [])
                    if archetypes:
                        print(f"  🎭 Archetypes: {', '.join(archetypes[:3])}")
                    combo_potential = data.get('synergy_vectors', {}).get('combo_potential', [])
                    if combo_potential:
                        print(f"  💥 Combo Potential: {', '.join(combo_potential[:3])}")
            except Exception:
                pass  # Skip example if there's any issue

def main():
    """Main function."""
    try:
        update_collection_synergy_data()
    except KeyboardInterrupt:
        print("\n\n⏹️  Update cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during update: {str(e)}")
        print("Please check your database connection and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
