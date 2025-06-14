"""
Model for storing synergy scores between pairs of cards.
"""
from typing import Dict, Any, Optional
import json
from datetime import datetime

from ..database import db

class CardSynergy(db.Model):
    """Represents synergy relationship between two cards."""

    __tablename__ = "card_synergy"

    # Primary key - composite of the two card IDs
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys to the two cards
    card1_id = db.Column(db.Integer, db.ForeignKey('card_info.id'), nullable=False, index=True)
    card2_id = db.Column(db.Integer, db.ForeignKey('card_info.id'), nullable=False, index=True)

    # Synergy score and breakdown
    total_score = db.Column(db.Float, nullable=False, index=True)

    # Detailed breakdown stored as JSON
    _synergy_breakdown = db.Column("synergy_breakdown", db.Text, nullable=True)

    # Individual synergy component scores for easier querying
    tribal_score = db.Column(db.Float, default=0, index=True)
    color_score = db.Column(db.Float, default=0)
    keyword_score = db.Column(db.Float, default=0)
    archetype_score = db.Column(db.Float, default=0, index=True)
    combo_score = db.Column(db.Float, default=0, index=True)
    type_score = db.Column(db.Float, default=0)
    mana_curve_score = db.Column(db.Float, default=0)
    format_score = db.Column(db.Float, default=0)

    # Analysis metadata
    analysis_version = db.Column(db.String(20), default="1.0")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    card1 = db.relationship("CardInfo", foreign_keys=[card1_id], backref="synergies_as_card1")
    card2 = db.relationship("CardInfo", foreign_keys=[card2_id], backref="synergies_as_card2")

    # Unique constraint to prevent duplicate pairs
    __table_args__ = (
        db.UniqueConstraint('card1_id', 'card2_id', name='unique_card_pair'),
        db.Index('idx_synergy_score', 'total_score'),
        db.Index('idx_tribal_synergy', 'tribal_score'),
        db.Index('idx_combo_synergy', 'combo_score'),
        db.Index('idx_archetype_synergy', 'archetype_score'),
    )

    @property
    def synergy_breakdown(self) -> Optional[Dict[str, Any]]:
        """Get detailed synergy breakdown."""
        if self._synergy_breakdown:
            return json.loads(self._synergy_breakdown)
        return None

    @synergy_breakdown.setter
    def synergy_breakdown(self, value: Optional[Dict[str, Any]]) -> None:
        """Set detailed synergy breakdown."""
        if value is not None:
            self._synergy_breakdown = json.dumps(value)
        else:
            self._synergy_breakdown = None

    @classmethod
    def create_from_analysis(cls, card1_id: int, card2_id: int, synergy_result: Dict[str, Any]) -> 'CardSynergy':
        """
        Create a CardSynergy instance from synergy analysis result.

        Args:
            card1_id: ID of the first card
            card2_id: ID of the second card
            synergy_result: Result from calculate_synergy_score()

        Returns:
            CardSynergy instance
        """
        # Ensure consistent ordering (lower ID first)
        if card1_id > card2_id:
            card1_id, card2_id = card2_id, card1_id

        synergy = cls(
            card1_id=card1_id,
            card2_id=card2_id,
            total_score=synergy_result.get('total_score', 0),
            tribal_score=synergy_result.get('tribal_score', 0),
            color_score=synergy_result.get('color_score', 0),
            keyword_score=synergy_result.get('keyword_score', 0),
            archetype_score=synergy_result.get('archetype_score', 0),
            combo_score=synergy_result.get('combo_score', 0),
            type_score=synergy_result.get('type_score', 0),
            mana_curve_score=synergy_result.get('mana_curve_score', 0),
            format_score=synergy_result.get('format_score', 0),
            synergy_breakdown=synergy_result
        )

        return synergy

    @classmethod
    def get_synergy(cls, card1_id: int, card2_id: int) -> Optional['CardSynergy']:
        """
        Get synergy between two cards (order independent).

        Args:
            card1_id: ID of the first card
            card2_id: ID of the second card

        Returns:
            CardSynergy instance or None if not found
        """
        # Ensure consistent ordering
        if card1_id > card2_id:
            card1_id, card2_id = card2_id, card1_id

        return cls.query.filter_by(card1_id=card1_id, card2_id=card2_id).first()

    @classmethod
    def get_top_synergies(cls, limit: int = 100, min_score: float = 10.0) -> list['CardSynergy']:
        """
        Get top synergies across the entire collection.

        Args:
            limit: Maximum number of synergies to return
            min_score: Minimum synergy score to include

        Returns:
            List of CardSynergy instances sorted by total score
        """
        return cls.query.filter(
            cls.total_score >= min_score
        ).order_by(cls.total_score.desc()).limit(limit).all()

    @classmethod
    def get_synergies_for_card(cls, card_id: int, min_score: float = 5.0, limit: int = 50) -> list['CardSynergy']:
        """
        Get all synergies for a specific card.

        Args:
            card_id: ID of the card to find synergies for
            min_score: Minimum synergy score to include
            limit: Maximum number of synergies to return

        Returns:
            List of CardSynergy instances sorted by total score
        """
        return cls.query.filter(
            db.or_(cls.card1_id == card_id, cls.card2_id == card_id),
            cls.total_score >= min_score
        ).order_by(cls.total_score.desc()).limit(limit).all()

    @classmethod
    def get_tribal_synergies(cls, min_score: float = 15.0) -> list['CardSynergy']:
        """Get synergies with high tribal scores."""
        return cls.query.filter(
            cls.tribal_score >= min_score
        ).order_by(cls.tribal_score.desc()).all()

    @classmethod
    def get_combo_synergies(cls, min_score: float = 15.0) -> list['CardSynergy']:
        """Get synergies with high combo potential."""
        return cls.query.filter(
            cls.combo_score >= min_score
        ).order_by(cls.combo_score.desc()).all()

    @classmethod
    def get_archetype_synergies(cls, min_score: float = 10.0) -> list['CardSynergy']:
        """Get synergies with high archetype scores."""
        return cls.query.filter(
            cls.archetype_score >= min_score
        ).order_by(cls.archetype_score.desc()).all()

    def get_partner_card(self, card_id: int):
        """
        Get the partner card in this synergy relationship.

        Args:
            card_id: ID of one card in the pair

        Returns:
            The other card in the synergy pair, or None if card_id is not in this pair
        """
        if self.card1_id == card_id:
            return self.card2
        elif self.card2_id == card_id:
            return self.card1
        else:
            return None

    def __repr__(self) -> str:
        return f"<CardSynergy(card1_id={self.card1_id}, card2_id={self.card2_id}, score={self.total_score:.1f})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "card1_id": self.card1_id,
            "card2_id": self.card2_id,
            "total_score": self.total_score,
            "tribal_score": self.tribal_score,
            "color_score": self.color_score,
            "keyword_score": self.keyword_score,
            "archetype_score": self.archetype_score,
            "combo_score": self.combo_score,
            "type_score": self.type_score,
            "mana_curve_score": self.mana_curve_score,
            "format_score": self.format_score,
            "synergy_breakdown": self.synergy_breakdown,
            "analysis_version": self.analysis_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
