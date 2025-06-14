"""
Card analysis service for processing and analyzing MTG cards.

This module integrates with the text analysis service to extract and store
information from card oracle text.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional

from ..database import db
from ..models.card_info import CardInfo
from ..services.text_analysis import analyze_card_text

# Configure logging
logger = logging.getLogger(__name__)

def analyze_card(card_info_id: int) -> Tuple[Optional[CardInfo], str]:
    """
    Analyze a single card's oracle text and update its record with the extracted data.

    Args:
        card_info_id: The ID of the CardInfo record to analyze

    Returns:
        A tuple containing:
        - The updated CardInfo object if found, None otherwise
        - A message describing the result of the operation
    """
    card_info = CardInfo.query.get(card_info_id)
    if not card_info:
        return None, f"Card with ID {card_info_id} not found."

    if not card_info.oracle_text:
        return card_info, "Card has no oracle text to analyze."

    try:
        # Get Scryfall data if available
        scryfall_data = {}

        # Check if card has enriched data from Scryfall
        if hasattr(card_info, 'printings') and card_info.printings.count() > 0:
            # Get the first printing to check for Scryfall data
            printing = card_info.printings.first()
            if printing and hasattr(printing, 'scryfall_id'):
                # Build Scryfall data from card_info fields
                scryfall_data = {
                    "oracle_text": card_info.oracle_text,
                    "mana_cost": card_info.mana_cost,
                    "cmc": card_info.cmc,
                    "type_line": card_info.type_line,
                    # Add more fields as they become available in the database
                }

        # Analyze the card text with additional card data
        analysis_result = analyze_card_text(card_info.oracle_text, scryfall_data)

        # Extract keywords from the analysis result
        keywords = analysis_result.get("keywords", [])

        # Update the card info record
        card_info.keywords = keywords
        card_info.extracted_data = analysis_result

        # Save to database
        db.session.commit()
        return card_info, "Card analyzed successfully."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error analyzing card {card_info_id}: {str(e)}")
        return card_info, f"Error analyzing card: {str(e)}"

def analyze_all_cards() -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Analyze all cards' oracle text and update their records with extracted data.
    Commits changes to the database after each successful card analysis.

    Returns:
        A tuple containing:
        - Number of successfully analyzed cards
        - Total number of cards processed
        - List of errors that occurred during analysis
    """
    card_infos = CardInfo.query.all()
    total_cards = len(card_infos)
    successful = 0
    errors = []

    for card_info in card_infos:
        # Skip cards without oracle text
        if not card_info.oracle_text:
            continue

        try:
            # Analyze the card text
            analysis_result = analyze_card_text(card_info.oracle_text)

            # Extract keywords from the analysis result
            keywords = analysis_result.get("keywords", [])

            # Update the card info record
            card_info.keywords = keywords
            card_info.extracted_data = analysis_result

            # Commit changes immediately
            try:
                db.session.commit()
                successful += 1
                logger.info(f"Successfully analyzed card {card_info.id} ({card_info.name})")
            except Exception as db_err:
                db.session.rollback()
                error_msg = f"Database error when saving analysis for card {card_info.id}: {str(db_err)}"
                errors.append({
                    "card_id": card_info.id,
                    "card_name": card_info.name,
                    "error": error_msg
                })
                logger.error(error_msg)

        except Exception as e:
            # Rollback any pending changes for this card
            db.session.rollback()
            errors.append({
                "card_id": card_info.id,
                "card_name": card_info.name,
                "error": str(e)
            })
            logger.error(f"Error analyzing card {card_info.id} ({card_info.name}): {str(e)}")

    return successful, total_cards, errors
