import socket
import threading
import json
import os
import time
from pathlib import Path

class VideoSyncServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # {client_id: {'socket': socket, 'address': address, 'volume': 100}}
        self.admin = None
        self.playlist = []  # list of video file paths
        self.current_video_index = -1
        self.video_directory = Path('videos')
        self.video_directory.mkdir(exist_ok=True)
        self.is_playing = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        print(f"Server started on {self.host}:{self.port}")
        
        # Accept connections in a separate thread
        threading.Thread(target=self.accept_connections, daemon=True).start()
        
        try:
            while True:
                time.sleep(0.1)  # Main thread keeps the server running
        except KeyboardInterrupt:
            print("Server shutting down...")
            self.server_socket.close()

    def accept_connections(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()

    def handle_client(self, client_socket, address):
        try:
            # First message should identify if this is an admin or client
            data = client_socket.recv(1024).decode('utf-8')
            message = json.loads(data)
            
            if message.get('type') == 'admin_connect':
                if self.admin is None:
                    self.admin = {'socket': client_socket, 'address': address}
                    print(f"Admin connected from {address}")
                    self.send_to_admin({'type': 'client_list', 'clients': [{'id': cid, 'volume': info['volume']} for cid, info in self.clients.items()]})
                else:
                    # Only allow one admin
                    client_socket.send(json.dumps({'type': 'error', 'message': 'Admin already connected'}).encode('utf-8'))
                    client_socket.close()
                    return
                
                # Handle admin messages
                while True:
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    self.handle_admin_message(json.loads(data))
                
                # Admin disconnected
                print("Admin disconnected")
                self.admin = None
            
            elif message.get('type') == 'client_connect':
                client_id = message.get('id', str(address[0]) + '_' + str(address[1]))
                self.clients[client_id] = {'socket': client_socket, 'address': address, 'volume': 100}
                print(f"Client {client_id} connected from {address}")
                
                # Notify admin about the new client
                if self.admin:
                    self.send_to_admin({'type': 'client_connected', 'client': {'id': client_id, 'volume': 100}})
                
                # Handle client messages
                while True:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    self.handle_client_message(client_id, json.loads(data))
                
                # Client disconnected
                del self.clients[client_id]
                print(f"Client {client_id} disconnected")
                
                # Notify admin about client disconnection
                if self.admin:
                    self.send_to_admin({'type': 'client_disconnected', 'client_id': client_id})
            
            else:
                # Unknown connection type
                client_socket.send(json.dumps({'type': 'error', 'message': 'Unknown connection type'}).encode('utf-8'))
                client_socket.close()
        
        except Exception as e:
            print(f"Error handling connection: {e}")
            client_socket.close()

    def handle_admin_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'set_playlist':
            self.playlist = message.get('playlist', [])
            self.current_video_index = -1
            print(f"New playlist set: {len(self.playlist)} videos")
        
        elif msg_type == 'play':
            if not self.is_playing and self.playlist:
                self.is_playing = True
                self.current_video_index = 0 if self.current_video_index < 0 else self.current_video_index
                self.broadcast_to_clients({'type': 'play', 'video': self.playlist[self.current_video_index]})
                print(f"Playing video: {self.playlist[self.current_video_index]}")
        
        elif msg_type == 'pause':
            if self.is_playing:
                self.is_playing = False
                self.broadcast_to_clients({'type': 'pause'})
                print("Playback paused")
        
        elif msg_type == 'next':
            if self.playlist and self.current_video_index < len(self.playlist) - 1:
                self.current_video_index += 1
                self.broadcast_to_clients({'type': 'play', 'video': self.playlist[self.current_video_index]})
                print(f"Playing next video: {self.playlist[self.current_video_index]}")
        
        elif msg_type == 'previous':
            if self.playlist and self.current_video_index > 0:
                self.current_video_index -= 1
                self.broadcast_to_clients({'type': 'play', 'video': self.playlist[self.current_video_index]})
                print(f"Playing previous video: {self.playlist[self.current_video_index]}")
        
        elif msg_type == 'set_volume':
            client_id = message.get('client_id')
            volume = message.get('volume', 100)
            
            if client_id == 'all':
                # Set volume for all clients
                for cid in self.clients:
                    self.clients[cid]['volume'] = volume
                self.broadcast_to_clients({'type': 'set_volume', 'volume': volume})
                print(f"Set volume to {volume} for all clients")
            elif client_id in self.clients:
                # Set volume for specific client
                self.clients[client_id]['volume'] = volume
                self.send_to_client(client_id, {'type': 'set_volume', 'volume': volume})
                print(f"Set volume to {volume} for client {client_id}")
        
        elif msg_type == 'upload_video':
            # Handle video upload (simplified)
            video_name = message.get('name')
            video_data = message.get('data')
            # In a real implementation, you would handle file uploads more efficiently
            # For simplicity, we're assuming the video data can be transmitted in a single message
            with open(self.video_directory / video_name, 'wb') as f:
                f.write(video_data)
            print(f"Video uploaded: {video_name}")

    def handle_client_message(self, client_id, message):
        msg_type = message.get('type')
        
        if msg_type == 'status_update':
            # Client sending status information
            status = message.get('status')
            if self.admin:
                self.send_to_admin({'type': 'client_status', 'client_id': client_id, 'status': status})
        
        elif msg_type == 'video_ended':
            # Client finished playing a video
            if self.is_playing and self.current_video_index < len(self.playlist) - 1:
                # Automatically play the next video
                self.current_video_index += 1
                self.broadcast_to_clients({'type': 'play', 'video': self.playlist[self.current_video_index]})
                print(f"Playing next video: {self.playlist[self.current_video_index]}")
            elif self.current_video_index >= len(self.playlist) - 1:
                # End of playlist
                self.is_playing = False
                print("End of playlist reached")

    def send_to_admin(self, message):
        if self.admin:
            try:
                self.admin['socket'].send(json.dumps(message).encode('utf-8'))
            except:
                print("Error sending message to admin")
                self.admin = None

    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].send(json.dumps(message).encode('utf-8'))
            except:
                print(f"Error sending message to client {client_id}")
                del self.clients[client_id]
                if self.admin:
                    self.send_to_admin({'type': 'client_disconnected', 'client_id': client_id})

    def broadcast_to_clients(self, message):
        for client_id in list(self.clients.keys()):
            self.send_to_client(client_id, message)

if __name__ == "__main__":
    server = VideoSyncServer()
    server.start()
