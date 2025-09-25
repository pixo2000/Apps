import socket
import json
import os
import hashlib
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileSyncClient:
    def __init__(self, host='localhost', port=8888, sync_folder='client2_sync_folder', client_name='Client2'):
        self.host = host
        self.port = port
        self.sync_folder = Path(sync_folder)
        self.client_name = client_name
        self.socket = None
        self.file_registry = {}  # {file_path: {'hash': str, 'mtime': float, 'size': int}}
        self.running = False
        self.observer = None
        
        # Create sync folder if it doesn't exist
        self.sync_folder.mkdir(exist_ok=True)
        
        # Initialize file registry
        self._scan_files()
        
        print(f"{self.client_name} initialized with sync folder: {self.sync_folder.absolute()}")
    
    def _scan_files(self):
        """Scan the sync folder and build file registry"""
        self.file_registry.clear()
        
        if not self.sync_folder.exists():
            return
            
        for file_path in self.sync_folder.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.sync_folder)
                self.file_registry[str(rel_path)] = self._get_file_info(file_path)
    
    def _get_file_info(self, file_path):
        """Get file information (hash, mtime, size)"""
        if not file_path.exists():
            return None
            
        stat = file_path.stat()
        with open(file_path, 'rb') as f:
            content = f.read()
            file_hash = hashlib.md5(content).hexdigest()
        
        return {
            'hash': file_hash,
            'mtime': stat.st_mtime,
            'size': stat.st_size
        }
    
    def _send_message(self, message_type, data):
        """Send a JSON message to server"""
        try:
            message = {
                'type': message_type,
                'data': data
            }
            json_message = json.dumps(message)
            message_length = len(json_message.encode('utf-8'))
            
            # Send length first, then message
            self.socket.send(message_length.to_bytes(4, 'big'))
            self.socket.send(json_message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _receive_message(self):
        """Receive a JSON message from server"""
        try:
            # Receive message length
            length_bytes = self.socket.recv(4)
            if not length_bytes:
                return None
            
            message_length = int.from_bytes(length_bytes, 'big')
            
            # Receive message
            message_data = b''
            while len(message_data) < message_length:
                chunk = self.socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return json.loads(message_data.decode('utf-8'))
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def _upload_file(self, file_path):
        """Upload a file to the server"""
        full_path = self.sync_folder / file_path
        
        if not full_path.exists():
            return
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            
            file_info = self._get_file_info(full_path)
            
            self._send_message('upload_file', {
                'path': str(file_path),
                'content': content.hex(),
                'info': file_info
            })
            
            # Update local registry
            self.file_registry[str(file_path)] = file_info
            
            print(f"Uploaded: {file_path}")
            
        except Exception as e:
            print(f"Error uploading file {file_path}: {e}")
    
    def _download_file(self, file_path):
        """Request a file from the server"""
        self._send_message('request_file', {'path': file_path})
    
    def _save_received_file(self, file_path, content_hex, file_info):
        """Save a file received from the server"""
        try:
            content = bytes.fromhex(content_hex)
            full_path = self.sync_folder / file_path
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(content)
            
            # Update registry
            self.file_registry[file_path] = file_info
            
            # Set modification time
            os.utime(full_path, (file_info['mtime'], file_info['mtime']))
            
            print(f"Downloaded: {file_path}")
            
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
    
    def _handle_server_messages(self):
        """Handle messages from server in a separate thread"""
        while self.running:
            try:
                message = self._receive_message()
                if not message:
                    break
                
                msg_type = message.get('type')
                data = message.get('data', {})
                
                if msg_type == 'file_registry':
                    # Server sent initial file registry
                    self._handle_initial_sync(data)
                
                elif msg_type == 'file_content':
                    # Server sent requested file
                    self._save_received_file(
                        data['path'],
                        data['content'],
                        data['info']
                    )
                
                elif msg_type == 'file_updated':
                    # Server notifies about file update from another client
                    server_info = data['info']
                    file_path = data['path']
                    local_info = self.file_registry.get(file_path)
                    
                    if not local_info or local_info['hash'] != server_info['hash']:
                        print(f"File updated on server: {file_path}")
                        self._download_file(file_path)
                
                elif msg_type == 'sync_updates':
                    # Server sent list of files to download
                    for file_path in data['files']:
                        self._download_file(file_path)
                
            except Exception as e:
                print(f"Error handling server message: {e}")
                break
    
    def _handle_initial_sync(self, server_registry):
        """Handle initial sync with server registry"""
        print("Starting initial synchronization...")
        
        # Files to download (missing or different on client)
        to_download = []
        
        # Files to upload (missing or different on server)
        to_upload = []
        
        # Check what needs to be downloaded
        for file_path, server_info in server_registry.items():
            local_info = self.file_registry.get(file_path)
            
            if not local_info or local_info['hash'] != server_info['hash']:
                to_download.append(file_path)
        
        # Check what needs to be uploaded
        for file_path, local_info in self.file_registry.items():
            server_info = server_registry.get(file_path)
            
            if not server_info or server_info['hash'] != local_info['hash']:
                # Only upload if local file is newer
                full_path = self.sync_folder / file_path
                if full_path.exists():
                    if not server_info or local_info['mtime'] > server_info['mtime']:
                        to_upload.append(file_path)
        
        # Send sync request to get files from server
        if to_download:
            print(f"Downloading {len(to_download)} files from server...")
            self._send_message('client_registry', self.file_registry)
        
        # Upload newer local files
        if to_upload:
            print(f"Uploading {len(to_upload)} files to server...")
            for file_path in to_upload:
                self._upload_file(file_path)
        
        if not to_download and not to_upload:
            print("All files are in sync!")
    
    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, client):
            self.client = client
            self._last_event = {}  # To avoid duplicate events
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            self._handle_file_event(event.src_path, 'modified')
        
        def on_created(self, event):
            if event.is_directory:
                return
            
            self._handle_file_event(event.src_path, 'created')
        
        def _handle_file_event(self, file_path, event_type):
            try:
                full_path = Path(file_path)
                
                # Check if file is in sync folder
                if not str(full_path).startswith(str(self.client.sync_folder)):
                    return
                
                # Avoid duplicate events
                current_time = time.time()
                if file_path in self._last_event:
                    if current_time - self._last_event[file_path] < 1:  # 1 second cooldown
                        return
                
                self._last_event[file_path] = current_time
                
                # Wait a moment for file operations to complete
                time.sleep(0.1)
                
                if full_path.exists() and full_path.is_file():
                    rel_path = full_path.relative_to(self.client.sync_folder)
                    
                    # Check if file actually changed
                    new_info = self.client._get_file_info(full_path)
                    old_info = self.client.file_registry.get(str(rel_path))
                    
                    if not old_info or old_info['hash'] != new_info['hash']:
                        print(f"File changed: {rel_path}")
                        
                        # Upload the changed file
                        if self.client.running and self.client.socket:
                            threading.Thread(
                                target=self.client._upload_file,
                                args=(rel_path,),
                                daemon=True
                            ).start()
                
            except Exception as e:
                print(f"Error handling file event: {e}")
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            print(f"{self.client_name} connected to server at {self.host}:{self.port}")
            
            # Start file monitoring
            event_handler = self.FileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.sync_folder), recursive=True)
            self.observer.start()
            
            # Start message handler thread
            message_thread = threading.Thread(target=self._handle_server_messages)
            message_thread.daemon = True
            message_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.socket:
            self.socket.close()
        
        print(f"{self.client_name} disconnected")
    
    def run(self):
        """Run the client"""
        if self.connect():
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{self.client_name} shutting down...")
            finally:
                self.disconnect()

if __name__ == "__main__":
    # You can change the sync folder path and client name here
    client = FileSyncClient(sync_folder='client2_sync_folder', client_name='Client2')
    
    # Install watchdog if not already installed
    try:
        import watchdog
    except ImportError:
        print("Installing watchdog for file monitoring...")
        os.system("pip install watchdog")
        import watchdog
    
    client.run()