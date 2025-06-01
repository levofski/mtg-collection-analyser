# Scryfall API Reference

This document provides an overview of the Scryfall API and how we use it in the MTG Collection Analyser to fetch card data.

## General API Information

- **Base URL**: `https://api.scryfall.com`
- **Protocol**: HTTPS only (TLS 1.2 or better)
- **Character Encoding**: UTF-8
- **Rate Limits**: 50-100ms delay between requests (max 10 requests per second)
  - Exceeding the rate limit results in HTTP 429 (Too Many Requests)
  - Repeated abuse may result in temporary or permanent IP ban
- **Caching**: Recommended to cache data for at least 24 hours
  - Price data only updates once per day
  - Game data (Oracle text, mana costs, etc.) updates less frequently

## Required Headers

- **User-Agent**: Must be accurate to our usage context (e.g., `MTG-Collection-Analyser/1.0`)
- **Accept**: Must be present (e.g., `Accept: application/json` or `Accept: */*`)

## Key Endpoints for Our Project

### 1. Cards by Name

```
GET /cards/named
```

This endpoint is useful for looking up a specific card by name, which will be our primary method for fetching detailed card information based on our CSV import data.

**Parameters**:
- `exact` (String): The exact card name to search for (case-insensitive)
- `fuzzy` (String): A fuzzy card name to search for (allows partial matches and misspellings)
- `set` (String, Optional): A set code to limit the search to one set
- `format` (String, Optional): The data format to return: json, text, or image (default: json)

**Example**:
```
GET https://api.scryfall.com/cards/named?exact=Lightning+Bolt
```

**Use case in our application**: When we import cards from CSV, we can use this endpoint to fetch detailed card information based on the name and set.

### 2. Cards by Set Code and Collector Number

```
GET /cards/:code/:number
```

This endpoint allows us to fetch a specific card print by its set code and collector number.

**Example**:
```
GET https://api.scryfall.com/cards/inr/139
```

**Use case**: For cards that have set code and collector number in our imported CSV data, this is the most precise way to fetch the exact printing.

### 3. Search Cards

```
GET /cards/search
```

This endpoint allows more complex searches using Scryfall's powerful query syntax.

**Parameters**:
- `q` (String): A query using Scryfall's search syntax
- `order` (String, Optional): How to order the returned cards
- `dir` (String, Optional): Direction of ordering (asc or desc)
- `include_extras` (Boolean, Optional): Include cards that aren't normally obtained in games
- `include_multilingual` (Boolean, Optional): Include non-English cards
- `include_variations` (Boolean, Optional): Include card variants
- `page` (Integer, Optional): Page number for paginated results
- `unique` (String, Optional): Strategy for handling duplicate cards (cards, art, or prints)

**Example**:
```
GET https://api.scryfall.com/cards/search?q=c%3Ared+pow%3D3
```

**Use case**: For advanced card searches and analysis features.

## Card Object

The Card object is the most complex data structure returned by the API. Here are some important fields that we'll use in our application:

### Core Fields
- `id` (UUID): Unique identifier for this card in Scryfall's database
- `name` (String): The card name
- `lang` (String): Language code for the card
- `uri` (URI): Link to the card on Scryfall's API
- `scryfall_uri` (URI): Link to the card on Scryfall's website

### Gameplay Fields
- `mana_cost` (String): The mana cost for the card
- `cmc` (Decimal): Converted mana cost/mana value
- `type_line` (String): The card's type line
- `oracle_text` (String): The official rules text
- `colors` (Array): The colors of the card
- `color_identity` (Array): The card's color identity
- `keywords` (Array): Keywords on the card
- `legalities` (Object): Card legality across formats
- `reserved` (Boolean): Whether the card is on the Reserved List
- `power` (String): The card's power (if applicable)
- `toughness` (String): The card's toughness (if applicable)
- `edhrec_rank` (Integer): The card's popularity rank on EDHREC

### Print Fields
- `set` (String): The set code
- `set_name` (String): Full set name
- `collector_number` (String): Collector number within the set
- `rarity` (String): Card rarity
- `artist` (String): Card artist
- `prices` (Object): Price information in various currencies
- `image_uris` (Object): Links to card images in various formats
- `foil` (Boolean): Whether the card is foil
- `nonfoil` (Boolean): Whether the card is available in non-foil
- `promo` (Boolean): Whether this is a promotional print
- `reprint` (Boolean): Whether this card is a reprint
- `released_at` (Date): When this card was first released

### Multiface Cards

For double-faced cards, transform cards, adventure cards, etc., the `card_faces` array contains individual faces with their own properties like `name`, `mana_cost`, `type_line`, `oracle_text`, and `image_uris`.

## Best Practices for Our Implementation

1. **Caching**: Implement client-side caching of Scryfall responses to reduce API calls and stay within rate limits.

2. **Error Handling**: Handle API errors gracefully, especially 404 (Not Found) and 429 (Too Many Requests).

3. **Rate Limiting**: Ensure our requests follow the rate limit guidelines (50-100ms between requests).

4. **Identifiers**: When possible, use precise identifiers (set code + collector number) rather than relying on name searches.

5. **User Experience**: Show appropriate loading indicators during API calls and meaningful error messages if the API is unavailable.

6. **Attribution**: Follow Scryfall's guidelines for attribution and usage of their data.

## Implementation Plan

1. Create a `scryfall_service.py` module that encapsulates all API calls to Scryfall.
2. Implement retry logic and rate limiting in this service.
3. Create methods for each key endpoint we need (by name, by set+collector number).
4. Build a caching mechanism to store responses and avoid redundant API calls.
5. Develop a background process to enrich our imported card data with details from Scryfall.

## References

- [Scryfall API Documentation](https://scryfall.com/docs/api)
- [Card Objects Reference](https://scryfall.com/docs/api/cards)
- [Images Guide](https://scryfall.com/docs/api/images)
