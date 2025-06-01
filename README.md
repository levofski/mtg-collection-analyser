# MTG Collection API

A Python-based API for managing and analyzing a "Magic: The Gathering" card collection. The API will allow users to store their card collection, and will tag and score cards based on synergies.

## Project Goals

- Store and retrieve MTG card collections.
- Fetch card data from external APIs (e.g., Scryfall).
- Analyze card text and properties to identify potential synergies.
- Tag cards with relevant synergy information.
- Score cards or combinations of cards based on synergistic potential.

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
