"""
Dimension class and celestial body definitions for interstellar travel.
"""
import json
import os
from pathlib import Path
from data_loader import DataLoader
from config import DIMENSIONS_DIRECTORY, DIMENSIONS_CONFIG

class Dimension:
    """
    Represents a dimension (star system) in the game universe.
    Contains properties like celestial bodies, coordinates, and description.
    """
    def __init__(self, name):
        """Initialize a dimension with the given name and load its data"""
        self.name = name
        self.properties = {}
        self.title = ""
        self.description = ""
        self.load_dimension()
    
    def load_dimension(self):
        """Load dimension data from the corresponding JSON file"""
        try:
            # Load the dimension data using the DataLoader
            dimension_data = DataLoader.load_dimension_data(self.name)
            
            # Set basic dimension properties
            self.title = dimension_data['title']
            self.description = dimension_data['description']
            
            # Store celestial bodies as properties
            for body_name, body_data in dimension_data['bodies'].items():
                # Normalize moon data structure if needed
                body_data = DataLoader.normalize_moon_data(body_data)
                # Store the body data
                self.properties[body_name] = body_data
                
            # Load stations for this dimension
            from station import load_stations_from_dimension
            load_stations_from_dimension({'bodies': self.properties}, self.name)
                
        except ValueError as e:
            raise ValueError(f"Failed to load dimension {self.name}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading dimension {self.name}: {str(e)}")

    @staticmethod
    def get_available_dimensions():
        """Get a list of all available dimensions"""
        return DataLoader.get_available_dimensions()
