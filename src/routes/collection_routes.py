from flask import Blueprint, request, jsonify
from flask.wrappers import Response as FlaskResponse
from typing import List, Dict, Any
from werkzeug.datastructures import FileStorage

from ..services.csv_importer import process_csv_data
from ..services.card_analysis import analyze_card, analyze_all_cards
from ..store.card_store import (
    add_cards_to_collection, get_all_cards, clear_collection,
    get_card_by_id, update_card, delete_card,
    enrich_card_with_scryfall_data, enrich_all_cards
)
from ..models.card_printing import CardPrinting
from ..models.card_info import CardInfo
from ..store.card_info_store import get_all_cards_info, get_card_info_by_id

collection_bp = Blueprint('collection_bp', __name__, url_prefix='/collection')

@collection_bp.route('/import_csv', methods=['POST'])
def import_csv_route() -> FlaskResponse:
    """
    Imports a CSV file containing card collection data.
    The CSV file is expected to be in the request's files.
    """
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request", "validation_errors": []}), 400

    file: FileStorage = request.files['file'] # type: ignore

    if not file.filename: # Handles case where file part exists but no file selected
        return jsonify({"message": "No selected file", "validation_errors": []}), 400

    if file.filename.endswith('.csv'):
        try:
            # file.stream is IO[bytes]
            message, valid_printings, validation_errors, status_code = process_csv_data(file.stream)

            response_data = {"message": message}
            if valid_printings is not None:
                add_cards_to_collection(valid_printings) # Store the valid cards
                response_data["cards_added_to_collection"] = len(valid_printings)
                # To see the actual card data in the response (can be verbose for large files):
                # response_data["validated_cards_data"] = [card.to_dict() for card in valid_printings]

            if validation_errors is not None:
                response_data["validation_errors"] = validation_errors

            return jsonify(response_data), status_code

        except Exception as e:
            # General exception handling for unexpected errors in the route
            # This should ideally be rare if process_csv_data handles its errors well.
            return jsonify({"message": f"An unexpected error occurred: {str(e)}", "validation_errors": []}), 500
    else:
        return jsonify({"message": "Invalid file type, please upload a CSV file.", "validation_errors": []}), 400

@collection_bp.route('/cards', methods=['GET'])
def get_collection_cards_route() -> FlaskResponse:
    """
    Retrieves all cards currently in the collection.
    """
    all_printings: List[CardPrinting] = get_all_cards()
    # Convert CardPrinting objects to dictionaries for JSON serialization
    printings_as_dicts: List[Dict[str, Any]] = []

    for printing in all_printings:
        # Create a combined dict with both printing and card info data
        printing_dict = printing.to_dict()
        # Add card info data
        card_info_dict = printing.card_info.to_dict() if printing.card_info else {}
        # Remove ID fields to avoid confusion
        if 'id' in card_info_dict:
            card_info_dict['card_info_id'] = card_info_dict.pop('id')

        # Merge the dicts
        combined_dict = {**printing_dict, **card_info_dict}
        printings_as_dicts.append(combined_dict)

    return jsonify({"cards": printings_as_dicts, "count": len(all_printings)}), 200

@collection_bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card_by_id_route(card_id: int) -> FlaskResponse:
    """
    Retrieves a specific card printing by its ID.

    Args:
        card_id: The ID of the card printing to retrieve.
    """
    card_printing = get_card_by_id(card_id)
    if card_printing:
        # Create a combined dict with both printing and card info data
        printing_dict = card_printing.to_dict()
        # Add card info data
        card_info_dict = card_printing.card_info.to_dict() if card_printing.card_info else {}
        # Remove ID fields to avoid confusion
        if 'id' in card_info_dict:
            card_info_dict['card_info_id'] = card_info_dict.pop('id')

        # Merge the dicts
        combined_dict = {**printing_dict, **card_info_dict}
        return jsonify(combined_dict), 200
    return jsonify({"message": f"Card with ID {card_id} not found."}), 404

@collection_bp.route('/cards/<int:card_id>', methods=['PUT'])
def update_card_route(card_id: int) -> FlaskResponse:
    """
    Updates a specific card printing by its ID.

    Args:
        card_id: The ID of the card printing to update.
    """
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json()

    # Attempt to update the card
    updated_card = update_card(card_id, data)

    if updated_card:
        # Create a combined dict with both printing and card info data
        printing_dict = updated_card.to_dict()
        # Add card info data
        card_info_dict = updated_card.card_info.to_dict() if updated_card.card_info else {}
        # Remove ID fields to avoid confusion
        if 'id' in card_info_dict:
            card_info_dict['card_info_id'] = card_info_dict.pop('id')

        # Merge the dicts
        combined_dict = {**printing_dict, **card_info_dict}

        return jsonify({
            "message": f"Card with ID {card_id} updated successfully.",
            "card": combined_dict
        }), 200

    return jsonify({"message": f"Card with ID {card_id} not found."}), 404

@collection_bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card_route(card_id: int) -> FlaskResponse:
    """
    Deletes a specific card printing by its ID.

    Args:
        card_id: The ID of the card printing to delete.
    """
    success = delete_card(card_id)

    if success:
        return jsonify({"message": f"Card with ID {card_id} deleted successfully."}), 200

    return jsonify({"message": f"Card with ID {card_id} not found."}), 404

@collection_bp.route('', methods=['DELETE'])
def clear_collection_route() -> FlaskResponse:
    """
    Clears all card printings from the collection.
    Following REST principles, this uses DELETE method on the collection resource.
    """
    clear_collection()
    return jsonify({"message": "Collection cleared successfully."}), 200

@collection_bp.route('/cards/<int:card_id>/enrich', methods=['POST'])
def enrich_card_route(card_id: int) -> FlaskResponse:
    """
    Enriches a specific card printing and its card info with data from the Scryfall API.

    Args:
        card_id: The ID of the card printing to enrich.
    """
    enriched_card, message = enrich_card_with_scryfall_data(card_id)

    if enriched_card:
        # Create a combined dict with both printing and card info data
        printing_dict = enriched_card.to_dict()
        # Add card info data
        card_info_dict = enriched_card.card_info.to_dict() if enriched_card.card_info else {}
        # Remove ID fields to avoid confusion
        if 'id' in card_info_dict:
            card_info_dict['card_info_id'] = card_info_dict.pop('id')

        # Merge the dicts
        combined_dict = {**printing_dict, **card_info_dict}

        return jsonify({
            "message": message,
            "card": combined_dict
        }), 200

    return jsonify({"message": message}), 404

@collection_bp.route('/enrich-all', methods=['POST'])
def enrich_all_cards_route() -> FlaskResponse:
    """
    Enriches all cards in the collection with data from the Scryfall API.
    """
    successful, total, errors = enrich_all_cards()

    response = {
        "message": f"Enriched {successful} out of {total} cards.",
        "success_count": successful,
        "total_count": total
    }

    if errors:
        response["errors"] = errors

    status_code = 200 if successful == total else 207  # 207 Multi-Status
    return jsonify(response), status_code

@collection_bp.route('/card-infos', methods=['GET'])
def get_all_card_infos_route() -> FlaskResponse:
    """
    Retrieves all unique card infos (oracle cards).
    """
    all_card_infos: List[CardInfo] = get_all_cards_info()
    # Convert CardInfo objects to dictionaries for JSON serialization
    card_infos_as_dicts: List[Dict[str, Any]] = [card_info.to_dict() for card_info in all_card_infos]
    return jsonify({"card_infos": card_infos_as_dicts, "count": len(all_card_infos)}), 200

@collection_bp.route('/card-infos/<int:card_info_id>', methods=['GET'])
def get_card_info_route(card_info_id: int) -> FlaskResponse:
    """
    Retrieves a specific card info by its ID.

    Args:
        card_info_id: The ID of the card info to retrieve.
    """
    card_info = get_card_info_by_id(card_info_id)
    if card_info:
        return jsonify(card_info.to_dict()), 200
    return jsonify({"message": f"Card info with ID {card_info_id} not found."}), 404

@collection_bp.route('/card-infos/<int:card_info_id>/analyze', methods=['POST'])
def analyze_card_info_route(card_info_id: int) -> FlaskResponse:
    """
    Analyzes a specific card's oracle text and extracts keywords and other data.

    Args:
        card_info_id: The ID of the card info to analyze.
    """
    analyzed_card, message = analyze_card(card_info_id)

    if analyzed_card:
        return jsonify({
            "message": message,
            "card_info": analyzed_card.to_dict()
        }), 200

    return jsonify({"message": message}), 404

@collection_bp.route('/card-infos/analyze-all', methods=['POST'])
def analyze_all_card_infos_route() -> FlaskResponse:
    """
    Analyzes all cards in the collection using NLP techniques.
    """
    successful, total, errors = analyze_all_cards()

    response = {
        "message": f"Analyzed {successful} out of {total} cards.",
        "success_count": successful,
        "total_count": total
    }

    if errors:
        response["errors"] = errors

    status_code = 200 if successful == total else 207  # 207 Multi-Status
    return jsonify(response), status_code
