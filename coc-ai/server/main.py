from flask import Flask, request, jsonify, send_from_directory
import os
import json
from flask_cors import CORS

app = Flask(__name__, static_folder='../client')
CORS(app)  # Enable cross-origin requests

# Simple in-memory storage for game data (in production, use a database)
game_data = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/save', methods=['POST'])
def save_game():
    data = request.json
    
    # In a real application, you'd validate the user and data
    player_id = request.headers.get('X-Player-ID', 'default_player')
    
    game_data[player_id] = data
    
    # Save to file for persistence (optional)
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, f'{player_id}.json'), 'w') as f:
        json.dump(data, f)
    
    return jsonify({"success": True, "message": "Game saved successfully"})

@app.route('/api/load', methods=['GET'])
def load_game():
    player_id = request.headers.get('X-Player-ID', 'default_player')
    
    # Try to find from memory
    if player_id in game_data:
        return jsonify({"success": True, "data": game_data[player_id]})
    
    # Try to load from file
    data_file = os.path.join(os.path.dirname(__file__), 'data', f'{player_id}.json')
    
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            game_data[player_id] = data
            return jsonify({"success": True, "data": data})
    
    # No saved data found
    return jsonify({
        "success": False, 
        "message": "No saved game found",
        "data": {
            "resources": {"gold": 1000, "elixir": 1000},
            "buildings": [],
            "troops": []
        }
    })

@app.route('/api/attack', methods=['GET'])
def get_enemy_village():
    # In a real game, this would find another player's village
    # For this demo, we'll generate a random village
    buildings = []
    building_types = ['townhall', 'goldmine', 'elixircollector', 'cannon']
    
    # Add town hall
    buildings.append({
        "type": "townhall",
        "row": 4,
        "col": 4,
        "health": 1000
    })
    
    # Add some random buildings
    import random
    for _ in range(5):
        building_type = random.choice(building_types)
        row = random.randint(0, 9)
        col = random.randint(0, 9)
        
        # Simple check to avoid overlap with town hall
        if not (row >= 4 and row <= 5 and col >= 4 and col <= 5):
            buildings.append({
                "type": building_type,
                "row": row,
                "col": col,
                "health": 300 if building_type != "cannon" else 500
            })
    
    return jsonify({
        "success": True,
        "village": {
            "buildings": buildings,
            "loot": {
                "gold": random.randint(500, 2000),
                "elixir": random.randint(500, 2000)
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
