\
import csv
import io
from typing import List, Dict, Tuple, Any, Optional, IO

from marshmallow import ValidationError
from ..schemas.card_schemas import CardImportSchema
from ..models.card_info import CardInfo
from ..models.card_printing import CardPrinting
from ..store.card_info_store import get_or_create_card_info

def process_csv_data(file_stream: IO[bytes]) -> Tuple[str, Optional[List[CardPrinting]], Optional[List[Dict[str, Any]]], int]:
    """
    Processes the CSV data from a byte file stream, validates it, and collects errors.

    Args:
        file_stream: The byte file stream object from the uploaded file.

    Returns:
        A tuple containing:
            - message (str): A summary message.
            - valid_printings (Optional[List[CardPrinting]]): List of successfully validated card printings as CardPrinting objects.
            - validation_errors (Optional[List[Dict[str, Any]]]): List of validation errors.
            - status_code (int): HTTP status code.
    """
    schema = CardImportSchema()
    valid_printings: List[CardPrinting] = []
    validation_errors: List[Dict[str, Any]] = []

    try:
        stream_content: bytes = file_stream.read()
        try:
            decoded_content: str = stream_content.decode("UTF-8")
        except UnicodeDecodeError:
            return "Invalid file encoding. Please use UTF-8.", None, [{"file_error": "Invalid file encoding. Please use UTF-8."}], 400

        string_io: io.StringIO = io.StringIO(decoded_content, newline=None)
        csv_reader: csv.DictReader = csv.DictReader(string_io)

        row_number = 1 # For error reporting
        for row in csv_reader:
            row_number += 1
            try:
                # Validate and deserialize data
                loaded_data = schema.load(row)

                # Get or create the CardInfo record
                card_name = loaded_data.pop('Name')
                card_info, _ = get_or_create_card_info(card_name)

                # Create the CardPrinting object with the remaining data
                card_printing = CardPrinting(card_info=card_info, **loaded_data)
                valid_printings.append(card_printing)
            except ValidationError as err:
                validation_errors.append({"row": row_number, "errors": err.messages, "data": row})
            except Exception as e: # Catch other unexpected errors during schema loading or CardPrinting creation
                validation_errors.append({"row": row_number, "errors": {"_unexpected": [str(e)]}, "data": row})


        if not valid_printings and not validation_errors:
             # This case implies the CSV was empty or only had headers
            return "CSV file is empty or contains no data rows.", None, None, 400

        message = f"Processed {len(valid_printings)} card(s) successfully."
        if validation_errors:
            message += f" Found {len(validation_errors)} row(s) with validation errors."
            # If there are errors, but also some valid cards, it's a partial success (207 Multi-Status)
            # If only errors and no valid cards, it's a client error (400 Bad Request)
            status_code = 207 if valid_printings else 400
        else:
            status_code = 200 # All good

        return message, valid_printings if valid_printings else None, validation_errors if validation_errors else None, status_code

    except csv.Error as e:
        return f"CSV parsing error: {str(e)}", None, [{"file_error": f"CSV parsing error: {str(e)}" }], 400
    except Exception as e:
        # Catch other potential errors during general processing
        return f"Failed to process CSV file: {str(e)}", None, [{"file_error": f"Failed to process CSV file: {str(e)}" }], 500
