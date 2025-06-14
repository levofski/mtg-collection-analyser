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
from ..models.card_synergy import CardSynergy
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

@collection_bp.route('/analyze-all', methods=['POST'])
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

@collection_bp.route('/cards/<int:card1_id>/synergy/<int:card2_id>', methods=['GET'])
def get_card_synergy_route(card1_id: int, card2_id: int) -> FlaskResponse:
    """
    Get synergy score between two specific cards.
    Checks stored synergies first, calculates on-the-fly if not found.
    """
    card1 = CardInfo.query.get(card1_id)
    card2 = CardInfo.query.get(card2_id)

    if not card1:
        return jsonify({"error": f"Card with ID {card1_id} not found"}), 404
    if not card2:
        return jsonify({"error": f"Card with ID {card2_id} not found"}), 404

    # First, try to get stored synergy
    stored_synergy = CardSynergy.get_synergy(card1_id, card2_id)

    if stored_synergy:
        # Use stored synergy data
        synergy_result = stored_synergy.synergy_breakdown
        source = "stored"
    else:
        # Calculate on-the-fly if not stored
        from src.services.text_analysis import calculate_synergy_score
        synergy_result = calculate_synergy_score(
            card1.extracted_data or {},
            card2.extracted_data or {}
        )
        source = "calculated"

    response = {
        "card1": {
            "id": card1.id,
            "name": card1.name,
            "type_line": card1.type_line
        },
        "card2": {
            "id": card2.id,
            "name": card2.name,
            "type_line": card2.type_line
        },
        "synergy": synergy_result,
        "source": source
    }

    return jsonify(response), 200

@collection_bp.route('/cards/<int:card_id>/synergistic-partners', methods=['GET'])
def find_synergistic_partners_route(card_id: int) -> FlaskResponse:
    """
    Find cards that synergize well with the specified card.
    Uses stored synergies for fast querying when available.
    """
    target_card = CardInfo.query.get(card_id)
    if not target_card:
        return jsonify({"error": f"Card with ID {card_id} not found"}), 404

    # Get query parameters
    min_score = float(request.args.get('min_score', 10.0))
    limit = int(request.args.get('limit', 20))
    use_stored_only = request.args.get('stored_only', 'true').lower() == 'true'

    synergistic_cards = []

    if use_stored_only:
        # Use stored synergies for fast querying
        stored_synergies = CardSynergy.get_synergies_for_card(
            card_id,
            min_score=min_score,
            limit=limit
        )

        for synergy in stored_synergies:
            partner_card = synergy.get_partner_card(card_id)
            if partner_card:
                synergistic_cards.append({
                    "card": {
                        "id": partner_card.id,
                        "name": partner_card.name,
                        "type_line": partner_card.type_line
                    },
                    "synergy_score": synergy.total_score,
                    "synergy_details": synergy.synergy_breakdown or {
                        "total_score": synergy.total_score,
                        "tribal_score": synergy.tribal_score,
                        "color_score": synergy.color_score,
                        "keyword_score": synergy.keyword_score,
                        "archetype_score": synergy.archetype_score,
                        "combo_score": synergy.combo_score,
                        "type_score": synergy.type_score,
                        "mana_curve_score": synergy.mana_curve_score,
                        "format_score": synergy.format_score
                    }
                })
        source = "stored"
    else:
        # Calculate on-the-fly (slower but more comprehensive)
        if not target_card.extracted_data:
            return jsonify({"error": "Card has not been analyzed yet"}), 400

        from src.services.text_analysis import calculate_synergy_score

        # Get other analyzed cards
        all_cards = CardInfo.query.filter(
            CardInfo._extracted_data.isnot(None),
            CardInfo.id != card_id
        ).limit(500).all()

        for card in all_cards:
            synergy_result = calculate_synergy_score(
                target_card.extracted_data,
                card.extracted_data or {}
            )

            score = synergy_result.get('total_score', 0)
            if score >= min_score:
                synergistic_cards.append({
                    "card": {
                        "id": card.id,
                        "name": card.name,
                        "type_line": card.type_line
                    },
                    "synergy_score": score,
                    "synergy_details": synergy_result
                })

        # Sort by score (highest first)
        synergistic_cards.sort(key=lambda x: x["synergy_score"], reverse=True)
        synergistic_cards = synergistic_cards[:limit]
        source = "calculated"

    response = {
        "target_card": {
            "id": target_card.id,
            "name": target_card.name,
            "type_line": target_card.type_line
        },
        "synergistic_partners": synergistic_cards,
        "total_found": len(synergistic_cards),
        "parameters": {
            "min_score": min_score,
            "limit": limit,
            "stored_only": use_stored_only
        },
        "source": source
    }

    return jsonify(response), 200

@collection_bp.route('/synergies/top', methods=['GET'])
def get_top_synergies_route() -> FlaskResponse:
    """
    Get the top synergies in the collection.
    """
    # Get query parameters
    limit = int(request.args.get('limit', 50))
    min_score = float(request.args.get('min_score', 10.0))
    synergy_type = request.args.get('type')  # tribal, combo, archetype, etc.

    if synergy_type == 'tribal':
        synergies = CardSynergy.get_tribal_synergies(min_score=min_score)
    elif synergy_type == 'combo':
        synergies = CardSynergy.get_combo_synergies(min_score=min_score)
    elif synergy_type == 'archetype':
        synergies = CardSynergy.get_archetype_synergies(min_score=min_score)
    else:
        synergies = CardSynergy.get_top_synergies(limit=limit, min_score=min_score)

    # Limit results
    synergies = synergies[:limit]

    # Format response
    synergy_list = []
    for synergy in synergies:
        synergy_list.append({
            "id": synergy.id,
            "card1": {
                "id": synergy.card1.id,
                "name": synergy.card1.name,
                "type_line": synergy.card1.type_line
            },
            "card2": {
                "id": synergy.card2.id,
                "name": synergy.card2.name,
                "type_line": synergy.card2.type_line
            },
            "total_score": synergy.total_score,
            "tribal_score": synergy.tribal_score,
            "color_score": synergy.color_score,
            "keyword_score": synergy.keyword_score,
            "archetype_score": synergy.archetype_score,
            "combo_score": synergy.combo_score,
            "type_score": synergy.type_score,
            "mana_curve_score": synergy.mana_curve_score,
            "format_score": synergy.format_score,
            "breakdown": synergy.synergy_breakdown
        })

    response = {
        "synergies": synergy_list,
        "count": len(synergy_list),
        "parameters": {
            "limit": limit,
            "min_score": min_score,
            "type": synergy_type
        }
    }

    return jsonify(response), 200

@collection_bp.route('/synergies/stats', methods=['GET'])
def get_synergy_stats_route() -> FlaskResponse:
    """
    Get statistics about the synergy graph.
    """
    total_synergies = CardSynergy.query.count()

    if total_synergies == 0:
        return jsonify({
            "total_synergies": 0,
            "message": "No synergies computed yet. Run the synergy computation script."
        }), 200

    # Score distribution
    high_synergy = CardSynergy.query.filter(CardSynergy.total_score >= 30).count()
    good_synergy = CardSynergy.query.filter(
        CardSynergy.total_score >= 15,
        CardSynergy.total_score < 30
    ).count()
    moderate_synergy = CardSynergy.query.filter(
        CardSynergy.total_score >= 5,
        CardSynergy.total_score < 15
    ).count()

    # Top synergy types
    top_tribal = CardSynergy.query.filter(CardSynergy.tribal_score >= 10).count()
    top_combo = CardSynergy.query.filter(CardSynergy.combo_score >= 10).count()
    top_archetype = CardSynergy.query.filter(CardSynergy.archetype_score >= 10).count()

    # Top synergy
    best_synergy = CardSynergy.query.order_by(CardSynergy.total_score.desc()).first()

    response = {
        "total_synergies": total_synergies,
        "score_distribution": {
            "high_synergy_30_plus": high_synergy,
            "good_synergy_15_to_30": good_synergy,
            "moderate_synergy_5_to_15": moderate_synergy
        },
        "synergy_types": {
            "strong_tribal": top_tribal,
            "strong_combo": top_combo,
            "strong_archetype": top_archetype
        },
        "best_synergy": {
            "score": best_synergy.total_score,
            "card1": {
                "id": best_synergy.card1.id,
                "name": best_synergy.card1.name
            },
            "card2": {
                "id": best_synergy.card2.id,
                "name": best_synergy.card2.name
            }
        } if best_synergy else None
    }

    return jsonify(response), 200

@collection_bp.route('/synergies/search', methods=['GET'])
def search_synergies_route() -> FlaskResponse:
    """
    Search for synergies by card name or criteria.
    """
    # Get query parameters
    card_name = request.args.get('card_name', '').strip()
    min_score = float(request.args.get('min_score', 10.0))
    limit = int(request.args.get('limit', 20))
    synergy_type = request.args.get('type')  # tribal, combo, archetype

    if not card_name:
        return jsonify({"error": "card_name parameter is required"}), 400

    # Find cards matching the name
    matching_cards = CardInfo.query.filter(
        CardInfo.name.ilike(f"%{card_name}%")
    ).all()

    if not matching_cards:
        return jsonify({"error": f"No cards found matching '{card_name}'"}), 404

    all_synergies = []

    # Get synergies for all matching cards
    for card in matching_cards:
        synergies = CardSynergy.get_synergies_for_card(
            card.id,
            min_score=min_score,
            limit=limit
        )

        for synergy in synergies:
            # Filter by synergy type if specified
            if synergy_type:
                if synergy_type == 'tribal' and synergy.tribal_score < 10:
                    continue
                elif synergy_type == 'combo' and synergy.combo_score < 10:
                    continue
                elif synergy_type == 'archetype' and synergy.archetype_score < 10:
                    continue

            partner_card = synergy.get_partner_card(card.id)
            if partner_card:
                all_synergies.append({
                    "synergy_id": synergy.id,
                    "total_score": synergy.total_score,
                    "source_card": {
                        "id": card.id,
                        "name": card.name,
                        "type_line": card.type_line
                    },
                    "partner_card": {
                        "id": partner_card.id,
                        "name": partner_card.name,
                        "type_line": partner_card.type_line
                    },
                    "synergy_scores": {
                        "tribal": synergy.tribal_score,
                        "color": synergy.color_score,
                        "keyword": synergy.keyword_score,
                        "archetype": synergy.archetype_score,
                        "combo": synergy.combo_score,
                        "type": synergy.type_score,
                        "mana_curve": synergy.mana_curve_score,
                        "format": synergy.format_score
                    },
                    "breakdown": synergy.synergy_breakdown
                })

    # Sort by score and limit
    all_synergies.sort(key=lambda x: x["total_score"], reverse=True)
    all_synergies = all_synergies[:limit]

    response = {
        "search_term": card_name,
        "matching_cards": [{"id": c.id, "name": c.name} for c in matching_cards],
        "synergies": all_synergies,
        "count": len(all_synergies),
        "parameters": {
            "min_score": min_score,
            "limit": limit,
            "type": synergy_type
        }
    }

    return jsonify(response), 200
