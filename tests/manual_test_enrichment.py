#!/usr/bin/env python3
"""
Manual test script to test the Scryfall enrichment API endpoints.
This script will:
1. Add sample cards to the collection
2. Enrich a single card
3. Enrich all cards
"""
import requests
import csv
import os
import io
from typing import List, Dict, Any

# API base URL
BASE_URL = "http://localhost:5000"

def create_sample_csv() -> io.StringIO:
    """
    Create a sample CSV file for testing.

    Returns:
        A StringIO object containing CSV data
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow([
        "Name", "Count", "Tradelist Count", "Edition", "Edition Code",
        "Card Number", "Condition", "Language", "Foil", "Signed",
        "Artist Proof", "Altered Art", "Misprint", "Promo", "Textless",
        "My Price", "Scryfall ID"
    ])

    # Write sample cards with Scryfall IDs
    cards = [
        ["Lightning Bolt", "4", "", "Masters 25", "a25", "141", "NM", "EN", "No", "No", "No", "No", "No", "No", "No", "", "fee393c7-1868-4d11-93c3-3d143e0c8dd9"],
        ["Black Lotus", "1", "", "Alpha", "lea", "232", "NM", "EN", "No", "No", "No", "No", "No", "No", "No", "", "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"],
        ["Birds of Paradise", "2", "", "Ravnica Allegiance: Guild Kits", "gk2", "82", "NM", "EN", "No", "No", "No", "No", "No", "No", "No", "", "f5e1c553-9fc0-475b-9298-3db1f67be1a1"],
        ["Sol Ring", "3", "", "Commander 2021", "c21", "263", "NM", "EN", "No", "No", "No", "No", "No", "No", "No", "", "0afa0e33-4804-430a-b799-952ce59200d6"]
    ]

    for card in cards:
        writer.writerow(card)

    # Reset the cursor to the beginning of the StringIO
    output.seek(0)
    return output

def import_cards() -> List[Dict[str, Any]]:
    """
    Import sample cards to the collection.

    Returns:
        The response data from the API
    """
    print("Step 1: Importing sample cards...")

    # Create sample CSV
    csv_data = create_sample_csv()

    # First, clear the collection
    response = requests.post(f"{BASE_URL}/collection/clear")
    print(f"  Cleared collection: {response.status_code} - {response.json()['message']}")

    # Import the CSV file
    files = {'file': ('sample.csv', csv_data.getvalue().encode('utf-8'), 'text/csv')}
    response = requests.post(f"{BASE_URL}/collection/import_csv", files=files)

    # Display results
    result = response.json()
    print(f"  Cards added: {result.get('cards_added_to_collection', 0)}")
    if 'validation_errors' in result and result['validation_errors']:
        print(f"  Validation errors: {len(result['validation_errors'])}")
        for error in result['validation_errors']:
            print(f"    - {error}")

    # Get all cards
    response = requests.get(f"{BASE_URL}/collection/cards")
    return response.json()['cards']

def enrich_single_card(card_id: int) -> Dict[str, Any]:
    """
    Enrich a single card.

    Args:
        card_id: The ID of the card to enrich

    Returns:
        The response data from the API
    """
    print(f"\nStep 2: Enriching single card (ID: {card_id})...")

    response = requests.post(f"{BASE_URL}/collection/cards/{card_id}/enrich")
    result = response.json()

    print(f"  Status: {response.status_code}")
    print(f"  Message: {result.get('message', 'No message')}")

    if 'card' in result:
        card = result['card']
        print("  Enrichment data:")
        print(f"    - Scryfall ID: {card.get('scryfall_id', 'N/A')}")
        print(f"    - Mana Cost: {card.get('mana_cost', 'N/A')}")
        print(f"    - Type Line: {card.get('type_line', 'N/A')}")
        print(f"    - Oracle Text: {card.get('oracle_text', 'N/A')[:100]}...")

    return result

def enrich_all_cards() -> Dict[str, Any]:
    """
    Enrich all cards in the collection.

    Returns:
        The response data from the API
    """
    print("\nStep 3: Enriching all cards...")

    response = requests.post(f"{BASE_URL}/collection/enrich-all")
    result = response.json()

    print(f"  Status: {response.status_code}")
    print(f"  Message: {result.get('message', 'No message')}")
    print(f"  Success count: {result.get('success_count', 0)}")
    print(f"  Total count: {result.get('total_count', 0)}")

    if 'errors' in result and result['errors']:
        print("  Errors:")
        for error in result['errors']:
            print(f"    - {error}")

    return result

def main():
    """Main function to run the tests."""
    print("Starting Scryfall Enrichment API Test\n" + "=" * 40)

    # Step 1: Import cards
    cards = import_cards()

    if not cards:
        print("No cards imported. Test cannot continue.")
        return

    # Step 2: Enrich a single card
    card_id = cards[0]['id']
    enrich_single_card(card_id)

    # Step 3: Enrich all cards
    enrich_all_cards()

    print("\nTest completed!")

if __name__ == "__main__":
    main()
