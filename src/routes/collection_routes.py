\
from flask import Blueprint, request, jsonify
from flask.wrappers import Response as FlaskResponse
from werkzeug.datastructures import FileStorage

from ..services.csv_importer import process_csv_data

collection_bp = Blueprint('collection_bp', __name__, url_prefix='/collection')

@collection_bp.route('/import_csv', methods=['POST'])
def import_csv_route() -> FlaskResponse:
    """
    Imports a CSV file containing card collection data.
    The CSV file is expected to be in the request's files.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file: FileStorage = request.files['file'] # type: ignore
    
    if not file.filename: # Handles case where file part exists but no file selected
        return jsonify({"error": "No selected file"}), 400
    
    if file.filename.endswith('.csv'):
        try:
            # file.stream is IO[bytes]
            message, data, status_code = process_csv_data(file.stream) 
            
            response_data = {"message": message}
            if data is not None and status_code == 200:
                response_data["cards_processed"] = len(data)
            
            if status_code == 200:
                 return jsonify(response_data), status_code
            else: # Error cases from process_csv_data
                return jsonify({"error": message}), status_code

        except Exception as e:
            # General exception handling for unexpected errors in the route
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type, please upload a CSV file."}), 400
