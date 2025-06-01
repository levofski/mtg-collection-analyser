from typing import Optional

class Card:
    """Represents a card entry in the user's collection."""

    def __init__(
        self,
        Name: str,
        Count: int,
        Tradelist_Count: Optional[int] = None,
        Edition: Optional[str] = None,
        Edition_Code: Optional[str] = None,
        Card_Number: Optional[str] = None,
        Condition: Optional[str] = None,
        Language: Optional[str] = None,
        Foil: Optional[str] = None, # Could be bool if normalized
        Signed: Optional[str] = None,
        Artist_Proof: Optional[str] = None,
        Altered_Art: Optional[str] = None,
        Misprint: Optional[str] = None,
        Promo: Optional[str] = None,
        Textless: Optional[str] = None,
        Printing_Id: Optional[str] = None,
        Printing_Note: Optional[str] = None,
        Tags: Optional[str] = None,
        My_Price: Optional[str] = None,
        # Add other fields from Scryfall later as needed
        scryfall_id: Optional[str] = None, # Example for future Scryfall data
        oracle_text: Optional[str] = None, # Example for future Scryfall data
        mana_cost: Optional[str] = None,   # Example for future Scryfall data
        cmc: Optional[float] = None,       # Example for future Scryfall data
        type_line: Optional[str] = None,   # Example for future Scryfall data
        image_uris: Optional[dict] = None # Example for future Scryfall data
    ):
        self.Name: str = Name
        self.Count: int = Count
        self.Tradelist_Count: Optional[int] = Tradelist_Count
        self.Edition: Optional[str] = Edition
        self.Edition_Code: Optional[str] = Edition_Code
        self.Card_Number: Optional[str] = Card_Number
        self.Condition: Optional[str] = Condition
        self.Language: Optional[str] = Language
        self.Foil: Optional[str] = Foil
        self.Signed: Optional[str] = Signed
        self.Artist_Proof: Optional[str] = Artist_Proof
        self.Altered_Art: Optional[str] = Altered_Art
        self.Misprint: Optional[str] = Misprint
        self.Promo: Optional[str] = Promo
        self.Textless: Optional[str] = Textless
        self.Printing_Id: Optional[str] = Printing_Id
        self.Printing_Note: Optional[str] = Printing_Note
        self.Tags: Optional[str] = Tags
        self.My_Price: Optional[str] = My_Price

        # Future Scryfall fields
        self.scryfall_id: Optional[str] = scryfall_id
        self.oracle_text: Optional[str] = oracle_text
        self.mana_cost: Optional[str] = mana_cost
        self.cmc: Optional[float] = cmc
        self.type_line: Optional[str] = type_line
        self.image_uris: Optional[dict] = image_uris

    def __repr__(self) -> str:
        return f"<Card(Name='{self.Name}', Edition='{self.Edition}', Count={self.Count})>"

    def to_dict(self) -> dict:
        """Converts the Card object to a dictionary for JSON serialization."""
        # Basic implementation, can be expanded based on needs
        # Excludes Scryfall fields for now if they are None, to keep it clean
        # until those are actively used.
        data = {
            "Name": self.Name,
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
            "My_Price": self.My_Price
        }
        # Add Scryfall fields if they exist
        if self.scryfall_id: data["scryfall_id"] = self.scryfall_id
        if self.oracle_text: data["oracle_text"] = self.oracle_text
        if self.mana_cost: data["mana_cost"] = self.mana_cost
        if self.cmc is not None: data["cmc"] = self.cmc
        if self.type_line: data["type_line"] = self.type_line
        if self.image_uris: data["image_uris"] = self.image_uris

        return {k: v for k, v in data.items() if v is not None} # Return only non-None values
