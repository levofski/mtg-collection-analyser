"""
Text analysis service for Magic: The Gathering card oracle text.

This module provides functionality to extract keywords, abilities, and other
relevant information from card oracle text using NLP techniques.
"""
import re
import logging
from typing import Dict, List, Set, Any

import spacy
from spacy.tokens import Doc
from spacy.language import Language

# Configure logging
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded spaCy model: en_core_web_sm")
except IOError:
    logger.warning("Failed to load spaCy model. Text analysis features will be limited.")
    nlp = None

# MTG-specific patterns and keywords
MTG_KEYWORDS = {
    "abilities": [
        "flying", "first strike", "double strike", "deathtouch", "haste",
        "hexproof", "indestructible", "lifelink", "menace", "protection",
        "reach", "trample", "vigilance", "ward", "defender", "flash",
        "prowess", "afterlife", "mentor", "riot", "adapt", "annihilator",
        "cascade", "cipher", "convoke", "crew", "delve", "emerge", "enrage",
        "evoke", "exalted", "exploit", "extort", "flanking", "graft",
        "improvise", "infect", "kicker", "madness", "modular", "morph",
        "mutate", "ninjutsu", "offering", "outlast", "overload", "persist",
        "proliferate", "provoke", "prowl", "raid", "replicate", "recover",
        "reinforce", "retrace", "scavenge", "shadow", "soulbond", "support",
        "surge", "suspend", "totem armor", "undying", "unearth", "unleash",
        "vanishing", "wither", "phasing", "banding"
    ],

    "card_types": [
        "artifact", "creature", "enchantment", "instant", "land",
        "planeswalker", "sorcery", "tribal", "battle", "conspiracy",
        "dungeon", "phenomenon", "plane", "scheme", "vanguard"
    ],

    "mana_symbols": [
        "white", "blue", "black", "red", "green",
        "colorless", "generic", "hybrid", "phyrexian"
    ],

    "zones": [
        "battlefield", "library", "graveyard", "hand", "stack", "exile",
        "command", "ante", "sideboard"
    ],

    "actions": [
        "cast", "activate", "counter", "sacrifice", "discard", "exile",
        "destroy", "tap", "untap", "attach", "unattach", "equip", "unequip",
        "transform", "play", "reveal", "search", "shuffle", "scry", "fateseal",
        "proliferate", "draw", "mill"
    ],

    "counters": [
        "+1/+1", "-1/-1", "loyalty", "poison", "age", "aim", "arrow", "arrowhead",
        "awakening", "blood", "brick", "charge", "coin", "credit", "crystal",
        "cube", "currency", "death", "delay", "depletion", "despair", "devotion"
    ]
}

# Combine all keywords into a single set for faster lookups
ALL_MTG_KEYWORDS = set()
for category in MTG_KEYWORDS.values():
    ALL_MTG_KEYWORDS.update(category)

def analyze_card_text(oracle_text: str) -> Dict[str, Any]:
    """
    Analyze card oracle text to extract keywords, abilities, and other relevant information.

    Args:
        oracle_text: The oracle text of the card to analyze.

    Returns:
        A dictionary containing extracted information such as:
        - keywords: List of MTG keywords found in the text
        - actions: List of game actions referenced in the text
        - zones: List of game zones referenced in the text
        - mana_references: List of mana symbols/colors referenced
        - noun_phrases: List of important noun phrases
        - named_entities: List of named entities (e.g., creature types)
    """
    if not oracle_text or not nlp:
        return {
            "keywords": [],
            "actions": [],
            "zones": [],
            "mana_references": [],
            "noun_phrases": [],
            "named_entities": []
        }

    # Process the text with spaCy
    doc = nlp(oracle_text)

    # Extract information
    result = {
        "keywords": extract_mtg_keywords(doc, "abilities"),
        "actions": extract_mtg_keywords(doc, "actions"),
        "zones": extract_mtg_keywords(doc, "zones"),
        "mana_references": extract_mtg_keywords(doc, "mana_symbols"),
        "noun_phrases": extract_noun_phrases(doc),
        "named_entities": extract_named_entities(doc),
        "raw_tokens": [token.text for token in doc if not token.is_punct and not token.is_space]
    }

    return result

def extract_mtg_keywords(doc: Doc, category: str) -> List[str]:
    """
    Extract MTG keywords of a specific category from the document.

    Args:
        doc: spaCy Doc object
        category: Category of keywords to extract from MTG_KEYWORDS

    Returns:
        List of found keywords in the text
    """
    keywords = set()
    text_lower = doc.text.lower()

    # Direct lookup for multi-word keywords
    for keyword in MTG_KEYWORDS.get(category, []):
        if keyword in text_lower:
            keywords.add(keyword)

    # Token-based lookup for single-word keywords
    for token in doc:
        if token.text.lower() in MTG_KEYWORDS.get(category, []):
            keywords.add(token.text.lower())

    return sorted(list(keywords))

def extract_noun_phrases(doc: Doc) -> List[str]:
    """
    Extract important noun phrases from the document.

    Args:
        doc: spaCy Doc object

    Returns:
        List of noun phrases
    """
    return [chunk.text for chunk in doc.noun_chunks]

def extract_named_entities(doc: Doc) -> List[Dict[str, str]]:
    """
    Extract named entities from the document.

    Args:
        doc: spaCy Doc object

    Returns:
        List of dictionaries containing entity text and type
    """
    return [{"text": ent.text, "type": ent.label_} for ent in doc.ents]

def find_synergy_candidates(card_text: str, collection_keywords: Set[str]) -> List[str]:
    """
    Find potential synergies between a card and collection keywords.

    Args:
        card_text: The oracle text of the card to analyze
        collection_keywords: Set of keywords present in the collection

    Returns:
        List of keywords from the collection that might synergize with this card
    """
    if not card_text or not nlp:
        return []

    # Process the text with spaCy
    doc = nlp(card_text)

    # Find all matching keywords
    matches = []
    for keyword in collection_keywords:
        if keyword.lower() in card_text.lower():
            matches.append(keyword)

    return matches
