import json
import os

class Dimension:
    def __init__(self, name):
        self.name = name
        self.load_dimension()
    
    def load_dimension(self):
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'dimensions', f'{self.name}.json')
        try:
            with open(file_path, 'r') as f:
                dimension_data = json.load(f)
                if self.name in dimension_data:
                    dimension_data = dimension_data[self.name]
                    self.title = dimension_data['title']
                    self.description = dimension_data['description']
                    self.properties = {}
                    # Store celestial bodies as properties
                    for body_name, body_data in dimension_data['bodies'].items():
                        self.properties[body_name] = body_data
                else:
                    raise ValueError(f"Dimension {self.name} not found in file")
        except FileNotFoundError:
            raise ValueError(f"Dimension file for {self.name} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in dimension file for {self.name}")

    @staticmethod
    def get_available_dimensions():
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'dimensions.json')
        try:
            with open(file_path, 'r') as f:
                dimensions_config = json.load(f)
                if 'enabled' in dimensions_config:
                    return dimensions_config['enabled']
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []