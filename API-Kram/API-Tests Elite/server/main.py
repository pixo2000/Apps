from flask import Flask, jsonify, request
import json
from flask_cors import CORS
import os
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create Flask app with minimal logging
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Disable Werkzeug logger's debug and info messages
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.WARNING)

CORS(app)

# Define the storage path
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')

# Create storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

# Log server is handling requests
@app.route('/')
def index():
    """Root endpoint that confirms the API is running"""
    return jsonify({"message": "Fleet Carrier API is running"}), 200

def load_carrier(carrier_id):
    """Load a specific carrier from its JSON file"""
    file_path = os.path.join(STORAGE_DIR, f"{carrier_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                # Skip JSON comments if present
                content = file.read()
                if content.strip().startswith('//'):
                    content = '\n'.join(content.split('\n')[1:])
                return json.loads(content)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding {carrier_id}.json: {e}")
                return None
    return None

def save_carrier(carrier_data):
    """Save carrier to its JSON file"""
    if "ID" not in carrier_data:
        return False
    
    carrier_id = carrier_data["ID"]
    file_path = os.path.join(STORAGE_DIR, f"{carrier_id}.json")
    
    with open(file_path, 'w') as file:
        # Write the JSON data without any comments
        json.dump(carrier_data, file, indent=4)
    
    return True

def get_all_carrier_ids():
    """Get a list of all carrier IDs from JSON files"""
    json_files = glob.glob(os.path.join(STORAGE_DIR, "*.json"))
    carrier_ids = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        if filename != "carriers.json" and filename.endswith(".json"):
            carrier_id = filename.replace(".json", "")
            # Skip non-carrier files like NOTES.md
            if "-" in carrier_id:
                carrier_ids.append(carrier_id)
    
    return carrier_ids

@app.route('/api/carriers', methods=['GET'])
def get_all_carriers():
    """Return information about all carriers"""
    logging.info(f"GET request for all carriers")
    carrier_ids = get_all_carrier_ids()
    carriers = {}
    
    for carrier_id in carrier_ids:
        carrier_data = load_carrier(carrier_id)
        if carrier_data:
            carriers[carrier_id] = carrier_data
    
    return jsonify({"carriers": carriers})

@app.route('/api/carriers/<carrier_id>', methods=['GET'])
def get_carrier(carrier_id):
    """Return information about a specific carrier"""
    logging.info(f"GET request for carrier: {carrier_id}")
    carrier_data = load_carrier(carrier_id)
    
    if not carrier_data:
        logging.warning(f"Carrier not found: {carrier_id}")
        return jsonify({"error": f"Carrier with ID {carrier_id} not found"}), 404
    
    return jsonify({"carrier": carrier_data})

@app.route('/api/carriers', methods=['POST'])
def add_carrier():
    """Add a new carrier to the system"""
    if not request.is_json:
        logging.warning("POST request with invalid content type")
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["Name", "ID", "Position", "Owner"]
    for field in required_fields:
        if field not in data:
            logging.warning(f"POST request missing required field: {field}")
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    carrier_id = data["ID"]
    logging.info(f"POST request to add carrier: {carrier_id}")
    
    # Check if carrier already exists
    if load_carrier(carrier_id):
        logging.warning(f"Cannot add carrier, ID already exists: {carrier_id}")
        return jsonify({"error": f"Carrier with ID {carrier_id} already exists"}), 409
    
    # Initialize missing fields with default values
    if "Market" not in data:
        data["Market"] = {"Needs": {}, "Sells": {}}
    if "Cargo" not in data:
        data["Cargo"] = {}
    if "Tritium" not in data:
        data["Tritium"] = 0
    if "Docking" not in data:
        data["Docking"] = "Everyone"
    
    # Save carrier data
    if not save_carrier(data):
        logging.error(f"Failed to save carrier data: {carrier_id}")
        return jsonify({"error": "Failed to save carrier data"}), 500
    
    logging.info(f"Carrier added successfully: {carrier_id}")
    return jsonify({"message": "Carrier added successfully", "carrier": data}), 201

@app.route('/api/carriers/<carrier_id>', methods=['PUT'])
def update_carrier(carrier_id):
    """Update an existing carrier"""
    logging.info(f"PUT request to update carrier: {carrier_id}")
    
    if not request.is_json:
        logging.warning("PUT request with invalid content type")
        return jsonify({"error": "Request must be JSON"}), 400
    
    carrier_data = load_carrier(carrier_id)
    if not carrier_data:
        logging.warning(f"Cannot update, carrier not found: {carrier_id}")
        return jsonify({"error": f"Carrier with ID {carrier_id} not found"}), 404
    
    data = request.get_json()
    
    # Don't allow changing the ID field
    if "ID" in data and data["ID"] != carrier_id:
        logging.warning(f"Attempted to change carrier ID from {carrier_id} to {data['ID']}")
        return jsonify({"error": "Cannot change carrier ID"}), 400
    
    # Update carrier data with new values
    for key, value in data.items():
        if key != "ID":  # Skip ID field
            carrier_data[key] = value
    
    # Save updated data
    if not save_carrier(carrier_data):
        logging.error(f"Failed to save updated carrier data: {carrier_id}")
        return jsonify({"error": "Failed to save carrier data"}), 500
    
    logging.info(f"Carrier updated successfully: {carrier_id}")
    return jsonify({"message": "Carrier updated successfully", "carrier": carrier_data})

@app.route('/api/carriers/<carrier_id>', methods=['DELETE'])
def delete_carrier(carrier_id):
    """Delete a carrier from the system"""
    logging.info(f"DELETE request for carrier: {carrier_id}")
    
    carrier_data = load_carrier(carrier_id)
    if not carrier_data:
        logging.warning(f"Cannot delete, carrier not found: {carrier_id}")
        return jsonify({"error": f"Carrier with ID {carrier_id} not found"}), 404
    
    # Delete the carrier file
    file_path = os.path.join(STORAGE_DIR, f"{carrier_id}.json")
    try:
        os.remove(file_path)
        logging.info(f"Carrier deleted successfully: {carrier_id}")
    except OSError as e:
        logging.error(f"Failed to delete carrier {carrier_id}: {e}")
        return jsonify({"error": f"Failed to delete carrier: {e}"}), 500
    
    return jsonify({"message": f"Carrier {carrier_id} deleted successfully", "deleted_carrier": carrier_data})

@app.route('/api/carriers/<carrier_id>/market', methods=['PUT'])
def update_market(carrier_id):
    """Update a carrier's market data"""
    logging.info(f"PUT request to update market for carrier: {carrier_id}")
    
    if not request.is_json:
        logging.warning("PUT market request with invalid content type")
        return jsonify({"error": "Request must be JSON"}), 400
    
    carrier_data = load_carrier(carrier_id)
    if not carrier_data:
        logging.warning(f"Cannot update market, carrier not found: {carrier_id}")
        return jsonify({"error": f"Carrier with ID {carrier_id} not found"}), 404
    
    market_data = request.get_json()
    
    # Update market data
    if "Market" not in carrier_data:
        carrier_data["Market"] = {"Needs": {}, "Sells": {}}
    
    if "Needs" in market_data:
        carrier_data["Market"]["Needs"] = market_data["Needs"]
    if "Sells" in market_data:
        carrier_data["Market"]["Sells"] = market_data["Sells"]
    
    # Save updated data
    if not save_carrier(carrier_data):
        logging.error(f"Failed to save market data for carrier: {carrier_id}")
        return jsonify({"error": "Failed to save carrier data"}), 500
    
    logging.info(f"Market updated successfully for carrier: {carrier_id}")
    return jsonify({"message": "Market updated successfully", "market": carrier_data["Market"]})

if __name__ == '__main__':
    logging.info("Starting Fleet Carrier API server")
    print("Fleet Carrier API server is starting...")
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error starting server: {e}")
    finally:
        logging.info("Server shutting down")
