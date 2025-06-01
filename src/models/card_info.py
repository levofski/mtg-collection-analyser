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

    # Related models
    printings = db.relationship("CardPrinting", back_populates="card_info", lazy="dynamic")

    # Track when each record was created/modified
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        return {k: v for k, v in data.items() if v is not None}  # Return only non-None values
