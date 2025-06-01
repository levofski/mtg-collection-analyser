#!/usr/bin/env python3
"""
Demonstrates synergy detection and visualization using NetworkX.
"""
import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Set, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.text_analysis import analyze_card_text, find_synergy_candidates

# Sample cards for synergy detection
SAMPLE_CARDS = [
    {
        "name": "Reanimate",
        "oracle_text": "Put target creature card from a graveyard onto the battlefield under your control. You lose life equal to its mana value."
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
    },
    {
        "name": "Aven Mindcensor",
        "oracle_text": "Flash\nFlying\nIf an opponent would search a library, that player searches the top four cards of that library instead."
    },
    {
        "name": "Tormod's Crypt",
        "oracle_text": "{T}, Sacrifice Tormod's Crypt: Exile all cards from target player's graveyard."
    },
    {
        "name": "Buried Alive",
        "oracle_text": "Search your library for up to three creature cards, put them into your graveyard, then shuffle."
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

def detect_synergies(cards: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect potential synergies between cards with strength scores.
    """
    synergies = {}

    # For each card, find synergies with other cards
    for card in cards:
        card_synergies = []

        # Check each other card
        for other_card in cards:
            if other_card["name"] == card["name"]:
                continue

            # Calculate synergy score based on matching keywords, zones, and actions
            score = 0
            matches = []

            # Check if this card's zones are mentioned in other card's text
            for zone in card["analysis"].get("zones", []):
                if zone in other_card["oracle_text"].lower():
                    score += 2
                    matches.append(f"zone:{zone}")

            # Check if this card's actions are mentioned in other card's text
            for action in card["analysis"].get("actions", []):
                if action in other_card["oracle_text"].lower():
                    score += 1
                    matches.append(f"action:{action}")

            # Check if this card's keywords are mentioned in other card's text
            for keyword in card["analysis"].get("keywords", []):
                if keyword in other_card["oracle_text"].lower():
                    score += 3
                    matches.append(f"keyword:{keyword}")

            # Add synergy if score is positive
            if score > 0:
                card_synergies.append({
                    "card": other_card["name"],
                    "score": score,
                    "matches": matches
                })

        # Sort synergies by score
        card_synergies.sort(key=lambda x: x["score"], reverse=True)
        synergies[card["name"]] = card_synergies

    return synergies

def build_synergy_graph(cards: List[Dict[str, Any]], synergies: Dict[str, List[Dict[str, Any]]]) -> nx.Graph:
    """
    Build a NetworkX graph representing card synergies.
    """
    G = nx.Graph()

    # Add nodes (cards)
    for card in cards:
        # Determine node size based on number of synergies
        size = sum(1 for c in synergies.values() if any(s["card"] == card["name"] for s in c))

        # Get card type from type line or make a guess
        card_type = "Unknown"
        text = card["oracle_text"].lower()

        if "creature" in text:
            card_type = "Creature"
        elif "instant" in text:
            card_type = "Instant"
        elif "sorcery" in text:
            card_type = "Sorcery"
        elif "enchant" in text:
            card_type = "Enchantment"
        elif "artifact" in text:
            card_type = "Artifact"

        G.add_node(card["name"],
                  size=100 + (size * 50),
                  type=card_type)

    # Add edges (synergies)
    for card_name, card_synergies in synergies.items():
        for synergy in card_synergies:
            other_card = synergy["card"]
            if not G.has_edge(card_name, other_card):
                G.add_edge(card_name, other_card, weight=synergy["score"])

    return G

def visualize_synergies(G: nx.Graph):
    """
    Visualize the synergy graph.
    """
    plt.figure(figsize=(12, 8))

    # Node positions
    pos = nx.spring_layout(G, seed=42)

    # Node sizes
    sizes = [G.nodes[node]["size"] for node in G.nodes]

    # Node colors by type
    type_to_color = {
        "Creature": "lightgreen",
        "Instant": "lightblue",
        "Sorcery": "coral",
        "Enchantment": "plum",
        "Artifact": "gold",
        "Unknown": "gray"
    }

    colors = [type_to_color[G.nodes[node]["type"]] for node in G.nodes]

    # Edge weights
    weights = [G[u][v]["weight"] for u, v in G.edges]

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.5, edge_color="gray")
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

    # Create a legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=card_type,
                          markerfacecolor=color, markersize=10)
                 for card_type, color in type_to_color.items() if any(G.nodes[node]["type"] == card_type for node in G.nodes)]

    plt.legend(handles=legend_elements, loc='upper left')

    plt.axis("off")
    plt.title("MTG Card Synergy Network")
    plt.tight_layout()

    # Save the figure
    plt.savefig("card_synergy_network.png")
    print(f"Graph visualization saved to 'card_synergy_network.png'")

def main():
    """Run the synergy visualization demo."""
    print("MTG Card Synergy Network Visualization")
    print("=====================================\n")

    # Analyze all cards
    analyzed_cards = analyze_cards()

    # Detect synergies
    synergies = detect_synergies(analyzed_cards)

    # Print synergies
    for card_name, card_synergies in synergies.items():
        print(f"{card_name}:")
        if card_synergies:
            for synergy in card_synergies:
                print(f"  - {synergy['card']} (Score: {synergy['score']}, Matches: {', '.join(synergy['matches'])})")
        else:
            print("  - No synergies detected")
        print()

    # Build and visualize the synergy graph
    G = build_synergy_graph(analyzed_cards, synergies)
    visualize_synergies(G)

if __name__ == "__main__":
    main()
