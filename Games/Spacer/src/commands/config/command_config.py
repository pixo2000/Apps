"""
Command configuration loader for Spacer game.
"""
import os
import yaml
import json

class CommandConfig:
    def __init__(self, config_dir=None):
        """
        Initialize the command configuration loader
        
        Args:
            config_dir (str): Directory containing command configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "commands")
        self.configs = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_all_configs(self):
        """Load all command configuration files"""
        if not os.path.exists(self.config_dir):
            print(f"Warning: Command config directory not found at {self.config_dir}")
            return {}
            
        for filename in os.listdir(self.config_dir):
            # Load YAML files
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                command_name = os.path.splitext(filename)[0]
                config_path = os.path.join(self.config_dir, filename)
                try:
                    with open(config_path, 'r') as f:
                        self.configs[command_name] = yaml.safe_load(f)
                except Exception as e:
                    print(f"Error loading config {filename}: {e}")
            
            # Load JSON files
            elif filename.endswith('.json'):
                command_name = os.path.splitext(filename)[0]
                config_path = os.path.join(self.config_dir, filename)
                try:
                    with open(config_path, 'r') as f:
                        self.configs[command_name] = json.load(f)
                except Exception as e:
                    print(f"Error loading config {filename}: {e}")
        
        return self.configs
    
    def get_config(self, command_name):
        """Get configuration for a specific command"""
        if not self.configs:
            self.load_all_configs()
        
        return self.configs.get(command_name, {})
    
    def save_config(self, command_name, config_data, format='yaml'):
        """Save configuration for a command"""
        if format.lower() == 'yaml':
            filename = f"{command_name}.yaml"
            file_path = os.path.join(self.config_dir, filename)
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        elif format.lower() == 'json':
            filename = f"{command_name}.json"
            file_path = os.path.join(self.config_dir, filename)
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        else:
            raise ValueError("Format must be either 'yaml' or 'json'")
        
        # Update in-memory config
        self.configs[command_name] = config_data
