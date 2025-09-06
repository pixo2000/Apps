from flask import Flask, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/api/weapons', methods=['GET'])
def get_weapons():
    # Create weapons data structure
    weapons_data = [
        {
            "uuid": "63e6c2b6-4a8e-869c-3d4c-e38355226584",
            "displayName": "Odin",
            "category": "EEquippableCategory::Heavy",
            "accessible": "yes"
        },
        {
            "uuid": "55d8a0f4-4274-ca67-fe2c-06ab45efdf58",
            "displayName": "Ares",
            "category": "EEquippableCategory::Heavy",
            "accessible": "yes"
        },
        {
            "uuid": "9c82e19d-4575-0200-1a81-3eacf00cf872",
            "displayName": "Vandal",
            "category": "EEquippableCategory::Rifle",
            "accessible": "yes"
        },
        {
            "uuid": "ae3de142-4d85-2547-dd26-4e90bed35cf7",
            "displayName": "Bulldog",
            "category": "EEquippableCategory::Rifle",
            "accessible": "yes"
        },
        {
            "uuid": "ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a",
            "displayName": "Phantom",
            "category": "EEquippableCategory::Rifle",
            "accessible": "yes"
        },
        {
            "uuid": "ec845bf4-4f79-ddda-a3da-0db3774b2794",
            "displayName": "Judge",
            "category": "EEquippableCategory::Shotgun",
            "accessible": "yes"
        },
        {
            "uuid": "910be174-449b-c412-ab22-d0873436b21b",
            "displayName": "Bucky",
            "category": "EEquippableCategory::Shotgun",
            "accessible": "yes"
        },
        {
            "uuid": "44d4e95c-4157-0037-81b2-17841bf2e8e3",
            "displayName": "Frenzy",
            "category": "EEquippableCategory::Sidearm",
            "accessible": "yes"
        },
        {
            "uuid": "29a0cfab-485b-f5d5-779a-b59f85e204a8",
            "displayName": "Classic",
            "category": "EEquippableCategory::Sidearm",
            "accessible": "yes"
        },
        {
            "uuid": "1baa85b4-4c70-1284-64bb-6481dfc3bb4e",
            "displayName": "Ghost",
            "category": "EEquippableCategory::Sidearm",
            "accessible": "yes"
        },
        {
            "uuid": "e336c6b8-418d-9340-d77f-7a9e4cfe0702",
            "displayName": "Sheriff",
            "category": "EEquippableCategory::Sidearm",
            "accessible": "yes"
        },
        {
            "uuid": "42da8ccc-40d5-affc-beec-15aa47b42eda",
            "displayName": "Shorty",
            "category": "EEquippableCategory::Sidearm",
            "accessible": "yes"
        },
        {
            "uuid": "a03b24d3-4319-996d-0f8c-94bbfba1dfc7",
            "displayName": "Operator",
            "category": "EEquippableCategory::Sniper",
            "accessible": "yes"
        },
        {
            "uuid": "4ade7faa-4cf1-8376-95ef-39884480959b",
            "displayName": "Guardian",
            "category": "EEquippableCategory::Rifle",
            "accessible": "yes"
        },
        {
            "uuid": "5f0aaf7a-4289-3998-d5ff-eb9a5cf7ef5c",
            "displayName": "Outlaw",
            "category": "EEquippableCategory::Sniper",
            "accessible": "yes"
        },
        {
            "uuid": "c4883e50-4494-202c-3ec3-6b8a9284f00b",
            "displayName": "Marshal",
            "category": "EEquippableCategory::Sniper",
            "accessible": "yes"
        },
        {
            "uuid": "462080d1-4035-2937-7c09-27aa2a5c27a7",
            "displayName": "Spectre",
            "category": "EEquippableCategory::SMG",
            "accessible": "yes"
        },
        {
            "uuid": "f7e1b454-4ad4-1063-ec0a-159e56b58941",
            "displayName": "Stinger",
            "category": "EEquippableCategory::SMG",
            "accessible": "yes"
        },
        {
            "uuid": "abcd1234-5678-90ef-ab12-34567890cdef",
            "displayName": "Cyclone",
            "category": "EEquippableCategory::SMG",
            "accessible": "no"
        },
        {
            "uuid": "2f59173c-4bed-b6c3-2191-dea9b58be9c7",
            "displayName": "Melee",
            "category": "EEquippableCategory::Melee",
            "accessible": "yes"
        }
    ]
    
    # Return response with status code and data
    return jsonify({
        "status": 200,
        "data": weapons_data
    })

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Returns metadata about the API including current time and user information"""
    return jsonify({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "user": {
            "login": "pixo2000",
            "repositories": [
                {"name": "pixo2000/Apps", "url": "https://github.com/pixo2000/Apps"},
                {"name": "pixo2000/Obsidian", "url": "https://github.com/pixo2000/Obsidian"},
                {"name": "pixo2000/Spacer", "url": "https://github.com/pixo2000/Spacer"},
                {"name": "pixo2000/VoidCapes", "url": "https://github.com/pixo2000/VoidCapes"},
                {"name": "pixo2000/Informatik", "url": "https://github.com/pixo2000/Informatik"}
            ]
        },
        "api_version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(debug=True)