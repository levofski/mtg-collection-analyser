#!/usr/bin/env python3
"""
Synergy Graph Management Tool

This script provides a comprehensive interface for managing the synergy graph:
- Check current status
- Compute missing synergies
- Update existing synergies
- Query and analyze the graph
"""
import os
import sys
import time
from typing import Dict, Any, List
from itertools import combinations

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.models.card_synergy import CardSynergy
from src.services.text_analysis import calculate_synergy_score
from src.database import db
from main import create_app

class SynergyGraphManager:
    """Manages the synergy graph computation and queries."""

    def __init__(self, app=None):
        self.app = app or create_app()

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the synergy graph."""
        with self.app.app_context():
            total_cards = CardInfo.query.count()
            analyzed_cards = CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).count()
            total_synergies = CardSynergy.query.count()

            # Calculate expected synergies for analyzed cards
            expected_synergies = (analyzed_cards * (analyzed_cards - 1)) // 2 if analyzed_cards > 1 else 0
            completion_rate = (total_synergies / expected_synergies * 100) if expected_synergies > 0 else 0

            # Get score distribution
            high_synergy = CardSynergy.query.filter(CardSynergy.total_score >= 30).count()
            good_synergy = CardSynergy.query.filter(
                CardSynergy.total_score >= 15,
                CardSynergy.total_score < 30
            ).count()
            moderate_synergy = CardSynergy.query.filter(
                CardSynergy.total_score >= 5,
                CardSynergy.total_score < 15
            ).count()

            # Get top synergy
            top_synergy = CardSynergy.query.order_by(CardSynergy.total_score.desc()).first()

            return {
                "total_cards": total_cards,
                "analyzed_cards": analyzed_cards,
                "total_synergies": total_synergies,
                "expected_synergies": expected_synergies,
                "completion_rate": completion_rate,
                "score_distribution": {
                    "high_30_plus": high_synergy,
                    "good_15_to_30": good_synergy,
                    "moderate_5_to_15": moderate_synergy
                },
                "top_synergy": {
                    "score": top_synergy.total_score,
                    "cards": f"{top_synergy.card1.name} + {top_synergy.card2.name}"
                } if top_synergy else None
            }

    def compute_missing_synergies(self, batch_size: int = 1000, min_score: float = 1.0) -> Dict[str, int]:
        """Compute only missing synergies."""
        with self.app.app_context():
            analyzed_cards = CardInfo.query.filter(CardInfo._extracted_data.isnot(None)).all()

            if len(analyzed_cards) < 2:
                return {"error": "Need at least 2 analyzed cards"}

            print(f"🔍 Checking for missing synergies among {len(analyzed_cards)} cards...")

            stats = {
                "checked": 0,
                "missing": 0,
                "computed": 0,
                "stored": 0,
                "skipped_low_score": 0,
                "errors": 0
            }

            synergy_batch = []
            start_time = time.time()

            for card1, card2 in combinations(analyzed_cards, 2):
                stats["checked"] += 1

                # Check if synergy already exists
                existing = CardSynergy.get_synergy(card1.id, card2.id)
                if existing:
                    continue

                stats["missing"] += 1

                try:
                    # Calculate synergy
                    synergy_result = calculate_synergy_score(
                        card1.extracted_data or {},
                        card2.extracted_data or {}
                    )

                    stats["computed"] += 1
                    total_score = synergy_result.get('total_score', 0)

                    # Only store if score meets minimum threshold
                    if total_score >= min_score:
                        synergy = CardSynergy.create_from_analysis(
                            card1.id, card2.id, synergy_result
                        )
                        synergy_batch.append(synergy)
                        stats["stored"] += 1
                    else:
                        stats["skipped_low_score"] += 1

                    # Commit batch
                    if len(synergy_batch) >= batch_size:
                        db.session.add_all(synergy_batch)
                        db.session.commit()
                        synergy_batch = []

                        # Progress update
                        elapsed = time.time() - start_time
                        rate = stats["computed"] / elapsed if elapsed > 0 else 0

                        print(f"📈 Checked: {stats['checked']:,} | "
                              f"Missing: {stats['missing']:,} | "
                              f"Computed: {stats['computed']:,} | "
                              f"Stored: {stats['stored']:,} | "
                              f"Rate: {rate:.1f}/sec")

                except Exception as e:
                    print(f"❌ Error: {card1.name} + {card2.name}: {str(e)}")
                    stats["errors"] += 1
                    continue

            # Commit remaining batch
            if synergy_batch:
                db.session.add_all(synergy_batch)
                db.session.commit()

            return stats

    def find_best_synergies(self, card_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find best synergies for a card by name."""
        with self.app.app_context():
            card = CardInfo.query.filter(CardInfo.name.ilike(f"%{card_name}%")).first()

            if not card:
                return []

            synergies = CardSynergy.get_synergies_for_card(card.id, min_score=0, limit=limit)

            results = []
            for synergy in synergies:
                partner = synergy.get_partner_card(card.id)
                if partner:
                    results.append({
                        "partner_name": partner.name,
                        "partner_type": partner.type_line,
                        "total_score": synergy.total_score,
                        "tribal_score": synergy.tribal_score,
                        "combo_score": synergy.combo_score,
                        "archetype_score": synergy.archetype_score
                    })

            return results

    def find_deck_cores(self, min_synergy: float = 20.0, min_cards: int = 3) -> List[Dict[str, Any]]:
        """Find groups of cards that form strong synergistic cores."""
        with self.app.app_context():
            # Get high-synergy pairs
            high_synergies = CardSynergy.query.filter(
                CardSynergy.total_score >= min_synergy
            ).all()

            # Build card connections
            card_connections = {}
            for synergy in high_synergies:
                card1_id = synergy.card1_id
                card2_id = synergy.card2_id

                if card1_id not in card_connections:
                    card_connections[card1_id] = set()
                if card2_id not in card_connections:
                    card_connections[card2_id] = set()

                card_connections[card1_id].add(card2_id)
                card_connections[card2_id].add(card1_id)

            # Find connected components (deck cores)
            visited = set()
            cores = []

            def dfs(card_id, component):
                if card_id in visited:
                    return
                visited.add(card_id)
                component.add(card_id)

                for connected_card in card_connections.get(card_id, set()):
                    dfs(connected_card, component)

            for card_id in card_connections:
                if card_id not in visited:
                    component = set()
                    dfs(card_id, component)

                    if len(component) >= min_cards:
                        # Get card names and calculate average synergy
                        card_names = []
                        total_synergy = 0
                        synergy_count = 0

                        for cid in component:
                            card = CardInfo.query.get(cid)
                            if card:
                                card_names.append(card.name)

                        for c1 in component:
                            for c2 in component:
                                if c1 < c2:  # Avoid duplicates
                                    synergy = CardSynergy.get_synergy(c1, c2)
                                    if synergy:
                                        total_synergy += synergy.total_score
                                        synergy_count += 1

                        avg_synergy = total_synergy / synergy_count if synergy_count > 0 else 0

                        cores.append({
                            "cards": card_names,
                            "card_count": len(component),
                            "average_synergy": avg_synergy,
                            "total_connections": synergy_count
                        })

            # Sort by average synergy
            cores.sort(key=lambda x: x["average_synergy"], reverse=True)
            return cores

def main():
    """Interactive synergy graph management."""
    manager = SynergyGraphManager()

    print("🚀 MTG SYNERGY GRAPH MANAGER")
    print("=" * 50)

    while True:
        print("\nChoose an option:")
        print("1. Check synergy graph status")
        print("2. Compute missing synergies")
        print("3. Find synergies for a card")
        print("4. Find deck cores")
        print("5. Show top synergies")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            status = manager.get_status()
            print(f"\n📊 SYNERGY GRAPH STATUS:")
            print(f"   Total cards: {status['total_cards']:,}")
            print(f"   Analyzed cards: {status['analyzed_cards']:,}")
            print(f"   Stored synergies: {status['total_synergies']:,}")
            print(f"   Expected synergies: {status['expected_synergies']:,}")
            print(f"   Completion: {status['completion_rate']:.1f}%")
            print(f"\n📈 Score Distribution:")
            print(f"   High (30+): {status['score_distribution']['high_30_plus']:,}")
            print(f"   Good (15-30): {status['score_distribution']['good_15_to_30']:,}")
            print(f"   Moderate (5-15): {status['score_distribution']['moderate_5_to_15']:,}")

            if status['top_synergy']:
                print(f"\n🔥 Top synergy: {status['top_synergy']['score']:.1f}")
                print(f"   {status['top_synergy']['cards']}")

        elif choice == "2":
            print("\n🔄 Computing missing synergies...")
            min_score = float(input("Minimum score to store (default 1.0): ") or "1.0")

            stats = manager.compute_missing_synergies(min_score=min_score)

            if "error" in stats:
                print(f"❌ {stats['error']}")
            else:
                print(f"\n✅ COMPUTATION COMPLETE:")
                print(f"   Pairs checked: {stats['checked']:,}")
                print(f"   Missing synergies: {stats['missing']:,}")
                print(f"   Computed: {stats['computed']:,}")
                print(f"   Stored: {stats['stored']:,}")
                print(f"   Skipped (low score): {stats['skipped_low_score']:,}")
                print(f"   Errors: {stats['errors']:,}")

        elif choice == "3":
            card_name = input("\nEnter card name (partial matches OK): ").strip()
            if card_name:
                synergies = manager.find_best_synergies(card_name)

                if synergies:
                    print(f"\n🔗 Best synergies for '{card_name}':")
                    for i, s in enumerate(synergies, 1):
                        print(f"{i:2d}. {s['partner_name']} ({s['partner_type']})")
                        print(f"     Score: {s['total_score']:.1f} "
                              f"(Tribal: {s['tribal_score']:.1f}, "
                              f"Combo: {s['combo_score']:.1f}, "
                              f"Archetype: {s['archetype_score']:.1f})")
                else:
                    print(f"❌ No card found matching '{card_name}' or no synergies computed")

        elif choice == "4":
            min_synergy = float(input("Minimum synergy score for cores (default 20.0): ") or "20.0")
            min_cards = int(input("Minimum cards per core (default 3): ") or "3")

            cores = manager.find_deck_cores(min_synergy=min_synergy, min_cards=min_cards)

            if cores:
                print(f"\n🏗️  DECK CORES FOUND:")
                for i, core in enumerate(cores[:10], 1):  # Show top 10
                    print(f"{i:2d}. {core['card_count']} cards, "
                          f"avg synergy: {core['average_synergy']:.1f}")
                    print(f"     Cards: {', '.join(core['cards'])}")
            else:
                print(f"❌ No deck cores found with those criteria")

        elif choice == "5":
            with manager.app.app_context():
                top_synergies = CardSynergy.get_top_synergies(limit=10)

                if top_synergies:
                    print(f"\n🔥 TOP SYNERGIES:")
                    for i, synergy in enumerate(top_synergies, 1):
                        print(f"{i:2d}. {synergy.card1.name} + {synergy.card2.name}")
                        print(f"     Score: {synergy.total_score:.1f}")
                else:
                    print("❌ No synergies found")

        elif choice == "6":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice, please try again")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
