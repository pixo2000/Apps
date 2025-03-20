"""
Dimension loading and universe data management functions.
"""
import json
import os
import sys
from pathlib import Path
from config import DIMENSIONS_DIRECTORY, DIMENSIONS_CONFIG

class DataLoader:
    """Handles loading of game data like dimensions and celestial bodies"""
    
    @staticmethod
    def _get_base_path():
        """Get the base path for resources, works for dev and PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = Path(sys._MEIPASS)
        except Exception:
            # We are not running as a bundled executable
            base_path = Path(os.path.dirname(__file__))
        return base_path
    
    @staticmethod
    def load_dimension_data(dimension_name):
        """Load data for a specific dimension"""
        # Get base path that works with PyInstaller
        base_path = DataLoader._get_base_path()
        dimensions_dir = base_path / DIMENSIONS_DIRECTORY
        file_path = dimensions_dir / f'{dimension_name}.json'
        
        # Ensure the dimensions directory exists
        if not dimensions_dir.exists():
            os.makedirs(dimensions_dir)
            print(f"Created dimensions directory: {dimensions_dir}")
        
        try:
            with open(file_path, 'r') as f:
                dimension_data = json.load(f)
                if dimension_name in dimension_data:
                    return dimension_data[dimension_name]
                else:
                    # If the dimension name doesn't exist in the file, create it with default data
                    default_data = DataLoader.create_default_dimension(dimension_name)
                    DataLoader.save_dimension_data(dimension_name, default_data)
                    return default_data
        except FileNotFoundError:
            # If the file doesn't exist, create it with default data
            default_data = DataLoader.create_default_dimension(dimension_name)
            DataLoader.save_dimension_data(dimension_name, default_data)
            return default_data
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in dimension file for {dimension_name}")
    
    @staticmethod
    def create_default_dimension(dimension_name):
        """Create a default structure for a new dimension"""
        return {
            "title": f"System {dimension_name}",
            "description": f"A newly discovered star system designated {dimension_name}.",
            "bodies": {
                f"{dimension_name} Star": {
                    "type": "Star",
                    "Coordinates": {"x": "0", "y": "0"},
                    "size": {"width": "3", "height": "3"},
                    "description": "The central star of this system."
                },
                f"{dimension_name} Planet": {
                    "type": "Planet",
                    "Coordinates": {"x": "10", "y": "0"},
                    "size": {"width": "2", "height": "2"},
                    "description": "A rocky planet orbiting the star."
                }
            }
        }
    
    @staticmethod
    def save_dimension_data(dimension_name, dimension_data):
        """Save dimension data to a JSON file"""
        # Updated path handling for PyInstaller compatibility
        base_path = DataLoader._get_base_path()
        dimensions_dir = base_path / DIMENSIONS_DIRECTORY
        file_path = dimensions_dir / f'{dimension_name}.json'
        
        # Create the file with the dimension data
        with open(file_path, 'w') as f:
            json.dump({dimension_name: dimension_data}, f, indent=4)
        
        # Update the dimensions config to include this dimension
        DataLoader.update_dimensions_config(dimension_name)
        
        print(f"Created new dimension file for {dimension_name}")
    
    @staticmethod
    def update_dimensions_config(dimension_name):
        """Add a dimension to the enabled dimensions in the config"""
        # Updated path handling for PyInstaller compatibility
        base_path = DataLoader._get_base_path() 
        config_path = base_path / DIMENSIONS_CONFIG
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"enabled": []}
            
            if "enabled" not in config:
                config["enabled"] = []
            
            if dimension_name not in config["enabled"]:
                config["enabled"].append(dimension_name)
                
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error updating dimensions config: {str(e)}")

    @staticmethod
    def get_available_dimensions():
        """Get a list of all available dimensions"""
        # Updated path handling for PyInstaller compatibility
        base_path = DataLoader._get_base_path()
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
