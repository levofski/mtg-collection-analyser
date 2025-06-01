# Project Status

[GitHub Repository](https://github.com/levofski/mtg-code-analyser)

## Project Overview

The goal of this project is to create a Python-based API to manage a "Magic: The Gathering" (MTG) card collection. The API will allow users to store their cards and will feature analysis capabilities to tag and score cards based on potential synergies with other cards.

## Current Phase

Initial project setup and implementation of core features.

## Key Decisions & Technologies Chosen

*   **Backend Language/Framework:** Python with Flask.
*   **Development Environment:** Docker Dev Container to ensure consistency and manage dependencies.
*   **Card Data Source (Planned):** Scryfall API (to be accessed via Python `requests` library).
*   **Text Analysis (Planned):**
    *   Python libraries like `spaCy` or `NLTK` are being considered for Natural Language Processing (NLP) to analyze card text for abilities, keywords, and mechanics.
*   **Synergy Modeling (Planned):**
    *   Python library `NetworkX` is being considered for representing cards and synergies as a graph, allowing for analysis of relationships and potential combos.
    *   Graph databases (e.g., Neo4j) are a potential future consideration for more complex synergy analysis.
*   **Data Validation:** Marshmallow for JSON schema validation of imported card data.
*   **Initial Dependencies (`requirements.txt`):**
    *   `Flask`
    *   `requests`
    *   `marshmallow`

## Setup So Far

*   Initialized a Git repository.
*   Created a `.devcontainer/devcontainer.json` file for VS Code to build and manage the Python development environment.
    *   Includes Python 3.11, `ms-python.python`, `ms-python.vscode-pylance` extensions.
    *   Configured for linting (Pylint) and formatting (autopep8).
    *   Port 5000 forwarded for the Flask application.
    *   `postCreateCommand` to install `requirements.txt`.
*   Created `requirements.txt` with initial dependencies.
*   Created a basic `main.py` with a "Hello World" Flask app using the application factory pattern.
*   Created a structured project layout with separate directories for routes, services, models, schemas, and data store.
*   Implemented CSV import functionality for card collections:
    *   Created a `/collection/import_csv` API endpoint that accepts CSV uploads.
    *   Implemented robust validation using Marshmallow schemas.
    *   Developed detailed error reporting for invalid CSV data.
*   Created a `Card` class for structured representation of collection items.
*   Implemented an in-memory store for cards with API endpoints to:
    *   View all cards in the collection (`GET /collection/cards`).
    *   Clear the collection (`POST /collection/clear`).
*   Created a `README.md` with project overview and setup instructions.
*   Created `.vscode/settings.json` for workspace-specific editor settings.
*   Created this `docs/project-status.md` file.

## Next Steps (Immediate)

*   Complete integration of the `Card` class with CSV importer and card store.
*   Implement logic to fetch card data from the Scryfall API to enrich imported cards.
*   Begin exploring card text analysis techniques.
*   Consider adding persistent storage (database) to replace the in-memory collection store.

