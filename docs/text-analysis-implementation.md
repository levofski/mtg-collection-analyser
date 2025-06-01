# Text Analysis Implementation

This document outlines the implementation details of the card text analysis feature.

## Overview

The card text analysis feature uses Natural Language Processing (NLP) to extract meaningful information from Magic: The Gathering card text. This information is used to identify card characteristics, detect synergies between cards, and build a network representation of card relationships.

## Components

### 1. Text Analysis Service (`src/services/text_analysis.py`)

This service provides core NLP functionality:

- **Card Text Analysis**: Extracts keywords, actions, zones, and other relevant information
- **MTG-Specific Pattern Recognition**: Identifies game-specific terminology
- **Synergy Candidate Detection**: Finds potential synergies between cards

Main functions:
- `analyze_card_text(oracle_text)`: Processes card text and returns extracted information
- `extract_mtg_keywords(doc, category)`: Extracts keywords from a specific category
- `extract_noun_phrases(doc)`: Extracts important noun phrases
- `extract_named_entities(doc)`: Extracts named entities
- `find_synergy_candidates(card_text, collection_keywords)`: Identifies potential synergies

### 2. Card Analysis Service (`src/services/card_analysis.py`)

This service applies text analysis to cards in the database:

- **Individual Card Analysis**: Analyzes a single card and stores results
- **Batch Processing**: Processes all cards in the collection
- **Database Integration**: Stores results in the `CardInfo` model

Main functions:
- `analyze_card(card_info_id)`: Analyzes a specific card by ID
- `analyze_all_cards()`: Processes all cards in the collection

### 3. Model Enhancement (`src/models/card_info.py`)

The `CardInfo` model was enhanced to store analysis results:

- **Text Analysis Fields**: Added fields for keywords and extracted data
- **JSON Serialization**: Implemented methods to convert between Python objects and JSON

Key additions:
- `_keywords`: Stores card keywords as JSON
- `_extracted_data`: Stores all extracted information as JSON

### 4. Demonstration Scripts

- **`standalone_text_analysis.py`**: Demonstrates basic text analysis on sample cards
- **`synergy_detection_demo.py`**: Shows how synergies are detected between cards
- **`synergy_visualization_demo.py`**: Creates a network visualization of card relationships

## API Endpoints

- **`/collection/card-infos/<id>/analyze`**: Analyzes a specific card
- **`/collection/card-infos/analyze-all`**: Analyzes all cards in the collection

## Results

The text analysis implementation successfully:

1. Extracts keywords, abilities, and game-specific terminology from card text
2. Identifies relationships between cards based on shared mechanics
3. Provides a foundation for more advanced synergy detection
4. Creates meaningful visualizations of card relationships

## Next Steps

1. **Advanced Synergy Scoring**:
   - Develop more sophisticated algorithms to score card synergies
   - Consider contextual relationships beyond keyword matching

2. **User Interface**:
   - Create a web interface for exploring card relationships
   - Implement interactive graph visualizations

3. **Performance Optimization**:
   - Improve batch processing for large collections
   - Implement caching for frequent analysis requests

4. **Integration with External Data**:
   - Combine text analysis with format/meta data from other sources
   - Incorporate deck archetype information for contextual synergy detection
