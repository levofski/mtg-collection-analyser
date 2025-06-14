#!/usr/bin/env python3
"""
Compute and store synergy scores for all card pairs in the collection.

This script calculates synergy scores between every combination of cards
and stores them in the database for fast querying later.
"""
import os
import sys
import time
from itertools import combinations
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.models.card_synergy import CardSynergy
from src.services.text_analysis import calculate_synergy_score
from src.database import db
from main import create_app

def get_analyzed_cards() -> List[CardInfo]:
    """Get all cards that have been analyzed."""
    return CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).all()

def compute_synergies_batch(cards: List[CardInfo], batch_size: int = 1000,
                           min_score: float = 1.0) -> Dict[str, int]:
    """
    Compute synergies for all card pairs in batches.

    Args:
        cards: List of analyzed cards
        batch_size: Number of synergies to compute before committing to database
        min_score: Minimum synergy score to store (saves space)

    Returns:
        Dictionary with computation statistics
    """
    total_cards = len(cards)
    total_pairs = (total_cards * (total_cards - 1)) // 2

    print(f"🔄 Computing synergies for {total_cards} cards ({total_pairs:,} pairs)")
    print(f"⚙️  Batch size: {batch_size}, Min score: {min_score}")
    print(f"💾 Only storing synergies with score >= {min_score}")
    print("-" * 60)

    stats = {
        "processed": 0,
        "stored": 0,
        "skipped_low_score": 0,
        "errors": 0,
        "batches": 0
    }

    synergy_batch = []
    start_time = time.time()

    # Generate all unique pairs
    for i, (card1, card2) in enumerate(combinations(cards, 2)):
        try:
            # Check if synergy already exists
            existing = CardSynergy.get_synergy(card1.id, card2.id)
            if existing:
                stats["processed"] += 1
                continue

            # Calculate synergy
            synergy_result = calculate_synergy_score(
                card1.extracted_data or {},
                card2.extracted_data or {}
            )

            total_score = synergy_result.get('total_score', 0)
            stats["processed"] += 1

            # Only store if score meets minimum threshold
            if total_score >= min_score:
                synergy = CardSynergy.create_from_analysis(
                    card1.id, card2.id, synergy_result
                )
                synergy_batch.append(synergy)
                stats["stored"] += 1
            else:
                stats["skipped_low_score"] += 1

            # Commit batch when it reaches batch_size
            if len(synergy_batch) >= batch_size:
                db.session.add_all(synergy_batch)
                db.session.commit()
                stats["batches"] += 1
                synergy_batch = []

                # Progress update
                elapsed = time.time() - start_time
                rate = stats["processed"] / elapsed if elapsed > 0 else 0
                eta = (total_pairs - stats["processed"]) / rate if rate > 0 else 0

                print(f"📈 Progress: {stats['processed']:,}/{total_pairs:,} pairs "
                      f"({stats['processed']/total_pairs*100:.1f}%) - "
                      f"Stored: {stats['stored']:,} - "
                      f"Rate: {rate:.1f} pairs/sec - "
                      f"ETA: {eta/60:.1f}m")

        except Exception as e:
            print(f"❌ Error processing {card1.name} + {card2.name}: {str(e)}")
            stats["errors"] += 1
            continue

    # Commit remaining batch
    if synergy_batch:
        db.session.add_all(synergy_batch)
        db.session.commit()
        stats["batches"] += 1

    return stats

def show_computation_summary(stats: Dict[str, int], elapsed_time: float):
    """Show summary of computation results."""
    print("\n✅ SYNERGY COMPUTATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Results:")
    print(f"  Total pairs processed: {stats['processed']:,}")
    print(f"  Synergies stored: {stats['stored']:,}")
    print(f"  Low-score pairs skipped: {stats['skipped_low_score']:,}")
    print(f"  Errors encountered: {stats['errors']:,}")
    print(f"  Database batches: {stats['batches']:,}")
    print(f"  Total time: {elapsed_time/60:.1f} minutes")
    print(f"  Processing rate: {stats['processed']/elapsed_time:.1f} pairs/sec")

    if stats['stored'] > 0:
        storage_rate = stats['stored'] / stats['processed'] * 100
        print(f"  Storage rate: {storage_rate:.1f}% of pairs had meaningful synergy")

def show_top_synergies(limit: int = 10):
    """Show top synergies found."""
    print(f"\n🔥 TOP {limit} SYNERGIES DISCOVERED:")
    print("-" * 60)

    top_synergies = CardSynergy.get_top_synergies(limit=limit, min_score=0)

    for i, synergy in enumerate(top_synergies, 1):
        card1_name = synergy.card1.name if synergy.card1 else f"ID:{synergy.card1_id}"
        card2_name = synergy.card2.name if synergy.card2 else f"ID:{synergy.card2_id}"

        print(f"{i:2d}. {card1_name} + {card2_name}")
        print(f"     Score: {synergy.total_score:.1f} "
              f"(Tribal: {synergy.tribal_score:.1f}, "
              f"Archetype: {synergy.archetype_score:.1f}, "
              f"Combo: {synergy.combo_score:.1f})")

def show_synergy_analytics():
    """Show analytics about the computed synergies."""
    print(f"\n📈 SYNERGY ANALYTICS:")
    print("-" * 60)

    total_synergies = CardSynergy.query.count()
    print(f"💾 Total synergies stored: {total_synergies:,}")

    if total_synergies == 0:
        return

    # Score distribution
    high_synergy = CardSynergy.query.filter(CardSynergy.total_score >= 30).count()
    good_synergy = CardSynergy.query.filter(
        CardSynergy.total_score >= 15,
        CardSynergy.total_score < 30
    ).count()
    moderate_synergy = CardSynergy.query.filter(
        CardSynergy.total_score >= 5,
        CardSynergy.total_score < 15
    ).count()

    print(f"🔥 High synergy (30+): {high_synergy:,}")
    print(f"✨ Good synergy (15-30): {good_synergy:,}")
    print(f"👍 Moderate synergy (5-15): {moderate_synergy:,}")

    # Top synergy types
    top_tribal = CardSynergy.query.filter(CardSynergy.tribal_score >= 10).count()
    top_combo = CardSynergy.query.filter(CardSynergy.combo_score >= 10).count()
    top_archetype = CardSynergy.query.filter(CardSynergy.archetype_score >= 10).count()

    print(f"🏷️  Strong tribal synergies: {top_tribal:,}")
    print(f"💥 Strong combo synergies: {top_combo:,}")
    print(f"🎭 Strong archetype synergies: {top_archetype:,}")

def main():
    """Main function."""
    print("🚀 MTG COLLECTION SYNERGY COMPUTATION")
    print("=" * 60)
    print("This will compute synergy scores between ALL card pairs in your collection.")
    print("This may take a while for large collections but only needs to be done once.")
    print()

    app = create_app()

    with app.app_context():
        # Get all analyzed cards
        cards = get_analyzed_cards()

        if len(cards) < 2:
            print("❌ Need at least 2 analyzed cards to compute synergies!")
            print("Run the analysis first: python scripts/update_collection_synergies.py")
            return

        total_pairs = (len(cards) * (len(cards) - 1)) // 2
        estimated_time = total_pairs / 100 / 60  # Rough estimate at 100 pairs/sec

        print(f"📋 Found {len(cards)} analyzed cards")
        print(f"🔢 Will compute {total_pairs:,} synergy pairs")
        print(f"⏱️  Estimated time: {estimated_time:.1f} minutes")
        print()

        # Ask for confirmation for large collections
        if total_pairs > 100000:
            response = input(f"⚠️  This is a large collection ({total_pairs:,} pairs). Continue? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return

        # Optional: Set minimum score threshold
        min_score_input = input("Minimum synergy score to store (default 1.0, 0 for all): ").strip()
        try:
            min_score = float(min_score_input) if min_score_input else 1.0
        except ValueError:
            min_score = 1.0

        print(f"\n🎯 Starting computation with min_score = {min_score}")
        start_time = time.time()

        # Compute all synergies
        stats = compute_synergies_batch(cards, min_score=min_score)

        elapsed_time = time.time() - start_time

        # Show results
        show_computation_summary(stats, elapsed_time)
        show_synergy_analytics()
        show_top_synergies()

        print(f"\n🎉 Synergy computation complete!")
        print(f"Your collection now has a complete synergy graph for deck building!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Computation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during computation: {str(e)}")
        import traceback
        traceback.print_exc()
