from marshmallow import Schema, fields, ValidationError, EXCLUDE, post_load

class CardImportSchema(Schema):
    """
    Schema for validating individual card entries from CSV import.
    Uses EXCLUDE to ignore unknown fields found in the CSV.
    """
    class Meta:
        unknown = EXCLUDE # Ignore fields in CSV not defined in schema

    Count = fields.Integer(required=True, error_messages={"required": "Count is required."})
    Tradelist_Count = fields.Integer(data_key="Tradelist Count", allow_none=True) # CSV header has space
    Name = fields.String(required=True, error_messages={"required": "Name is required."})
    Edition = fields.String(allow_none=True)
    Edition_Code = fields.String(data_key="Edition Code", allow_none=True) # CSV header has space
    Card_Number = fields.String(data_key="Card Number", allow_none=True) # CSV header has space
    Condition = fields.String(allow_none=True)
    Language = fields.String(allow_none=True)
    Foil = fields.String(allow_none=True) # Could be boolean if values are consistent
    Signed = fields.String(allow_none=True) # Assuming string, could be boolean
    Artist_Proof = fields.String(data_key="Artist Proof", allow_none=True) # CSV header has space
    Altered_Art = fields.String(data_key="Altered Art", allow_none=True) # CSV header has space
    Misprint = fields.String(allow_none=True)
    Promo = fields.String(allow_none=True)
    Textless = fields.String(allow_none=True)
    Printing_Id = fields.String(data_key="Printing Id", allow_none=True) # CSV header has space
    Printing_Note = fields.String(data_key="Printing Note", allow_none=True) # CSV header has space
    Tags = fields.String(allow_none=True)
    My_Price = fields.String(data_key="My Price", allow_none=True) # CSV header has space, often a string like "$0.00"
    scryfall_id = fields.String(data_key="Scryfall ID", allow_none=True) # Direct Scryfall ID for precise lookup - lowercase to match Card model

    # Example of a custom validator if needed:
    # @validates_schema
    # def validate_counts(self, data, **kwargs):
    #     if data.get('Count', 0) < 0:
    #         raise ValidationError("Count cannot be negative.", "Count")
