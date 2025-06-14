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
        "vanishing", "wither", "phasing", "banding", "buyback", "cumulative upkeep",
        "echo", "fading", "fear", "flashback", "horsemanship", "landwalk",
        "rampage", "shroud", "storm", "threshold", "bloodthirst", "living weapon",
        "battle cry", "soulshift", "splice", "ninjutsu", "bushido", "channel",
        "epic", "absorb", "afflict", "ascend", "assist", "aura swap", "bestow",
        "bloodrush", "boast", "champion", "changeling", "clash", "conspire",
        "cycling", "dash", "domain", "dredge", "embalm", "encore", "escape",
        "eternalize", "evoke", "explore", "fabricate", "forecast", "fuse",
        "graft", "haunt", "hideaway", "imprint", "impulse", "investigate",
        "jump-start", "learn", "level up", "miracle", "monstrosity", "multikicker",
        "outlast", "partner", "populate", "rebound", "recover", "regenerate",
        "reinforce", "renown", "replicate", "retrace", "spectacle", "split second",
        "strive", "surge", "surveil", "training", "transform", "tribute",
        "unleash", "unearth", "vigilance", "voyage", "hexproof from"
    ],

    "card_types": [
        "artifact", "creature", "enchantment", "instant", "land",
        "planeswalker", "sorcery", "tribal", "battle", "conspiracy",
        "dungeon", "phenomenon", "plane", "scheme", "vanguard", "legendary",
        "basic", "snow", "world"
    ],

    "creature_types": [
        "human", "elf", "goblin", "dragon", "angel", "demon", "zombie", "spirit",
        "beast", "bird", "cat", "dog", "elephant", "fish", "insect", "snake",
        "spider", "wolf", "warrior", "wizard", "cleric", "rogue", "knight",
        "soldier", "scout", "berserker", "barbarian", "shaman", "druid", "monk",
        "artificer", "advisor", "assassin", "archer", "rebel", "mercenary",
        "pirate", "pilot", "ninja", "samurai", "vampire", "werewolf", "zombie",
        "minotaur", "centaur", "giant", "dwarf", "orc", "troll", "ogre",
        "cyclops", "hydra", "kraken", "leviathan", "octopus", "salamander",
        "merfolk", "triton", "siren", "naga", "lamia", "sphinx", "pegasus",
        "unicorn", "hippogriff", "griffin", "phoenix", "roc", "thrull", "orgg",
        "atog", "aurochs", "avatar", "badger", "basilisk", "bat", "bear",
        "boar", "camel", "caribou", "construct", "cow", "crab", "crocodile",
        "deer", "devil", "dinosaur", "djinn", "dreadnought", "drone", "egg",
        "elemental", "elk", "eye", "faerie", "ferret", "fox", "frog", "fungus",
        "gargoyle", "germ", "gnome", "goat", "golem", "gorgon", "graveborn",
        "hag", "harpy", "hellion", "hippo", "homunculus", "horror", "horse",
        "hound", "illusion", "imp", "incarnation", "kavu", "kirin", "kithkin",
        "kobold", "kor", "lammasu", "lhurgoyf", "licid", "lizard", "manticore",
        "masticore", "myr", "nautilus", "nephilim", "nightmare", "nightstalker",
        "ooze", "ox", "oyster", "pegasus", "pentavite", "pest", "phelddagrif",
        "plant", "prism", "rabbit", "rat", "rhino", "rigger", "sable", "sand",
        "saproling", "scarecrow", "scorpion", "serf", "shade", "shapeshifter",
        "shark", "sheep", "skeleton", "slith", "sliver", "slug", "spawn",
        "specter", "spellshaper", "starfish", "surrakar", "tetravite", "thalakos",
        "thopter", "treefolk", "turtle", "vedalken", "volver", "wall", "whale",
        "wombat", "wurm", "yeti", "zubera"
    ],

    "planeswalker_types": [
        "ajani", "aminatou", "angrath", "arlinn", "ashiok", "basri", "bolas",
        "chandra", "dack", "daretti", "davriel", "domri", "dovin", "elspeth",
        "estrid", "freyalise", "garruk", "gideon", "huatli", "jace", "jaya",
        "karn", "kasmina", "kaya", "kiora", "koth", "liliana", "lukka",
        "nahiri", "narset", "nissa", "nixilis", "oko", "ral", "rowan",
        "saheeli", "samut", "sarkhan", "sorin", "tamiyo", "teferi", "tezzeret",
        "tibalt", "ugin", "venser", "vivien", "vraska", "will", "windgrace",
        "wrenn", "xenagos", "yanling"
    ],

    "artifact_subtypes": [
        "equipment", "vehicle", "fortification", "clue", "food", "treasure",
        "blood", "gold", "contraption", "attraction"
    ],

    "enchantment_subtypes": [
        "aura", "cartouche", "curse", "saga", "shrine", "class", "background",
        "case", "role"
    ],

    "mana_symbols": [
        "white", "blue", "black", "red", "green", "colorless", "generic",
        "hybrid", "phyrexian", "monocolored", "multicolored", "devotion"
    ],

    "zones": [
        "battlefield", "library", "graveyard", "hand", "stack", "exile",
        "command", "ante", "sideboard", "outside the game"
    ],

    "actions": [
        "cast", "activate", "counter", "sacrifice", "discard", "exile",
        "destroy", "tap", "untap", "attach", "unattach", "equip", "unequip",
        "transform", "play", "reveal", "search", "shuffle", "scry", "fateseal",
        "proliferate", "draw", "mill", "surveil", "investigate", "explore",
        "adapt", "amass", "populate", "populate", "manifest", "morph", "megamorph",
        "return", "bounce", "flicker", "blink", "reanimate", "recur", "tutor",
        "fetch", "copy", "clone", "steal", "gain control", "exchange", "swap",
        "double", "prevent", "redirect", "regenerate", "indestructible",
        "hexproof", "shroud", "protection", "unblockable", "vigilance", "haste",
        "enters", "leaves", "dies", "attacks", "blocks", "deals damage",
        "loses life", "gains life", "pays", "spends", "costs", "reduces",
        "increases", "additional", "extra", "first", "upkeep", "main phase",
        "combat", "end step", "cleanup", "beginning", "end", "during", "until"
    ],

    "counters": [
        "+1/+1", "-1/-1", "loyalty", "poison", "energy", "experience", "age",
        "aim", "arrow", "arrowhead", "awakening", "blood", "bounty", "bribery",
        "brick", "charge", "coin", "credit", "crystal", "cube", "currency",
        "death", "delay", "depletion", "despair", "devotion", "divinity",
        "doom", "dream", "echo", "fade", "fate", "feather", "filibuster",
        "flame", "flood", "funk", "fuse", "growth", "hatchling", "healing",
        "hoofprint", "hour", "hunger", "ice", "incarnation", "intervention",
        "isolation", "ki", "level", "lore", "luck", "magnet", "manifestation",
        "matrix", "mine", "mining", "muster", "net", "omen", "ore", "page",
        "pain", "paralyzation", "petal", "petrification", "pin", "plague",
        "polyp", "pressure", "prey", "pupa", "quest", "rust", "scream",
        "shell", "shield", "shred", "sleep", "sleight", "slime", "spore",
        "storage", "strife", "study", "theft", "thorn", "tide", "time",
        "tower", "training", "trap", "treasure", "unity", "velocity",
        "verse", "vitality", "wage", "winch", "wind", "wish"
    ],

    "power_toughness_patterns": [
        "x/x", "*/x", "x/*", "*/*", "x/1", "1/x", "x/2", "2/x", "0/1", "1/1",
        "2/2", "3/3", "4/4", "5/5", "6/6", "7/7", "8/8", "9/9", "10/10"
    ],

    "format_legalities": [
        "standard", "pioneer", "modern", "legacy", "vintage", "commander",
        "historic", "alchemy", "explorer", "timeless", "brawl", "pauper"
    ]
}

# Combine all keywords into a single set for faster lookups
ALL_MTG_KEYWORDS = set()
for category in MTG_KEYWORDS.values():
    ALL_MTG_KEYWORDS.update(category)

def analyze_card_text(oracle_text: str, card_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze card oracle text and card data to extract comprehensive information for synergy detection.

    Args:
        oracle_text: The oracle text of the card to analyze.
        card_data: Additional card data from Scryfall API (colors, type_line, mana_cost, etc.)

    Returns:
        A dictionary containing extracted information such as:
        - keywords: List of MTG keywords found in the text
        - actions: List of game actions referenced in the text
        - zones: List of game zones referenced in the text
        - mana_references: List of mana symbols/colors referenced
        - creature_types: List of creature types from type line
        - card_types: List of card types from type line
        - colors: List of card colors
        - color_identity: List of color identity
        - mana_cost: Parsed mana cost information
        - power_toughness: Power and toughness information
        - synergy_vectors: Categorized synergy potential vectors
        - noun_phrases: List of important noun phrases
        - named_entities: List of named entities
    """
    if not oracle_text and not card_data:
        return _empty_analysis_result()

    # Process the text with spaCy if available
    doc = nlp(oracle_text) if oracle_text and nlp else None

    # Extract information from oracle text
    text_analysis = {
        "keywords": extract_mtg_keywords(doc, "abilities") if doc else [],
        "actions": extract_mtg_keywords(doc, "actions") if doc else [],
        "zones": extract_mtg_keywords(doc, "zones") if doc else [],
        "mana_references": extract_mtg_keywords(doc, "mana_symbols") if doc else [],
        "counters": extract_mtg_keywords(doc, "counters") if doc else [],
        "noun_phrases": extract_noun_phrases(doc) if doc else [],
        "named_entities": extract_named_entities(doc) if doc else [],
        "raw_tokens": [token.text for token in doc if not token.is_punct and not token.is_space] if doc else []
    }

    # Extract information from card data (Scryfall API data)
    card_analysis = extract_card_data_features(card_data) if card_data else {}

    # Combine text and card data analysis
    result = {**text_analysis, **card_analysis}

    # Generate synergy vectors for improved matching
    result["synergy_vectors"] = generate_synergy_vectors(result)

    return result

def _empty_analysis_result() -> Dict[str, Any]:
    """Return an empty analysis result with all expected keys."""
    return {
        "keywords": [],
        "actions": [],
        "zones": [],
        "mana_references": [],
        "creature_types": [],
        "card_types": [],
        "colors": [],
        "color_identity": [],
        "mana_cost_info": {},
        "power_toughness": {},
        "synergy_vectors": {},
        "counters": [],
        "noun_phrases": [],
        "named_entities": [],
        "raw_tokens": []
    }

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

def calculate_synergy_score(card1_analysis: Dict[str, Any], card2_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a comprehensive synergy score between two analyzed cards.

    Args:
        card1_analysis: Analysis data for the first card
        card2_analysis: Analysis data for the second card

    Returns:
        Dictionary containing synergy score and detailed breakdown
    """
    synergy_breakdown = {
        "total_score": 0,
        "tribal_score": 0,
        "color_score": 0,
        "keyword_score": 0,
        "archetype_score": 0,
        "combo_score": 0,
        "type_score": 0,
        "mana_curve_score": 0,
        "format_score": 0,
        "matches": []
    }

    # Tribal synergies (high weight - very important)
    tribal_score = calculate_tribal_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["tribal_score"] = tribal_score["score"]
    synergy_breakdown["matches"].extend(tribal_score["matches"])

    # Color synergies
    color_score = calculate_color_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["color_score"] = color_score["score"]
    synergy_breakdown["matches"].extend(color_score["matches"])

    # Keyword synergies
    keyword_score = calculate_keyword_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["keyword_score"] = keyword_score["score"]
    synergy_breakdown["matches"].extend(keyword_score["matches"])

    # Archetype synergies
    archetype_score = calculate_archetype_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["archetype_score"] = archetype_score["score"]
    synergy_breakdown["matches"].extend(archetype_score["matches"])

    # Combo potential synergies
    combo_score = calculate_combo_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["combo_score"] = combo_score["score"]
    synergy_breakdown["matches"].extend(combo_score["matches"])

    # Type synergies
    type_score = calculate_type_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["type_score"] = type_score["score"]
    synergy_breakdown["matches"].extend(type_score["matches"])

    # Mana curve synergies
    mana_score = calculate_mana_curve_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["mana_curve_score"] = mana_score["score"]
    synergy_breakdown["matches"].extend(mana_score["matches"])

    # Format synergies
    format_score = calculate_format_synergy(card1_analysis, card2_analysis)
    synergy_breakdown["format_score"] = format_score["score"]
    synergy_breakdown["matches"].extend(format_score["matches"])

    # Calculate weighted total score
    synergy_breakdown["total_score"] = (
        synergy_breakdown["tribal_score"] * 5.0 +      # Tribal is very important
        synergy_breakdown["archetype_score"] * 4.0 +   # Archetype synergies are crucial
        synergy_breakdown["combo_score"] * 4.0 +       # Combo potential is highly valued
        synergy_breakdown["keyword_score"] * 3.0 +     # Keywords are important
        synergy_breakdown["type_score"] * 2.0 +        # Type synergies matter
        synergy_breakdown["color_score"] * 1.5 +       # Color compatibility
        synergy_breakdown["mana_curve_score"] * 1.0 +  # Mana curve fit
        synergy_breakdown["format_score"] * 0.5        # Format legality is minor
    )

    return synergy_breakdown

def calculate_tribal_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate tribal synergy score between two cards."""
    result = {"score": 0, "matches": []}

    types1 = set(card1.get("creature_types", []))
    types2 = set(card2.get("creature_types", []))

    if not types1 and not types2:
        return result

    shared_types = types1.intersection(types2)

    for shared_type in shared_types:
        result["score"] += 3  # High score for exact tribal matches
        result["matches"].append(f"tribal:{shared_type}")

    # Check if one card cares about creature types the other has
    oracle_text1 = " ".join(card1.get("raw_tokens", [])).lower()
    oracle_text2 = " ".join(card2.get("raw_tokens", [])).lower()

    for creature_type in types1:
        if creature_type in oracle_text2:
            result["score"] += 2
            result["matches"].append(f"tribal_support:{creature_type}")

    for creature_type in types2:
        if creature_type in oracle_text1:
            result["score"] += 2
            result["matches"].append(f"tribal_support:{creature_type}")

    return result

def calculate_color_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate color synergy score between two cards."""
    result = {"score": 0, "matches": []}

    colors1 = set(card1.get("colors", []))
    colors2 = set(card2.get("colors", []))
    identity1 = set(card1.get("color_identity", []))
    identity2 = set(card2.get("color_identity", []))

    # Perfect color match
    if colors1 == colors2 and colors1:
        result["score"] += 2
        result["matches"].append(f"exact_colors:{','.join(sorted(colors1))}")

    # Shared colors
    shared_colors = colors1.intersection(colors2)
    for color in shared_colors:
        result["score"] += 1
        result["matches"].append(f"shared_color:{color}")

    # Compatible color identity
    if identity1.issubset(identity2) or identity2.issubset(identity1):
        result["score"] += 1
        result["matches"].append("compatible_identity")

    # Multicolor synergy
    if len(colors1) > 1 and len(colors2) > 1:
        result["score"] += 1
        result["matches"].append("multicolor_synergy")

    return result

def calculate_keyword_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate keyword synergy score between two cards."""
    result = {"score": 0, "matches": []}

    keywords1 = set(card1.get("keywords", []) + card1.get("scryfall_keywords", []))
    keywords2 = set(card2.get("keywords", []) + card2.get("scryfall_keywords", []))

    shared_keywords = keywords1.intersection(keywords2)

    for keyword in shared_keywords:
        # Some keywords are more synergistic than others
        if keyword in ["flying", "deathtouch", "lifelink", "vigilance", "trample"]:
            result["score"] += 2
        else:
            result["score"] += 1
        result["matches"].append(f"keyword:{keyword}")

    # Check if cards have complementary keywords
    complementary_pairs = [
        ("flying", "reach"),
        ("first strike", "deathtouch"),
        ("lifelink", "vigilance"),
        ("haste", "trample")
    ]

    for kw1, kw2 in complementary_pairs:
        if (kw1 in keywords1 and kw2 in keywords2) or (kw2 in keywords1 and kw1 in keywords2):
            result["score"] += 1
            result["matches"].append(f"complementary:{kw1}+{kw2}")

    return result

def calculate_archetype_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate archetype synergy score between two cards."""
    result = {"score": 0, "matches": []}

    vectors1 = card1.get("synergy_vectors", {})
    vectors2 = card2.get("synergy_vectors", {})

    archetypes1 = set(vectors1.get("archetype", []))
    archetypes2 = set(vectors2.get("archetype", []))

    shared_archetypes = archetypes1.intersection(archetypes2)

    for archetype in shared_archetypes:
        # Different archetypes have different synergy strengths
        archetype_weights = {
            "graveyard": 4,
            "artifacts": 3,
            "spells": 3,
            "tokens": 3,
            "tribal": 4,
            "combo": 5,
            "aggro": 2,
            "control": 2
        }
        weight = archetype_weights.get(archetype, 2)
        result["score"] += weight
        result["matches"].append(f"archetype:{archetype}")

    return result

def calculate_combo_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate combo potential synergy score between two cards."""
    result = {"score": 0, "matches": []}

    vectors1 = card1.get("synergy_vectors", {})
    vectors2 = card2.get("synergy_vectors", {})

    combo1 = set(vectors1.get("combo_potential", []))
    combo2 = set(vectors2.get("combo_potential", []))

    shared_combo = combo1.intersection(combo2)

    for combo_type in shared_combo:
        # High-value combo synergies
        combo_weights = {
            "infinite_mana": 5,
            "infinite_tokens": 5,
            "storm": 4,
            "tutoring": 3,
            "recursion": 3,
            "copy_effects": 3,
            "untap_effects": 2,
            "card_draw": 2,
            "mana_generation": 2
        }
        weight = combo_weights.get(combo_type, 1)
        result["score"] += weight
        result["matches"].append(f"combo:{combo_type}")

    # Check for specific combo patterns
    if "mana_generation" in combo1 and "untap_effects" in combo2:
        result["score"] += 3
        result["matches"].append("combo_pattern:mana+untap")

    if "tutoring" in combo1 and "recursion" in combo2:
        result["score"] += 2
        result["matches"].append("combo_pattern:tutor+recursion")

    return result

def calculate_type_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate type-based synergy score between two cards."""
    result = {"score": 0, "matches": []}

    types1 = set(card1.get("card_types", []))
    types2 = set(card2.get("card_types", []))

    shared_types = types1.intersection(types2)

    for card_type in shared_types:
        result["score"] += 1
        result["matches"].append(f"type:{card_type}")

    # Artifact synergies
    artifact_subtypes1 = set(card1.get("artifact_subtypes", []))
    artifact_subtypes2 = set(card2.get("artifact_subtypes", []))
    shared_artifact_subtypes = artifact_subtypes1.intersection(artifact_subtypes2)

    for subtype in shared_artifact_subtypes:
        result["score"] += 2  # Artifact subtypes are more specific
        result["matches"].append(f"artifact_subtype:{subtype}")

    # Enchantment synergies
    enchant_subtypes1 = set(card1.get("enchantment_subtypes", []))
    enchant_subtypes2 = set(card2.get("enchantment_subtypes", []))
    shared_enchant_subtypes = enchant_subtypes1.intersection(enchant_subtypes2)

    for subtype in shared_enchant_subtypes:
        result["score"] += 2
        result["matches"].append(f"enchantment_subtype:{subtype}")

    return result

def calculate_mana_curve_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate mana curve synergy score between two cards."""
    result = {"score": 0, "matches": []}

    vectors1 = card1.get("synergy_vectors", {})
    vectors2 = card2.get("synergy_vectors", {})

    curve1 = vectors1.get("mana_curve", {})
    curve2 = vectors2.get("mana_curve", {})

    cmc1 = curve1.get("cmc", 0)
    cmc2 = curve2.get("cmc", 0)

    # Good mana curve distribution
    cmc_diff = abs(cmc1 - cmc2)
    if cmc_diff == 1:
        result["score"] += 1
        result["matches"].append("curve:adjacent_costs")
    elif cmc_diff == 2:
        result["score"] += 0.5
        result["matches"].append("curve:good_spread")

    # Color intensity compatibility
    intensity1 = curve1.get("mana_intensiveness", 0)
    intensity2 = curve2.get("mana_intensiveness", 0)

    if abs(intensity1 - intensity2) < 0.3:  # Similar color requirements
        result["score"] += 0.5
        result["matches"].append("curve:similar_intensity")

    return result

def calculate_format_synergy(card1: Dict[str, Any], card2: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate format legality synergy score between two cards."""
    result = {"score": 0, "matches": []}

    formats1 = set(card1.get("legal_formats", []))
    formats2 = set(card2.get("legal_formats", []))

    shared_formats = formats1.intersection(formats2)

    # Weight formats by popularity/importance
    format_weights = {
        "commander": 1.0,
        "modern": 0.8,
        "pioneer": 0.7,
        "standard": 0.9,
        "legacy": 0.6,
        "vintage": 0.5,
        "pauper": 0.4
    }

    for fmt in shared_formats:
        weight = format_weights.get(fmt, 0.2)
        result["score"] += weight
        result["matches"].append(f"format:{fmt}")

    return result

def find_synergy_candidates(card_analysis: Dict[str, Any], collection_analyses: List[Dict[str, Any]],
                          threshold: float = 5.0) -> List[Dict[str, Any]]:
    """
    Find potential synergies between a card and a collection using comprehensive analysis.

    Args:
        card_analysis: Analysis data for the target card
        collection_analyses: List of analysis data for cards in the collection
        threshold: Minimum synergy score to consider a match

    Returns:
        List of synergy matches sorted by score
    """
    synergies = []

    for other_card in collection_analyses:
        # Skip self-comparison - check both the analysis and parent card data
        target_name = card_analysis.get("name")
        other_name = other_card.get("name")

        # Handle cases where name might be in the parent card structure
        if not target_name and hasattr(card_analysis, 'get'):
            # Try to get from parent card data if this is a nested structure
            target_name = getattr(card_analysis, 'name', None)
        if not other_name and hasattr(other_card, 'get'):
            other_name = getattr(other_card, 'name', None)

        if target_name and other_name and target_name == other_name:
            continue

        # Check for ID-based comparison as fallback
        if (card_analysis.get("id") and other_card.get("id") and
            card_analysis.get("id") == other_card.get("id")):
            continue

        synergy_result = calculate_synergy_score(card_analysis, other_card)

        if synergy_result["total_score"] >= threshold:
            synergies.append({
                "card": other_card,
                "synergy": synergy_result,
                "score": synergy_result["total_score"]
            })

    # Sort by synergy score (highest first)
    synergies.sort(key=lambda x: x["score"], reverse=True)

    return synergies

def extract_card_data_features(card_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract synergy-relevant features from Scryfall card data.

    Args:
        card_data: Card data from Scryfall API

    Returns:
        Dictionary containing extracted card features
    """
    result = {}

    # Extract colors and color identity
    result["colors"] = card_data.get("colors", [])
    result["color_identity"] = card_data.get("color_identity", [])

    # Parse type line for card types and subtypes
    type_line = card_data.get("type_line", "")
    result.update(parse_type_line(type_line))

    # Parse mana cost
    mana_cost = card_data.get("mana_cost", "")
    result["mana_cost_info"] = parse_mana_cost(mana_cost)

    # Extract power and toughness
    power = card_data.get("power")
    toughness = card_data.get("toughness")
    result["power_toughness"] = {
        "power": power,
        "toughness": toughness,
        "power_numeric": convert_power_toughness_to_numeric(power),
        "toughness_numeric": convert_power_toughness_to_numeric(toughness)
    }

    # Extract keywords from Scryfall data
    scryfall_keywords = card_data.get("keywords", [])
    result["scryfall_keywords"] = [kw.lower() for kw in scryfall_keywords]

    # Extract legalities for format synergies
    legalities = card_data.get("legalities", {})
    result["legal_formats"] = [fmt for fmt, legality in legalities.items() if legality == "legal"]

    # Extract rarity
    result["rarity"] = card_data.get("rarity", "").lower()

    # Extract set information
    result["set_code"] = card_data.get("set", "")
    result["set_name"] = card_data.get("set_name", "")

    # Extract converted mana cost
    result["cmc"] = card_data.get("cmc", 0)

    # Check for special properties
    result["is_legendary"] = "legendary" in type_line.lower()
    result["is_artifact"] = "artifact" in type_line.lower()
    result["is_enchantment"] = "enchantment" in type_line.lower()
    result["is_multicolored"] = len(result["colors"]) > 1
    result["is_colorless"] = len(result["colors"]) == 0

    return result

def parse_type_line(type_line: str) -> Dict[str, Any]:
    """
    Parse the type line to extract card types and subtypes.

    Args:
        type_line: The type line string from card data

    Returns:
        Dictionary with parsed type information
    """
    result = {
        "card_types": [],
        "creature_types": [],
        "planeswalker_types": [],
        "artifact_subtypes": [],
        "enchantment_subtypes": []
    }

    if not type_line:
        return result

    type_line_lower = type_line.lower()

    # Split by "—" to separate types from subtypes
    parts = type_line.split("—")
    main_types = parts[0].strip().lower() if parts else ""
    subtypes = parts[1].strip().lower() if len(parts) > 1 else ""

    # Extract main card types
    for card_type in MTG_KEYWORDS["card_types"]:
        if card_type in main_types:
            result["card_types"].append(card_type)

    # Extract subtypes based on main type
    if subtypes:
        if "creature" in main_types:
            for creature_type in MTG_KEYWORDS["creature_types"]:
                if creature_type in subtypes:
                    result["creature_types"].append(creature_type)

        if "planeswalker" in main_types:
            for pw_type in MTG_KEYWORDS["planeswalker_types"]:
                if pw_type in subtypes:
                    result["planeswalker_types"].append(pw_type)

        if "artifact" in main_types:
            for artifact_subtype in MTG_KEYWORDS["artifact_subtypes"]:
                if artifact_subtype in subtypes:
                    result["artifact_subtypes"].append(artifact_subtype)

        if "enchantment" in main_types:
            for enchant_subtype in MTG_KEYWORDS["enchantment_subtypes"]:
                if enchant_subtype in subtypes:
                    result["enchantment_subtypes"].append(enchant_subtype)

    return result

def parse_mana_cost(mana_cost: str) -> Dict[str, Any]:
    """
    Parse mana cost string to extract detailed mana information.

    Args:
        mana_cost: Mana cost string (e.g., "{2}{W}{U}")

    Returns:
        Dictionary with parsed mana cost information
    """
    if not mana_cost:
        return {}

    import re

    result = {
        "total_symbols": 0,
        "colored_symbols": 0,
        "generic_mana": 0,
        "white": 0,
        "blue": 0,
        "black": 0,
        "red": 0,
        "green": 0,
        "colorless": 0,
        "hybrid": 0,
        "phyrexian": 0,
        "x_cost": 0
    }

    # Find all mana symbols in braces
    symbols = re.findall(r'\{([^}]+)\}', mana_cost)

    for symbol in symbols:
        result["total_symbols"] += 1
        symbol_lower = symbol.lower()

        if symbol_lower == "w":
            result["white"] += 1
            result["colored_symbols"] += 1
        elif symbol_lower == "u":
            result["blue"] += 1
            result["colored_symbols"] += 1
        elif symbol_lower == "b":
            result["black"] += 1
            result["colored_symbols"] += 1
        elif symbol_lower == "r":
            result["red"] += 1
            result["colored_symbols"] += 1
        elif symbol_lower == "g":
            result["green"] += 1
            result["colored_symbols"] += 1
        elif symbol_lower == "c":
            result["colorless"] += 1
        elif symbol_lower == "x":
            result["x_cost"] += 1
        elif symbol_lower.isdigit():
            result["generic_mana"] += int(symbol_lower)
        elif "/" in symbol_lower:
            result["hybrid"] += 1
        elif "p" in symbol_lower:
            result["phyrexian"] += 1

    return result

def convert_power_toughness_to_numeric(value: str) -> int:
    """
    Convert power/toughness string to numeric value for comparison.

    Args:
        value: Power or toughness string

    Returns:
        Numeric value (or special codes for * and X)
    """
    if not value:
        return 0

    value_str = str(value).strip()

    if value_str == "*":
        return -1  # Special value for variable power/toughness
    elif value_str.upper() == "X":
        return -2  # Special value for X power/toughness
    elif value_str.isdigit():
        return int(value_str)
    elif value_str.startswith("-") and value_str[1:].isdigit():
        return int(value_str)
    else:
        return 0

def generate_synergy_vectors(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate synergy vectors for improved card matching and synergy detection.

    Args:
        analysis: Complete card analysis data

    Returns:
        Dictionary of synergy vectors categorized by synergy type
    """
    vectors = {
        "tribal": [],
        "color_synergy": [],
        "mana_curve": [],
        "keyword_synergy": [],
        "type_synergy": [],
        "archetype": [],
        "combo_potential": [],
        "format_synergy": []
    }

    # Tribal synergies
    creature_types = analysis.get("creature_types", [])
    if creature_types:
        vectors["tribal"] = creature_types

    # Color synergies
    colors = analysis.get("colors", [])
    color_identity = analysis.get("color_identity", [])
    vectors["color_synergy"] = {
        "colors": colors,
        "color_identity": color_identity,
        "is_multicolored": len(colors) > 1,
        "is_colorless": len(colors) == 0,
        "color_count": len(colors)
    }

    # Mana curve synergies
    mana_info = analysis.get("mana_cost_info", {})
    cmc = analysis.get("cmc", 0)
    vectors["mana_curve"] = {
        "cmc": cmc,
        "colored_symbols": mana_info.get("colored_symbols", 0),
        "generic_mana": mana_info.get("generic_mana", 0),
        "mana_intensiveness": mana_info.get("colored_symbols", 0) / max(cmc, 1)
    }

    # Keyword synergies
    all_keywords = set()
    all_keywords.update(analysis.get("keywords", []))
    all_keywords.update(analysis.get("scryfall_keywords", []))
    vectors["keyword_synergy"] = list(all_keywords)

    # Type synergies
    vectors["type_synergy"] = {
        "card_types": analysis.get("card_types", []),
        "artifact_subtypes": analysis.get("artifact_subtypes", []),
        "enchantment_subtypes": analysis.get("enchantment_subtypes", []),
        "is_legendary": analysis.get("is_legendary", False)
    }

    # Archetype detection
    archetype_indicators = detect_archetype_indicators(analysis)
    vectors["archetype"] = archetype_indicators

    # Combo potential
    combo_indicators = detect_combo_potential(analysis)
    vectors["combo_potential"] = combo_indicators

    # Format synergies
    vectors["format_synergy"] = analysis.get("legal_formats", [])

    return vectors

def detect_archetype_indicators(analysis: Dict[str, Any]) -> List[str]:
    """
    Detect archetype indicators from card analysis.

    Args:
        analysis: Card analysis data

    Returns:
        List of archetype indicators
    """
    archetypes = []

    actions = analysis.get("actions", [])
    zones = analysis.get("zones", [])
    keywords = analysis.get("keywords", [])
    oracle_text = " ".join(analysis.get("raw_tokens", [])).lower()

    # Graveyard-based archetypes
    if any(zone in ["graveyard"] for zone in zones) or any(action in ["mill", "dredge", "reanimate"] for action in actions):
        archetypes.append("graveyard")

    # Aggressive archetypes
    if any(keyword in ["haste", "trample", "double strike", "first strike"] for keyword in keywords):
        archetypes.append("aggro")

    # Control archetypes
    if any(action in ["counter", "destroy", "exile"] for action in actions):
        archetypes.append("control")

    # Artifact-based archetypes
    if "artifact" in analysis.get("card_types", []) or "improvise" in keywords:
        archetypes.append("artifacts")

    # Enchantment-based archetypes
    if "enchantment" in analysis.get("card_types", []) or "constellation" in oracle_text:
        archetypes.append("enchantments")

    # Spellslinger archetypes
    if any(keyword in ["prowess", "storm"] for keyword in keywords) or "instant" in oracle_text or "sorcery" in oracle_text:
        archetypes.append("spells")

    # Token strategies
    if any(word in oracle_text for word in ["token", "populate", "create"]):
        archetypes.append("tokens")

    # Lifegain strategies
    if "lifelink" in keywords or "gain" in oracle_text:
        archetypes.append("lifegain")

    # Sacrifice strategies
    if "sacrifice" in actions:
        archetypes.append("sacrifice")

    # Lands matter
    if "land" in oracle_text or "landfall" in keywords:
        archetypes.append("lands")

    return archetypes

def detect_combo_potential(analysis: Dict[str, Any]) -> List[str]:
    """
    Detect combo potential indicators from card analysis.

    Args:
        analysis: Card analysis data

    Returns:
        List of combo potential indicators
    """
    combo_indicators = []

    actions = analysis.get("actions", [])
    keywords = analysis.get("keywords", [])
    oracle_text = " ".join(analysis.get("raw_tokens", [])).lower()

    # Infinite mana potential
    if any(word in oracle_text for word in ["add", "mana", "untap"]):
        combo_indicators.append("mana_generation")

    # Tutoring effects
    if "search" in actions or "tutor" in oracle_text:
        combo_indicators.append("tutoring")

    # Card draw engines
    if "draw" in actions or any(word in oracle_text for word in ["draw", "card"]):
        combo_indicators.append("card_draw")

    # Recursion
    if any(action in ["return", "recur"] for action in actions):
        combo_indicators.append("recursion")

    # Untap effects
    if "untap" in actions:
        combo_indicators.append("untap_effects")

    # Copy effects
    if "copy" in actions or "copy" in oracle_text:
        combo_indicators.append("copy_effects")

    # Storm potential
    if "storm" in keywords:
        combo_indicators.append("storm")

    # Infinite token potential
    if any(word in oracle_text for word in ["token", "populate", "create"]) and "untap" in actions:
        combo_indicators.append("infinite_tokens")

    return combo_indicators
