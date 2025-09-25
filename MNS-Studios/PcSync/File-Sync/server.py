import socket
import threading
import json
import os
import hashlib
import time
from pathlib import Path
import shutil

class FileSyncServer:
    def __init__(self, host='localhost', port=8888, sync_folder='server_sync_folder'):
        self.host = host
        self.port = port
        self.sync_folder = Path(sync_folder)
        self.clients = []
        self.file_registry = {}  # {file_path: {'hash': str, 'mtime': float, 'size': int}}
        
        # Create sync folder if it doesn't exist
        self.sync_folder.mkdir(exist_ok=True)
        
        # Initialize file registry
        self._scan_files()
        
        print(f"Server initialized with sync folder: {self.sync_folder.absolute()}")
    
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
    
    def _send_message(self, client_socket, message_type, data):
        """Send a JSON message to client"""
        try:
            message = {
                'type': message_type,
                'data': data
            }
            json_message = json.dumps(message)
            message_length = len(json_message.encode('utf-8'))
            
            # Send length first, then message
            client_socket.send(message_length.to_bytes(4, 'big'))
            client_socket.send(json_message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _receive_message(self, client_socket):
        """Receive a JSON message from client"""
        try:
            # Receive message length
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                return None
            
            message_length = int.from_bytes(length_bytes, 'big')
            
            # Receive message
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return json.loads(message_data.decode('utf-8'))
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def _send_file(self, client_socket, file_path):
        """Send file content to client"""
        full_path = self.sync_folder / file_path
        
        if not full_path.exists():
            self._send_message(client_socket, 'file_not_found', {'path': file_path})
            return
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            
            file_info = self._get_file_info(full_path)
            self._send_message(client_socket, 'file_content', {
                'path': file_path,
                'content': content.hex(),
                'info': file_info
            })
        except Exception as e:
            print(f"Error sending file {file_path}: {e}")
    
    def _receive_file(self, client_socket, file_path, content_hex, file_info):
        """Receive file from client and update server"""
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
            
            print(f"Updated file: {file_path}")
            
            # Notify other clients about the update
            self._notify_clients_file_update(file_path, exclude_client=client_socket)
            
        except Exception as e:
            print(f"Error receiving file {file_path}: {e}")
    
    def _notify_clients_file_update(self, file_path, exclude_client=None):
        """Notify all clients (except sender) about file update"""
        file_info = self.file_registry.get(file_path)
        if not file_info:
            return
        
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            if client != exclude_client:
                try:
                    self._send_message(client, 'file_updated', {
                        'path': file_path,
                        'info': file_info
                    })
                except:
                    # Remove disconnected client
                    if client in self.clients:
                        self.clients.remove(client)
    
    def _handle_client(self, client_socket, address):
        """Handle individual client connection"""
        print(f"Client connected: {address}")
        self.clients.append(client_socket)
        
        try:
            # Send initial file list
            self._send_message(client_socket, 'file_registry', self.file_registry)
            
            while True:
                message = self._receive_message(client_socket)
                if not message:
                    break
                
                msg_type = message.get('type')
                data = message.get('data', {})
                
                if msg_type == 'request_file':
                    self._send_file(client_socket, data['path'])
                
                elif msg_type == 'upload_file':
                    self._receive_file(
                        client_socket,
                        data['path'],
                        data['content'],
                        data['info']
                    )
                
                elif msg_type == 'client_registry':
                    # Client sends their file registry for comparison
                    self._handle_sync_request(client_socket, data)
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"Client disconnected: {address}")
    
    def _handle_sync_request(self, client_socket, client_registry):
        """Handle client sync request by comparing registries"""
        updates_needed = []
        
        # Check which files need to be sent to client
        for file_path, server_info in self.file_registry.items():
            client_info = client_registry.get(file_path)
            
            if not client_info or client_info['hash'] != server_info['hash']:
                updates_needed.append(file_path)
        
        # Send update list to client
        self._send_message(client_socket, 'sync_updates', {'files': updates_needed})
    
    def start(self):
        """Start the server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"File sync server started on {self.host}:{self.port}")
        print(f"Sync folder: {self.sync_folder.absolute()}")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    # You can change the sync folder path here
    server = FileSyncServer(sync_folder='server_sync_folder')
    server.start()