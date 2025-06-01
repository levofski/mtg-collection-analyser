# Project Status

[GitHub Repository](https://github.com/levofski/mtg-code-analyser)

## Project Overview

The goal of this project is to create a Python-based API to manage a "Magic: The Gathering" (MTG) card collection. The API will allow users to store their cards and will feature analysis capabilities to tag and score cards based on potential synergies with other cards.

## Current Phase

Initial project setup and implementation of core features.

## Key Decisions & Technologies Chosen

*   **Backend Language/Framework:** Python with Flask.
*   **Development Environment:** Docker Dev Container to ensure consistency and manage dependencies.
*   **Data Storage:** SQLAlchemy ORM with SQLite database.
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
    *   `SQLAlchemy`
    *   `Flask-SQLAlchemy`

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
*   Created a `Card` class as a SQLAlchemy model for structured representation of collection items.
*   Implemented a SQLite database for persistent data storage:
    *   Used Flask-SQLAlchemy for ORM capabilities.
    *   Implemented CRUD operations for cards (Create, Read, Update, Delete).
    *   Added REST API endpoints for card operations:
        *   `GET /collection/cards` - View all cards in the collection.
        *   `GET /collection/cards/<id>` - View a specific card.
        *   `PUT /collection/cards/<id>` - Update a specific card.
        *   `DELETE /collection/cards/<id>` - Delete a specific card.
        *   `DELETE /collection` - Clear the collection.
*   Created documentation for the Scryfall API (`docs/scryfall-api-reference.md`):
    *   Documented key endpoints needed for our project
    *   Outlined best practices for API integration
    *   Established implementation plan for card data enrichment
*   Created a `README.md` with project overview and setup instructions.
*   Created `.vscode/settings.json` for workspace-specific editor settings.
*   Created this `docs/project-status.md` file.

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
*   Created a `Card` class as a SQLAlchemy model for structured representation of collection items.
*   Implemented a SQLite database for persistent data storage:
    *   Used Flask-SQLAlchemy for ORM capabilities.
    *   Implemented CRUD operations for cards (Create, Read, Update, Delete).
    *   Added REST API endpoints for card operations:
        *   `GET /collection/cards` - View all cards in the collection.
        *   `GET /collection/cards/<id>` - View a specific card.
        *   `PUT /collection/cards/<id>` - Update a specific card.
        *   `DELETE /collection/cards/<id>` - Delete a specific card.
        *   `DELETE /collection` - Clear the collection.
*   Created documentation for the Scryfall API (`docs/scryfall-api-reference.md`):
    *   Documented key endpoints needed for our project
    *   Outlined best practices for API integration
    *   Established implementation plan for card data enrichment
*   Implemented Scryfall API integration with card enrichment functionality:
    *   Created a comprehensive Scryfall service with rate limiting, caching, and error handling.
    *   Added `/collection/cards/<id>/enrich` endpoint to enrich individual cards with Scryfall data.
    *   Added `/collection/enrich-all` endpoint to enrich all cards in the collection.
    *   Implemented background processing for bulk enrichment operations.
    *   Created test script to validate the enrichment functionality.
*   Created a `README.md` with project overview and setup instructions.
*   Created `.vscode/settings.json` for workspace-specific editor settings.
*   Created this `docs/project-status.md` file.

## Next Steps (Immediate)

*   Begin exploring card text analysis techniques for extracting keywords and abilities.
*   Enhance error handling and data validation in the API.
*   Add more advanced collection management features (filtering, sorting, pagination).
*   Consider adding authentication/authorization for API access.
*   Implement initial synergy detection based on card text analysis.

