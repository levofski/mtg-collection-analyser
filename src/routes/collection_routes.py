\
from flask import Blueprint, request, jsonify
from flask.wrappers import Response as FlaskResponse
from typing import List, Dict, Any
from werkzeug.datastructures import FileStorage

from ..services.csv_importer import process_csv_data
from ..store.card_store import add_cards_to_collection, get_all_cards, clear_collection
from ..models.card import Card

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
            message, valid_cards, validation_errors, status_code = process_csv_data(file.stream)

            response_data = {"message": message}
            if valid_cards is not None:
                add_cards_to_collection(valid_cards) # Store the valid cards
                response_data["cards_added_to_collection"] = len(valid_cards)
                # To see the actual card data in the response (can be verbose for large files):
                # response_data["validated_cards_data"] = [card.to_dict() for card in valid_cards]

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
    all_cards: List[Card] = get_all_cards()
    # Convert Card objects to dictionaries for JSON serialization
    cards_as_dicts: List[Dict[str, Any]] = [card.to_dict() for card in all_cards]
    return jsonify({"cards": cards_as_dicts, "count": len(all_cards)}), 200

@collection_bp.route('/clear', methods=['POST']) # Using POST for a state-changing operation
def clear_collection_route() -> FlaskResponse:
    """
    Clears all cards from the collection.
    """
    clear_collection()
    return jsonify({"message": "Collection cleared successfully."}), 200
