import json
import os

class Dimension:
    def __init__(self, name):
        self.name = name
        self.load_dimension()
    
    def load_dimension(self):
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'dimensions.json')
        with open(file_path, 'r') as f:
            dimensions = json.load(f)
            if self.name in dimensions:
                dimension_data = dimensions[self.name]
                self.title = dimension_data['title']
                self.description = dimension_data['description']
                self.properties = {}
                # Store celestial bodies as properties
                for body_name, body_data in dimension_data['properties'].items():
                    self.properties[body_name] = body_data
            else:
                raise ValueError(f"Dimension {self.name} not found")

    @staticmethod # why statismethod
    def get_available_dimensions():
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'dimensions.json')
        with open(file_path, 'r') as f:
            dimensions = json.load(f)
            return list(dimensions.keys())