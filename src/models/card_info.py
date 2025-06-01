"""
Model for the card information that is shared across printings.
This includes Oracle text, mana cost, etc.
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from ..database import db

class CardInfo(db.Model):
    """Represents core Magic card data, shared across all printings of the same card."""

    __tablename__ = "card_info"

    # Primary key - auto-incrementing ID
    id = db.Column(db.Integer, primary_key=True)

    # Card identity fields - these define a unique card
    name = db.Column(db.String(255), nullable=False, index=True, unique=True)
    oracle_id = db.Column(db.String(100), nullable=True, unique=True)  # Scryfall's oracle_id

    # Oracle fields - shared across all printings
    oracle_text = db.Column(db.Text, nullable=True)
    mana_cost = db.Column(db.String(50), nullable=True)
    cmc = db.Column(db.Float, nullable=True)
    type_line = db.Column(db.String(255), nullable=True)

    # Text analysis fields - stored as JSON strings
    _keywords = db.Column("keywords", db.Text, nullable=True)
    _extracted_data = db.Column("extracted_data", db.Text, nullable=True)

    # Related models - use string for back_populates to avoid circular imports
    printings = db.relationship("CardPrinting", back_populates="card_info", lazy="dynamic",
                               foreign_keys="CardPrinting.card_info_id")

    # Track when each record was created/modified
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def keywords(self) -> Optional[List[str]]:
        """Get list of keywords for this card."""
        if self._keywords:
            return json.loads(self._keywords)
        return None

    @keywords.setter
    def keywords(self, value: Optional[List[str]]) -> None:
        """Set keywords for this card."""
        if value is not None:
            self._keywords = json.dumps(value)
        else:
            self._keywords = None

    @property
    def extracted_data(self) -> Optional[Dict[str, Any]]:
        """Get extracted data from text analysis."""
        if self._extracted_data:
            return json.loads(self._extracted_data)
        return None

    @extracted_data.setter
    def extracted_data(self, value: Optional[Dict[str, Any]]) -> None:
        """Set extracted data from text analysis."""
        if value is not None:
            self._extracted_data = json.dumps(value)
        else:
            self._extracted_data = None

    def __repr__(self) -> str:
        return f"<CardInfo(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Converts the CardInfo object to a dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "name": self.name,
            "oracle_id": self.oracle_id,
            "oracle_text": self.oracle_text,
            "mana_cost": self.mana_cost,
            "cmc": self.cmc,
            "type_line": self.type_line,
            "keywords": self.keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        # Add extracted data if available
        if self.extracted_data:
            data["extracted_data"] = self.extracted_data

        return {k: v for k, v in data.items() if v is not None}  # Return only non-None values
