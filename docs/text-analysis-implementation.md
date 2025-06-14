# Enhanced Text Analysis Implementation

This document outlines the implementation details of the enhanced card text analysis feature.

## Overview

The enhanced card text analysis feature uses comprehensive Natural Language Processing (NLP) and structured data analysis to extract detailed information from Magic: The Gathering cards. This system analyzes both oracle text and card metadata from the Scryfall API to identify card characteristics, detect complex synergies between cards, and build sophisticated network representations of card relationships.

## Key Features

### Comprehensive Data Extraction
- **Oracle Text Analysis**: Keywords, abilities, actions, zones, and game mechanics
- **Type Line Parsing**: Card types, creature types, planeswalker types, artifact/enchantment subtypes
- **Mana Cost Analysis**: Color requirements, converted mana cost, mana intensiveness
- **Statistical Data**: Power/toughness, rarity, format legalities
- **Metadata**: Set information, artist, card numbers

### Multi-Dimensional Synergy Detection
- **Tribal Synergies**: Creature type matching and tribal support detection (weight: 5.0x)
- **Color Synergies**: Color identity compatibility, multicolor synergies (weight: 1.5x)
- **Keyword Synergies**: Shared and complementary abilities (weight: 3.0x)
- **Archetype Detection**: Aggro, control, combo, graveyard, artifacts, etc. (weight: 4.0x)
- **Combo Potential**: Infinite combos, engine pieces, tutoring effects (weight: 4.0x)
- **Type Synergies**: Artifact/enchantment interactions, legendary matters (weight: 2.0x)
- **Mana Curve Analysis**: Cost distribution and color requirements (weight: 1.0x)
- **Format Compatibility**: Legal format overlap analysis (weight: 0.5x)

### Advanced Scoring System
- **Weighted Scoring**: Different synergy types have appropriate weights based on importance
- **Detailed Breakdown**: Individual scores for each synergy category
- **Match Explanations**: Specific reasons for each synergy connection
- **Threshold Filtering**: Configurable minimum synergy requirements

## Components

### 1. Enhanced Text Analysis Service (`src/services/text_analysis.py`)

This service provides comprehensive NLP and data analysis functionality:

#### Core Functions:
- **`analyze_card_text(oracle_text, card_data)`**: Processes both card text and structured data
- **`extract_card_data_features(card_data)`**: Extracts features from Scryfall API data
- **`parse_type_line(type_line)`**: Parses card types and subtypes
- **`parse_mana_cost(mana_cost)`**: Analyzes mana cost requirements
- **`generate_synergy_vectors(analysis)`**: Creates synergy compatibility vectors
- **`calculate_synergy_score(card1, card2)`**: Comprehensive synergy scoring
- **`find_synergy_candidates(card, collection)`**: Collection-wide synergy detection

#### Enhanced Data Extraction:
- **MTG Keywords**: 100+ abilities, keywords, and mechanics
- **Creature Types**: 200+ creature subtypes for tribal synergies
- **Planeswalker Types**: All planeswalker subtypes
- **Artifact/Enchantment Subtypes**: Equipment, vehicles, auras, sagas, etc.
- **Archetype Detection**: Automatic classification into deck archetypes
- **Combo Indicators**: Detection of infinite combo potential
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
- **`/collection/analyze-all`**: Analyzes all cards in the collection

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
