\
import csv
import io
from typing import List, Dict, Tuple, Any, Optional, IO

def process_csv_data(file_stream: IO[bytes]) -> Tuple[str, Optional[List[Dict[str, Any]]], int]:
    """
    Processes the CSV data from a byte file stream.

    Args:
        file_stream: The byte file stream object from the uploaded file.

    Returns:
        A tuple containing:
            - message (str): A success or error message.
            - data (Optional[List[Dict[str, Any]]]): A list of dictionaries 
              representing cards, or None on error.
            - status_code (int): HTTP status code.
    """
    try:
        stream_content: bytes = file_stream.read()
        try:
            decoded_content: str = stream_content.decode("UTF-8")
        except UnicodeDecodeError:
            return "Invalid file encoding. Please use UTF-8.", None, 400
            
        string_io: io.StringIO = io.StringIO(decoded_content, newline=None)
        csv_reader: csv.DictReader = csv.DictReader(string_io) 
        
        cards: List[Dict[str, Any]] = []
        for row in csv_reader:
            # Basic validation: Ensure 'Name' and 'Count' are present and not empty
            if not row.get('Name') or not row.get('Count'):
                # Skipping row due to missing 'Name' or 'Count'.
                # A more robust solution might collect errors or log.
                continue 
            cards.append(row)
        
        if not cards:
            return "CSV file is empty or contains no valid card data after filtering.", None, 400

        return f"{len(cards)} cards processed successfully.", cards, 200
    except csv.Error as e:
        return f"CSV parsing error: {str(e)}", None, 400
    except Exception as e:
        # Catch other potential errors during processing
        return f"Failed to process CSV file: {str(e)}", None, 500
