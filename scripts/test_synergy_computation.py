#!/usr/bin/env python3
"""
Test script to compute synergies for a small sample of cards.

This helps verify the system works before running on the full collection.
"""
import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.models.card_synergy import CardSynergy
from src.services.text_analysis import calculate_synergy_score
from src.database import db
from main import create_app

def test_synergy_computation(limit: int = 50):
    """Test synergy computation with a small sample."""
    print(f"🧪 TESTING SYNERGY COMPUTATION")
    print("=" * 60)
    print(f"Testing with first {limit} analyzed cards...")

    app = create_app()

    with app.app_context():
        # Get a small sample of cards
        cards = CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).limit(limit).all()

        if len(cards) < 2:
            print("❌ Need at least 2 analyzed cards!")
            return

        print(f"📋 Testing with {len(cards)} cards")
        total_pairs = (len(cards) * (len(cards) - 1)) // 2
        print(f"🔢 Will compute {total_pairs} synergy pairs")

        stored_count = 0
        start_time = time.time()

        # Compute synergies for all pairs
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                card1, card2 = cards[i], cards[j]

                # Check if already exists
                existing = CardSynergy.get_synergy(card1.id, card2.id)
                if existing:
                    print(f"⏭️  Skipping existing: {card1.name} + {card2.name}")
                    continue

                # Calculate synergy
                synergy_result = calculate_synergy_score(
                    card1.extracted_data or {},
                    card2.extracted_data or {}
                )

                total_score = synergy_result.get('total_score', 0)

                # Store if meaningful synergy (score >= 1.0)
                if total_score >= 1.0:
                    synergy = CardSynergy.create_from_analysis(
                        card1.id, card2.id, synergy_result
                    )
                    db.session.add(synergy)
                    stored_count += 1

                    print(f"✅ {card1.name} + {card2.name}: {total_score:.1f}")
                else:
                    print(f"⚪ {card1.name} + {card2.name}: {total_score:.1f} (not stored)")

        # Commit all changes
        db.session.commit()

        elapsed = time.time() - start_time
        print(f"\n✅ Test completed!")
        print(f"⏱️  Time: {elapsed:.1f} seconds")
        print(f"💾 Stored: {stored_count} synergies")
        print(f"📊 Rate: {total_pairs / elapsed:.1f} pairs/sec")

        # Show some examples
        if stored_count > 0:
            print(f"\n🔥 Top synergies found:")
            top_synergies = CardSynergy.query.order_by(CardSynergy.total_score.desc()).limit(5).all()
            for i, synergy in enumerate(top_synergies, 1):
                print(f"  {i}. {synergy.card1.name} + {synergy.card2.name}: {synergy.total_score:.1f}")

if __name__ == "__main__":
    test_synergy_computation()
