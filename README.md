# MTG Collection API

A Python-based API for managing and analyzing a "Magic: The Gathering" card collection with advanced synergy detection capabilities. The API stores collections, enriches card data from Scryfall, and provides comprehensive multi-dimensional synergy analysis.

## Project Goals

- Store and retrieve MTG card collections with full CRUD operations.
- Enrich card data from the Scryfall API (oracle text, types, costs, etc.).
- **Enhanced Text Analysis**: Extract keywords, abilities, types, and game mechanics using NLP.
- **Multi-Dimensional Synergy Detection**: Analyze tribal, color, archetype, combo, and format synergies.
- **Advanced Scoring**: Weighted synergy scoring with detailed explanations.
- **Collection Analysis**: Find synergies across entire card collections.

## Key Features

### 🔍 **Comprehensive Card Analysis**
- **200+ Creature Types**: Advanced tribal synergy detection
- **100+ Keywords & Abilities**: Complete MTG mechanics coverage
- **Archetype Detection**: Automatic classification (aggro, control, combo, etc.)
- **Combo Potential**: Infinite combo and engine piece identification
- **Mana Analysis**: Color requirements, curve, and intensity

### 🤝 **Multi-Dimensional Synergy Detection**
- **Tribal Synergies**: Creature type matching and support (5.0x weight)
- **Color Synergies**: Identity compatibility and multicolor support
- **Keyword Synergies**: Shared and complementary abilities
- **Archetype Synergies**: Deck strategy alignment (4.0x weight)
- **Combo Synergies**: Infinite combo detection (4.0x weight)
- **Type Synergies**: Artifacts, enchantments, and legendary matters
- **Mana Curve**: Cost distribution analysis
- **Format Synergies**: Legal format overlap

### 📊 **Advanced Scoring System**
- **Weighted Scoring**: Importance-based calculation
- **Detailed Breakdown**: Score explanation by category
- **Threshold Filtering**: Configurable minimum requirements
- **Collection-Wide Analysis**: Find synergies across entire collections

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup & Running

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd mtg-collection-analyser
    ```
2.  **Open in Dev Container:**
    Open the project folder in VS Code. You should be prompted to "Reopen in Container". Click it.
    This will build the Docker container defined in `.devcontainer/devcontainer.json` and install all necessary dependencies.
3.  **Run the application:**
    Once the container is running and the VS Code window has reloaded, open a new terminal in VS Code (it will be a terminal inside the container) and run:
    ```bash
    python main.py
    ```
    The API will be accessible at `http://localhost:5000`.

## Development

(Details about linters, formatters, and testing will be added here.)

## API Endpoints

### Collection Management

- **GET /collection/cards** - Get all cards in the collection
- **GET /collection/cards/{id}** - Get a specific card by ID
- **PUT /collection/cards/{id}** - Update a specific card
- **DELETE /collection/cards/{id}** - Delete a specific card
- **DELETE /collection** - Clear the entire collection

### CSV Import

- **POST /collection/import_csv** - Import cards from a CSV file

### Scryfall Integration

- **POST /collection/cards/{id}/enrich** - Enrich a specific card with Scryfall data
- **POST /collection/enrich-all** - Enrich all cards in the collection with Scryfall data
