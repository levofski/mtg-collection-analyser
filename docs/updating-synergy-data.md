# Updating Synergy Data for Your MTG Collection

This guide provides multiple methods to update the enhanced synergy data for your entire MTG collection.

## 🚀 Quick Start - API Method (Recommended)

### Method 1: Using the API Endpoint

The fastest way to update all your cards with enhanced synergy analysis:

```bash
# Start your Flask application first
python main.py

# Then in another terminal, run:
curl -X POST http://localhost:5000/collection/analyze-all
```

**What this does:**
- Analyzes ALL cards in your collection with enhanced synergy detection
- Uses both oracle text AND Scryfall data for comprehensive analysis
- Extracts 200+ creature types, 100+ keywords, archetype indicators, combo potential
- Stores detailed synergy vectors for each card
- Updates the database with all extracted information

**Response Example:**
```json
{
  "message": "Analyzed 42 out of 45 cards.",
  "success_count": 42,
  "total_count": 45,
  "errors": [...]  // Any cards that failed
}
```

## 🔍 Method 2: Using Python Scripts

### Option A: Use the Enhanced Demo Script

```bash
cd /workspaces/mtg-collection-analyser
python scripts/enhanced_synergy_demo.py
```

This demonstrates the enhanced analysis but doesn't update your database.

### Option B: Create a Custom Update Script

Create a new script to update your actual collection:

```python
#!/usr/bin/env python3
"""
Update synergy data for the entire MTG collection.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.card_analysis import analyze_all_cards
from src.database import db
from main import create_app

def update_collection_synergy_data():
    """Update synergy data for all cards in the collection."""
    # Create Flask app context
    app = create_app()

    with app.app_context():
        print("🔍 Updating synergy data for entire collection...")
        print("=" * 60)

        # Analyze all cards with enhanced system
        successful, total, errors = analyze_all_cards()

        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"Successfully analyzed: {successful}/{total} cards")

        if errors:
            print(f"\n❌ Errors encountered ({len(errors)} cards):")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error['card_name']}: {error['error']}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")

        print(f"\n🎯 Your collection now has enhanced synergy data!")
        print("  - Tribal synergies (200+ creature types)")
        print("  - Keyword synergies (100+ abilities)")
        print("  - Archetype detection (aggro, control, combo, etc.)")
        print("  - Combo potential identification")
        print("  - Color and format compatibility")
        print("  - Mana curve analysis")

if __name__ == "__main__":
    update_collection_synergy_data()
```

Save this as `scripts/update_collection_synergies.py` and run:

```bash
python scripts/update_collection_synergies.py
```

## 🛠 Method 3: Database Direct Access

### Check Current Analysis Status

First, see which cards already have analysis data:

```bash
cd /workspaces/mtg-collection-analyser
python -c "
from main import create_app
from src.models.card_info import CardInfo

app = create_app()
with app.app_context():
    total_cards = CardInfo.query.count()
    analyzed_cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).count()
    print(f'Total cards: {total_cards}')
    print(f'Analyzed cards: {analyzed_cards}')
    print(f'Need analysis: {total_cards - analyzed_cards}')
"
```

### Analyze Specific Cards

If you want to analyze specific cards by name:

```python
from main import create_app
from src.models.card_info import CardInfo
from src.services.card_analysis import analyze_card

app = create_app()
with app.app_context():
    # Find cards by name
    card_names = ["Lightning Bolt", "Counterspell", "Goblin Guide"]

    for name in card_names:
        card = CardInfo.query.filter_by(name=name).first()
        if card:
            updated_card, message = analyze_card(card.id)
            print(f"{name}: {message}")
        else:
            print(f"{name}: Not found in collection")
```

## 📊 Method 4: Batch Processing for Large Collections

For very large collections (1000+ cards), you might want to process in batches:

```python
#!/usr/bin/env python3
"""
Batch process large collections for synergy analysis.
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.card_info import CardInfo
from src.services.card_analysis import analyze_card
from src.database import db
from main import create_app

def batch_analyze_collection(batch_size=100):
    """Analyze collection in batches to avoid memory issues."""
    app = create_app()

    with app.app_context():
        # Get cards that need analysis
        cards_to_analyze = CardInfo.query.filter(
            CardInfo.extracted_data.is_(None)
        ).all()

        total_cards = len(cards_to_analyze)
        print(f"🔍 Processing {total_cards} cards in batches of {batch_size}")

        successful = 0
        errors = []

        for i in range(0, total_cards, batch_size):
            batch = cards_to_analyze[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_cards + batch_size - 1) // batch_size

            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} cards)...")

            for card in batch:
                try:
                    updated_card, message = analyze_card(card.id)
                    if updated_card:
                        successful += 1
                        print(f"  ✅ {card.name}")
                    else:
                        errors.append({"card_name": card.name, "error": message})
                        print(f"  ❌ {card.name}: {message}")
                except Exception as e:
                    errors.append({"card_name": card.name, "error": str(e)})
                    print(f"  ❌ {card.name}: {str(e)}")

            # Small delay between batches
            if i + batch_size < total_cards:
                time.sleep(1)

        print(f"\n✅ BATCH PROCESSING COMPLETE!")
        print(f"Successfully analyzed: {successful}/{total_cards} cards")
        print(f"Errors: {len(errors)} cards")

if __name__ == "__main__":
    batch_analyze_collection()
```

## 🔍 Verification & Validation

### Check Analysis Results

After updating, verify the enhanced data is present:

```python
from main import create_app
from src.models.card_info import CardInfo
import json

app = create_app()
with app.app_context():
    # Get a random analyzed card
    card = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).first()

    if card and card.extracted_data:
        data = card.extracted_data
        print(f"📋 Analysis for: {card.name}")
        print(f"🏷️  Keywords: {data.get('keywords', [])}")
        print(f"🎭 Creature Types: {data.get('creature_types', [])}")
        print(f"🎨 Colors: {data.get('colors', [])}")
        print(f"⚡ Archetypes: {data.get('synergy_vectors', {}).get('archetype', [])}")
        print(f"💥 Combo Potential: {data.get('synergy_vectors', {}).get('combo_potential', [])}")
    else:
        print("No analyzed cards found. Run analysis first!")
```

### Test Synergy Detection

Test the enhanced synergy detection on your collection:

```python
from main import create_app
from src.models.card_info import CardInfo
from src.services.text_analysis import find_synergy_candidates

app = create_app()
with app.app_context():
    # Get all analyzed cards
    cards = CardInfo.query.filter(CardInfo.extracted_data.isnot(None)).all()

    if len(cards) < 2:
        print("Need at least 2 analyzed cards for synergy testing")
    else:
        # Test synergy detection with first card
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

        print(f"🔗 Synergies for {target_card.name}:")
        for i, synergy in enumerate(synergies[:5], 1):  # Top 5
            other_name = synergy["card"].get('name', 'Unknown')
            score = synergy["score"]
            print(f"  {i}. {other_name} (Score: {score:.1f})")
```

## 🎯 Recommendations

### Before Running Analysis:
1. **Ensure your cards are enriched** with Scryfall data first:
   ```bash
   curl -X POST http://localhost:5000/collection/enrich-all
   ```

2. **Back up your database** (optional but recommended):
   ```bash
   cp instance/mtg_collection.db instance/mtg_collection_backup.db
   ```

### After Running Analysis:
1. **Verify the results** using the verification scripts above
2. **Test synergy detection** to ensure it's working correctly
3. **Check for errors** and re-run analysis for failed cards if needed

### Best Practices:
- **Start small**: Test on a few cards first using individual analysis
- **Use API method**: The `/analyze-all` endpoint is the most reliable
- **Check logs**: Monitor the console output for any error messages
- **Incremental updates**: The system only analyzes cards that need it

## 🚀 Quick Command Summary

```bash
# 1. Start your application
python main.py

# 2. Update all synergy data (in another terminal)
curl -X POST http://localhost:5000/collection/analyze-all

# 3. Verify results
curl http://localhost:5000/collection/card-infos | jq '.card_infos[0].extracted_data'
```

Your collection will now have comprehensive synergy data including tribal relationships, archetype classification, combo potential, and multi-dimensional compatibility scoring! 🎉
