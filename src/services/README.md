# MTG Text Analysis Module

This module provides Natural Language Processing (NLP) capabilities to analyze Magic: The Gathering card text.

## Features

- Extraction of keywords, abilities, and mechanics from card text
- Identification of game zones and actions referenced in card text
- Detection of potential synergies between cards
- Storage of analysis results in the database
- Visualization of card relationships as a network graph

## Prerequisites

- Python 3.11+
- spaCy with English language model
- NetworkX and Matplotlib for visualization

## Setup

1. Ensure Python 3.11+ is installed
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Download the spaCy English language model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

### Analyzing Card Text

```python
from src.services.text_analysis import analyze_card_text

# Analyze a card's oracle text
card_text = "Flying\nWhen this creature enters the battlefield, draw a card."
analysis = analyze_card_text(card_text)

# Access extracted information
keywords = analysis.get('keywords', [])
actions = analysis.get('actions', [])
zones = analysis.get('zones', [])
```

### Analyzing Cards in the Database

```python
from src.services.card_analysis import analyze_card, analyze_all_cards

# Analyze a specific card
card_info, message = analyze_card(card_info_id)

# Analyze all cards in the collection
successful, total, errors = analyze_all_cards()
```

### Finding Synergies

```python
from src.services.text_analysis import find_synergy_candidates

# Find potential synergies
card_text = "Search your library for a card and put it into your hand."
collection_keywords = {"flying", "search", "library", "draw"}
synergies = find_synergy_candidates(card_text, collection_keywords)
```

### Using the API Endpoints

- `POST /collection/card-infos/<id>/analyze`: Analyze a specific card
- `POST /collection/card-infos/analyze-all`: Analyze all cards in the collection

## Demo Scripts

Several demonstration scripts are available:

- `scripts/standalone_text_analysis.py`: Basic text analysis demo with sample cards
- `scripts/synergy_detection_demo.py`: Demonstrates synergy detection between cards
- `scripts/synergy_visualization_demo.py`: Creates a network visualization of card relationships

## How it Works

1. **Text Processing**: Card text is processed using spaCy's NLP pipeline
2. **Pattern Matching**: MTG-specific terminology is identified using custom pattern recognition
3. **Keyword Extraction**: Keywords, actions, and zones are extracted from the text
4. **Synergy Detection**: Cards are compared to find shared mechanics and interactions
5. **Visualization**: Card relationships are visualized as a network graph using NetworkX

## Contributing

To enhance the text analysis capabilities:

1. Add new keywords, zones, or actions in `src.services.text_analysis.MTG_KEYWORDS`
2. Improve synergy detection by modifying the scoring algorithm in `scripts/synergy_visualization_demo.py`
3. Add test cases with interesting card interactions

## Future Enhancements

- Contextual analysis of card interactions
- Machine learning-based synergy prediction
- Integration with deck archetype data
- Interactive web visualization of card networks
