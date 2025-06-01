# Scryfall Integration

This document provides information on how the Scryfall API integratio### Lookup Strategy**: Tries to find the most precise match for a card:
  1. First by Scryfall ID (preferred method)
  2. Then by set code + collector number
  3. Then by exact name + set code
  4. Finally by name onlyrks in the MTG Collection Analyser.

## Overview

The MTG Collection Analyser integrates with the [Scryfall API](https://scryfall.com/docs/api) to enrich card data in the collection. When cards are imported from a CSV file, they may have minimal information (name, set, collector number, etc.). The Scryfall integration allows us to fetch additional data such as:

- Oracle text (official rules text)
- Mana cost
- Converted mana cost (CMC)
- Type line
- Card images
- And more

## API Endpoints

Two API endpoints are available for card enrichment:

### 1. Enrich a Single Card

```
POST /collection/cards/{id}/enrich
```

This endpoint enriches a specific card by its ID with data from the Scryfall API.

Example:
```bash
curl -X POST http://localhost:5000/collection/cards/1/enrich
```

### 2. Enrich All Cards

```
POST /collection/enrich-all
```

This endpoint enriches all cards in the collection with data from the Scryfall API.

Example:
```bash
curl -X POST http://localhost:5000/collection/enrich-all
```

## Testing the Integration

Two testing methods are available:

### 1. Automated Test

Run the automated test using:

```bash
cd /workspaces/mtg-collection-analyser
python -m unittest tests.test_scryfall_enrichment
```

This will run a series of tests to ensure the enrichment functionality is working correctly.

### 2. Manual Test Script

A manual test script is also available that:
1. Imports sample cards
2. Enriches a single card
3. Enriches all cards

Run it using:

```bash
cd /workspaces/mtg-collection-analyser
./tests/manual_test_enrichment.py
```

Note: Make sure the Flask application is running in a separate terminal:

```bash
python main.py
```

## Implementation Details

The Scryfall integration is implemented in the following files:

- `src/services/scryfall_service.py`: Service for making requests to the Scryfall API
- `src/store/card_store.py`: Functions for enriching cards with Scryfall data
- `src/routes/collection_routes.py`: API endpoints for enrichment

### Features

- **Rate Limiting**: Implements rate limiting to stay within Scryfall's API guidelines
- **Caching**: Caches responses to reduce redundant API calls
- **Error Handling**: Gracefully handles API errors with retries for transient issues
- **Progressive Commits**: Database changes are committed after each card enrichment to preserve progress in case of failures
- **Lookup Strategy**: Tries to find the most precise match for a card:
  1. First by Scryfall ID (preferred method)
  2. Then by set code + collector number
  3. Then by exact name + set code
  4. Finally by name only

## Next Steps

Future improvements to consider:

1. **Background Processing**: Handle bulk enrichment as a background task using Celery or similar
2. **Progress Tracking**: Implement progress tracking for large collection enrichment
3. **Enhanced Error Recovery**: Add more robust error recovery for failed enrichment attempts
4. **Selective Enrichment**: Allow selective enrichment of specific fields

## Reference

- [Scryfall API Documentation](https://scryfall.com/docs/api)
- [Project Status](project-status.md)
- [Scryfall API Reference](scryfall-api-reference.md)
