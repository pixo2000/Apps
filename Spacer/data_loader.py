"""
Dimension loading and universe data management functions.
"""
import json
import os
from pathlib import Path
from config import DIMENSIONS_DIRECTORY, DIMENSIONS_CONFIG

class DataLoader:
    """Handles loading of game data like dimensions and celestial bodies"""
    
    @staticmethod
    def load_dimension_data(dimension_name):
        """Load data for a specific dimension"""
        base_path = Path(os.path.dirname(os.path.dirname(__file__)))
        file_path = base_path / DIMENSIONS_DIRECTORY / f'{dimension_name}.json'
        
        try:
            with open(file_path, 'r') as f:
                dimension_data = json.load(f)
                if dimension_name in dimension_data:
                    return dimension_data[dimension_name]
                else:
                    raise ValueError(f"Dimension {dimension_name} not found in file")
        except FileNotFoundError:
            raise ValueError(f"Dimension file for {dimension_name} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in dimension file for {dimension_name}")
    
    @staticmethod
    def get_available_dimensions():
        """Get a list of all available dimensions"""
        base_path = Path(os.path.dirname(os.path.dirname(__file__)))
        file_path = base_path / DIMENSIONS_CONFIG
        
        try:
            with open(file_path, 'r') as f:
                dimensions_config = json.load(f)
                if 'enabled' in dimensions_config:
                    return dimensions_config['enabled']
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def normalize_moon_data(body_data):
        """Normalize moon data to ensure consistent format"""
        if "Moons" in body_data:
            # Check if Moons is a dictionary (new format) or a list (old format)
            if isinstance(body_data["Moons"], list):
                # Convert old format to new format
                body_data["Moons"] = {
                    moon_name: {
                        "type": "Moon",
                        "Coordinates": {"x": "0", "y": "0"},
                        "size": {"width": "1", "height": "1"}
                    } for moon_name in body_data["Moons"]
                }
        return body_data
