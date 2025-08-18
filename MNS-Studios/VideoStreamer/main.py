import easywebdav
import os
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = os.getenv('WEBDAV_USERNAME')
password = os.getenv('WEBDAV_PASSWORD')
host = os.getenv('WEBDAV_HOST')
protocol = os.getenv('WEBDAV_PROTOCOL')
port = int(os.getenv('WEBDAV_PORT'))

def create_webdav_connection():
    """Create WebDAV connection using environment variables"""
    try:
        webdav = easywebdav.connect(
            host=host,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            path=f'/remote.php/dav/files/{username}/'
        )
        return webdav
    except Exception as e:
        print(f"Failed to create WebDAV connection: {e}")
        return None

def test_connection(webdav_client):
    """Test a WebDAV connection"""
    try:
        print("\nTesting config directory access...")
        try:
            config_files = webdav_client.ls('/Konzept MNS-Studios Krissel/')
            print("Config directory contents:")
            for file in config_files:
                print(f"  - {file.name}")
        except Exception as e:
            print(f"Error accessing config directory: {e}")
            
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def download_config(webdav_client, config_path='/Konzept MNS-Studios Krissel/Fernsehr-Server/config.json'):
    """Download and parse config.json from WebDAV server"""
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            webdav_client.download(config_path, temp_file.name)
            temp_file_path = temp_file.name
        
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        os.unlink(temp_file_path)
        return config_data
    except Exception as e:
        print(f"Error downloading config: {e}")
        return None

def upload_config(webdav_client, config_data, config_path='/Konzept MNS-Studios Krissel/Fernsehr-Server/config.json'):
    """Upload updated config.json to WebDAV server"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(config_data, temp_file, indent=2, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        webdav_client.upload(temp_file_path, config_path)
        os.unlink(temp_file_path)
        print("Config updated successfully!")
        return True
    except Exception as e:
        print(f"Error uploading config: {e}")
        return False

def update_config_value(config_data, key_path, new_value):
    """Update a nested config value using dot notation (e.g., 'server.port')"""
    keys = key_path.split('.')
    current = config_data
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the final value
    current[keys[-1]] = new_value
    return config_data

def config_management_tool(webdav_client):
    """Interactive config management tool"""
    config_path = '/Konzept MNS-Studios Krissel/Fernsehr-Server/config.json'
    
    print("\n=== Config Management Tool ===")
    config_data = download_config(webdav_client, config_path)
    
    if not config_data:
        print("Failed to download config file.")
        return
    
    print("Current config:")
    print(json.dumps(config_data, indent=2, ensure_ascii=False))
    
    while True:
        print("\nOptions:")
        print("1. Update a value")
        print("2. View current config")
        print("3. Save and exit")
        print("4. Exit without saving")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            key_path = input("Enter key path (e.g., 'server.port' or 'database.host'): ").strip()
            new_value = input("Enter new value: ").strip()
            
            # Try to convert to appropriate type
            try:
                if new_value.lower() == 'true':
                    new_value = True
                elif new_value.lower() == 'false':
                    new_value = False
                elif new_value.isdigit():
                    new_value = int(new_value)
                elif '.' in new_value and new_value.replace('.', '').isdigit():
                    new_value = float(new_value)
            except:
                pass  # Keep as string
            
            config_data = update_config_value(config_data, key_path, new_value)
            print(f"Updated {key_path} = {new_value}")
            
        elif choice == '2':
            print("\nCurrent config:")
            print(json.dumps(config_data, indent=2, ensure_ascii=False))
            
        elif choice == '3':
            if upload_config(webdav_client, config_data, config_path):
                print("Config saved successfully!")
            break
            
        elif choice == '4':
            print("Exiting without saving.")
            break

def list_files(webdav_client, directory_path='/'):
    """Liste Dateien im Verzeichnis mit Error Handling"""
    try:
        print(f"Attempting to list files in: {directory_path}")
        files = webdav_client.ls(directory_path)
        print(f"Files in {directory_path}:")
        for file in files:
            print(f"  - {file.name}")
    except easywebdav.client.OperationFailed as e:
        print(f"WebDAV Operation Failed: {e}")
        print("This might indicate:")
        print("- The directory doesn't exist")
        print("- Insufficient permissions") 
        print("- Incorrect path format")
    except Exception as e:
        print(f"Unexpected error: {e}")

def list_videos_by_date(webdav_client):
    """List all videos from the Ablage directory sorted by date (newest first)"""
    video_path = '/Konzept MNS-Studios Krissel/Ablage Filmaterial, Fertige Filme/'
    
    try:
        print(f"\nListing videos from: {video_path}")
        files = webdav_client.ls(video_path)
        
        # Filter for video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        video_files = []
        
        for file in files:
            if any(file.name.lower().endswith(ext) for ext in video_extensions):
                video_files.append(file)
        
        # Sort by modification date (newest first)
        video_files.sort(key=lambda x: x.mtime if hasattr(x, 'mtime') else 0, reverse=True)
        
        print(f"\nFound {len(video_files)} video files:")
        print("-" * 80)
        
        for i, video in enumerate(video_files, 1):
            # Format date if available
            date_str = "Unknown date"
            if hasattr(video, 'mtime') and video.mtime:
                try:
                    from datetime import datetime
                    date_str = datetime.fromtimestamp(video.mtime).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_str = str(video.mtime)
            
            # Format file size if available
            size_str = "Unknown size"
            if hasattr(video, 'size') and video.size:
                size_mb = video.size / (1024 * 1024)
                if size_mb > 1024:
                    size_str = f"{size_mb/1024:.1f} GB"
                else:
                    size_str = f"{size_mb:.1f} MB"
            
            print(f"{i:3d}. {video.name}")
            print(f"     Date: {date_str}")
            print(f"     Size: {size_str}")
            print()
            
    except Exception as e:
        print(f"Error listing videos: {e}")
        print("Trying alternative paths...")
        
        # Try URL-encoded path
        try:
            encoded_path = '/Konzept%20MNS-Studios%20Krissel/Ablage%20Filmaterial%2c%20Fertige%20Filme/'
            print(f"Trying encoded path: {encoded_path}")
            files = webdav_client.ls(encoded_path)
            print(f"Success! Found {len(files)} items in encoded path")
            for file in files:
                print(f"  - {file.name}")
        except Exception as e2:
            print(f"Encoded path also failed: {e2}")

if __name__ == "__main__":
    print("Establishing WebDAV connection...")
    
    # Create connection
    webdav = create_webdav_connection()
    
    if webdav and test_connection(webdav):
        print("\nWebDAV connection successful!")
        
        # List videos by date
        list_videos_by_date(webdav)
        
        # Start config management tool
        config_management_tool(webdav)
        
    else:
        print("WebDAV connection failed. Please check your .env file and credentials.")