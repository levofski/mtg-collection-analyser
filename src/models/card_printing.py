"""
Model for specific printings of cards in the user's collection.
"""
from typing import Optional, Dict, Any
import json

from ..database import db

class CardPrinting(db.Model):
    """Represents a specific printing of a card in the user's collection."""

    __tablename__ = "card_printings"

    # Primary key - auto-incrementing ID
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to CardInfo
    card_info_id = db.Column(db.Integer, db.ForeignKey('card_info.id'), nullable=False)
    card_info = db.relationship("CardInfo", back_populates="printings",
                               foreign_keys=[card_info_id])

    # Fields from CSV import related to collection ownership
    Count = db.Column(db.Integer, nullable=False)
    Tradelist_Count = db.Column(db.Integer, nullable=True)

    # Fields specific to a printing
    Edition = db.Column(db.String(255), nullable=True)
    Edition_Code = db.Column(db.String(50), nullable=True)
    Card_Number = db.Column(db.String(50), nullable=True)
    Condition = db.Column(db.String(50), nullable=True)
    Language = db.Column(db.String(50), nullable=True)
    Foil = db.Column(db.String(50), nullable=True)  # Could be bool if normalized
    Signed = db.Column(db.String(50), nullable=True)
    Artist_Proof = db.Column(db.String(50), nullable=True)
    Altered_Art = db.Column(db.String(50), nullable=True)
    Misprint = db.Column(db.String(50), nullable=True)
    Promo = db.Column(db.String(50), nullable=True)
    Textless = db.Column(db.String(50), nullable=True)
    Printing_Id = db.Column(db.String(50), nullable=True)
    Printing_Note = db.Column(db.String(255), nullable=True)
    Tags = db.Column(db.String(255), nullable=True)
    My_Price = db.Column(db.String(50), nullable=True)

    # Scryfall data specific to this printing
    scryfall_id = db.Column(db.String(100), nullable=True)
    _image_uris = db.Column("image_uris", db.Text, nullable=True)  # Store JSON as text

    # Track when each record was created/modified
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def image_uris(self) -> Optional[Dict[str, Any]]:
        """Convert stored JSON string to dictionary."""
        if self._image_uris:
            return json.loads(self._image_uris)
        return None

    @image_uris.setter
    def image_uris(self, value: Optional[Dict[str, Any]]) -> None:
        """Convert dictionary to JSON string for storage."""
        if value is not None:
            self._image_uris = json.dumps(value)
        else:
            self._image_uris = None

    def __repr__(self) -> str:
        return f"<CardPrinting(id={self.id}, Edition='{self.Edition}', Count={self.Count})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converts the CardPrinting object to a dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "card_info_id": self.card_info_id,
            "Count": self.Count,
            "Tradelist_Count": self.Tradelist_Count,
            "Edition": self.Edition,
            "Edition_Code": self.Edition_Code,
            "Card_Number": self.Card_Number,
            "Condition": self.Condition,
            "Language": self.Language,
            "Foil": self.Foil,
            "Signed": self.Signed,
            "Artist_Proof": self.Artist_Proof,
            "Altered_Art": self.Altered_Art,
            "Misprint": self.Misprint,
            "Promo": self.Promo,
            "Textless": self.Textless,
            "Printing_Id": self.Printing_Id,
            "Printing_Note": self.Printing_Note,
            "Tags": self.Tags,
            "My_Price": self.My_Price,
            "scryfall_id": self.scryfall_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        # Add Scryfall printing-specific fields
        if self.image_uris:
            data["image_uris"] = self.image_uris

        # Include card_info data if it's loaded
        if self.card_info:
            data["name"] = self.card_info.name
            data["oracle_text"] = self.card_info.oracle_text
            data["mana_cost"] = self.card_info.mana_cost
            data["cmc"] = self.card_info.cmc
            data["type_line"] = self.card_info.type_line

        return {k: v for k, v in data.items() if v is not None}  # Return only non-None values
