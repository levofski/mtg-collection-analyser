#!/usr/bin/env python3
"""
Query and analyze stored synergy data to find deck building strategies.

This script provides tools to explore the synergy graph and discover
optimal card combinations for different strategies.
"""
import os
import sys
from typing import List, Dict, Any, Set
from collections import defaultdict, Counter

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.models.card_synergy import CardSynergy
from src.database import db
from main import create_app

def find_synergy_clusters(min_score: float = 15.0, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
    """
    Find clusters of cards that all synergize well with each other.

    Args:
        min_score: Minimum synergy score between cards in cluster
        min_cluster_size: Minimum number of cards in a cluster

    Returns:
        List of synergy clusters
    """
    print(f"🔍 Finding synergy clusters (min_score: {min_score}, min_size: {min_cluster_size})")

    # Get all high-synergy pairs
    high_synergies = CardSynergy.query.filter(CardSynergy.total_score >= min_score).all()

    # Build adjacency list
    adjacency = defaultdict(set)
    for synergy in high_synergies:
        adjacency[synergy.card1_id].add(synergy.card2_id)
        adjacency[synergy.card2_id].add(synergy.card1_id)

    print(f"📊 Found {len(high_synergies)} high-synergy pairs")
    print(f"📊 {len(adjacency)} cards participate in high synergies")

    # Find clusters using simple connected components
    visited = set()
    clusters = []

    def dfs_cluster(card_id: int, current_cluster: Set[int]):
        """Depth-first search to find connected cluster."""
        if card_id in visited:
            return
        visited.add(card_id)
        current_cluster.add(card_id)

        # Only include cards that are connected to ALL other cards in cluster
        # (ensuring it's a complete subgraph)
        for neighbor in adjacency[card_id]:
            if neighbor not in visited:
                # Check if neighbor is connected to all cards in current cluster
                if all(neighbor in adjacency[cluster_card] or neighbor == cluster_card
                       for cluster_card in current_cluster):
                    dfs_cluster(neighbor, current_cluster)

    # Find clusters
    for card_id in adjacency:
        if card_id not in visited:
            cluster = set()
            dfs_cluster(card_id, cluster)
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)

    # Convert to detailed cluster information
    detailed_clusters = []
    for i, cluster_card_ids in enumerate(clusters):
        cluster_cards = CardInfo.query.filter(CardInfo.id.in_(cluster_card_ids)).all()

        # Calculate average synergy within cluster
        total_synergy = 0
        synergy_count = 0
        for card1_id in cluster_card_ids:
            for card2_id in cluster_card_ids:
                if card1_id < card2_id:  # Avoid double counting
                    synergy = CardSynergy.get_synergy(card1_id, card2_id)
                    if synergy:
                        total_synergy += synergy.total_score
                        synergy_count += 1

        avg_synergy = total_synergy / synergy_count if synergy_count > 0 else 0

        detailed_clusters.append({
            "id": i + 1,
            "cards": cluster_cards,
            "size": len(cluster_cards),
            "average_synergy": avg_synergy,
            "card_names": [card.name for card in cluster_cards]
        })

    # Sort by average synergy score
    detailed_clusters.sort(key=lambda x: x["average_synergy"], reverse=True)

    return detailed_clusters

def find_deck_cores(archetype: str = None, min_score: float = 20.0) -> List[Dict[str, Any]]:
    """
    Find potential deck cores based on synergy patterns.

    Args:
        archetype: Specific archetype to focus on (e.g., 'tribal', 'combo')
        min_score: Minimum synergy score for core cards

    Returns:
        List of potential deck cores
    """
    print(f"🎯 Finding deck cores (archetype: {archetype or 'any'}, min_score: {min_score})")

    # Filter synergies by archetype if specified
    query = CardSynergy.query.filter(CardSynergy.total_score >= min_score)

    if archetype == 'tribal':
        query = query.filter(CardSynergy.tribal_score >= 10)
    elif archetype == 'combo':
        query = query.filter(CardSynergy.combo_score >= 10)
    elif archetype == 'control':
        query = query.filter(CardSynergy.archetype_score >= 8)

    synergies = query.order_by(CardSynergy.total_score.desc()).limit(200).all()

    # Find cards that appear most frequently in high synergies
    card_synergy_counts = defaultdict(int)
    card_total_scores = defaultdict(float)

    for synergy in synergies:
        card_synergy_counts[synergy.card1_id] += 1
        card_synergy_counts[synergy.card2_id] += 1
        card_total_scores[synergy.card1_id] += synergy.total_score
        card_total_scores[synergy.card2_id] += synergy.total_score

    # Find potential core cards (cards that synergize with many others)
    potential_cores = []
    for card_id, count in card_synergy_counts.items():
        if count >= 3:  # Must synergize with at least 3 other cards
            card = CardInfo.query.get(card_id)
            if card:
                avg_score = card_total_scores[card_id] / count
                potential_cores.append({
                    "card": card,
                    "synergy_count": count,
                    "average_score": avg_score,
                    "total_score": card_total_scores[card_id]
                })

    # Sort by synergy count and average score
    potential_cores.sort(key=lambda x: (x["synergy_count"], x["average_score"]), reverse=True)

    return potential_cores[:20]  # Top 20 potential cores

def analyze_archetype_synergies() -> Dict[str, Any]:
    """Analyze synergies by archetype."""
    print("🎭 Analyzing archetype synergies...")

    results = {
        "tribal": CardSynergy.query.filter(CardSynergy.tribal_score >= 10).count(),
        "combo": CardSynergy.query.filter(CardSynergy.combo_score >= 10).count(),
        "archetype": CardSynergy.query.filter(CardSynergy.archetype_score >= 10).count(),
        "keyword": CardSynergy.query.filter(CardSynergy.keyword_score >= 5).count(),
        "type": CardSynergy.query.filter(CardSynergy.type_score >= 5).count(),
    }

    # Find top archetype synergies
    top_tribal = CardSynergy.get_tribal_synergies(min_score=15.0)[:10]
    top_combo = CardSynergy.get_combo_synergies(min_score=15.0)[:10]

    results["top_tribal"] = top_tribal
    results["top_combo"] = top_combo

    return results

def find_hub_cards(min_synergies: int = 10) -> List[Dict[str, Any]]:
    """
    Find "hub" cards that synergize with many other cards.

    Args:
        min_synergies: Minimum number of synergies to be considered a hub

    Returns:
        List of hub cards with their synergy statistics
    """
    print(f"🌟 Finding hub cards (min_synergies: {min_synergies})")

    # Query all cards and count their synergies
    card_synergy_data = defaultdict(lambda: {
        "count": 0,
        "total_score": 0,
        "max_score": 0,
        "tribal_synergies": 0,
        "combo_synergies": 0
    })

    # Count synergies where each card appears
    synergies = CardSynergy.query.filter(CardSynergy.total_score >= 5.0).all()

    for synergy in synergies:
        for card_id in [synergy.card1_id, synergy.card2_id]:
            data = card_synergy_data[card_id]
            data["count"] += 1
            data["total_score"] += synergy.total_score
            data["max_score"] = max(data["max_score"], synergy.total_score)

            if synergy.tribal_score >= 5:
                data["tribal_synergies"] += 1
            if synergy.combo_score >= 5:
                data["combo_synergies"] += 1

    # Find hub cards
    hub_cards = []
    for card_id, data in card_synergy_data.items():
        if data["count"] >= min_synergies:
            card = CardInfo.query.get(card_id)
            if card:
                hub_cards.append({
                    "card": card,
                    "synergy_count": data["count"],
                    "average_score": data["total_score"] / data["count"],
                    "max_score": data["max_score"],
                    "tribal_synergies": data["tribal_synergies"],
                    "combo_synergies": data["combo_synergies"]
                })

    # Sort by synergy count
    hub_cards.sort(key=lambda x: x["synergy_count"], reverse=True)

    return hub_cards

def interactive_mode():
    """Interactive mode for exploring synergy data."""
    print("🎮 INTERACTIVE SYNERGY EXPLORER")
    print("=" * 60)
    print("Commands:")
    print("  • 'clusters [min_score] [min_size]' - Find synergy clusters")
    print("  • 'cores [archetype] [min_score]' - Find deck cores")
    print("  • 'hubs [min_synergies]' - Find hub cards")
    print("  • 'top [limit]' - Show top synergies")
    print("  • 'stats' - Show synergy statistics")
    print("  • 'card <name>' - Show synergies for specific card")
    print("  • 'quit' - Exit")
    print()

    while True:
        try:
            command = input("🔍 Enter command: ").strip()

            if command.lower() == 'quit':
                break

            elif command.startswith('clusters'):
                parts = command.split()
                min_score = float(parts[1]) if len(parts) > 1 else 15.0
                min_size = int(parts[2]) if len(parts) > 2 else 3

                clusters = find_synergy_clusters(min_score, min_size)
                print(f"\n🔗 Found {len(clusters)} synergy clusters:")
                for cluster in clusters[:10]:
                    print(f"  Cluster {cluster['id']}: {cluster['size']} cards, "
                          f"avg score: {cluster['average_synergy']:.1f}")
                    print(f"    Cards: {', '.join(cluster['card_names'][:5])}")
                    if len(cluster['card_names']) > 5:
                        print(f"    ... and {len(cluster['card_names']) - 5} more")

            elif command.startswith('cores'):
                parts = command.split()
                archetype = parts[1] if len(parts) > 1 and not parts[1].replace('.','').isdigit() else None
                min_score = float(parts[2] if archetype else parts[1]) if len(parts) > (2 if archetype else 1) else 20.0

                cores = find_deck_cores(archetype, min_score)
                print(f"\n🎯 Found {len(cores)} potential deck cores:")
                for core in cores[:10]:
                    print(f"  {core['card'].name}: {core['synergy_count']} synergies, "
                          f"avg score: {core['average_score']:.1f}")

            elif command.startswith('hubs'):
                parts = command.split()
                min_synergies = int(parts[1]) if len(parts) > 1 else 10

                hubs = find_hub_cards(min_synergies)
                print(f"\n🌟 Found {len(hubs)} hub cards:")
                for hub in hubs[:10]:
                    print(f"  {hub['card'].name}: {hub['synergy_count']} synergies, "
                          f"max score: {hub['max_score']:.1f}")

            elif command.startswith('top'):
                parts = command.split()
                limit = int(parts[1]) if len(parts) > 1 else 10

                top_synergies = CardSynergy.get_top_synergies(limit=limit)
                print(f"\n🔥 Top {limit} synergies:")
                for i, synergy in enumerate(top_synergies, 1):
                    print(f"  {i}. {synergy.card1.name} + {synergy.card2.name}: "
                          f"{synergy.total_score:.1f}")

            elif command == 'stats':
                archetype_stats = analyze_archetype_synergies()
                print(f"\n📊 Synergy Statistics:")
                print(f"  Tribal synergies: {archetype_stats['tribal']}")
                print(f"  Combo synergies: {archetype_stats['combo']}")
                print(f"  Archetype synergies: {archetype_stats['archetype']}")
                print(f"  Keyword synergies: {archetype_stats['keyword']}")
                print(f"  Type synergies: {archetype_stats['type']}")

            elif command.startswith('card '):
                card_name = command[5:].strip()
                card = CardInfo.query.filter(CardInfo.name.ilike(f'%{card_name}%')).first()
                if card:
                    synergies = CardSynergy.get_synergies_for_card(card.id, min_score=5.0, limit=10)
                    print(f"\n🃏 Top synergies for {card.name}:")
                    for synergy in synergies:
                        partner = synergy.get_partner_card(card.id)
                        if partner:
                            print(f"  {partner.name}: {synergy.total_score:.1f}")
                else:
                    print(f"❌ Card not found: {card_name}")

            else:
                print("❌ Unknown command. Type 'quit' to exit.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function."""
    app = create_app()

    with app.app_context():
        print("🎯 MTG SYNERGY GRAPH ANALYZER")
        print("=" * 60)

        # Check if synergy data exists
        total_synergies = CardSynergy.query.count()
        if total_synergies == 0:
            print("❌ No synergy data found!")
            print("Run synergy computation first: python scripts/compute_all_synergies.py")
            return

        print(f"📊 Found {total_synergies:,} stored synergies")
        print("Ready to analyze your collection's synergy graph!")
        print()

        interactive_mode()

if __name__ == "__main__":
    main()
