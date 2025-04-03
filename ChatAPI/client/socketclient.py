import socketio
import time

class WebSocketClient:
    def __init__(self, server_url="http://localhost", port=5500):
        self.server_url = server_url
        self.port = port
        self.username = "Anonymous"
        self.sio = socketio.Client()
        self.connected = False
        self.message_callback = None
        self.setup_events()
        
    def setup_events(self):
        @self.sio.event
        def connect():
            self.connected = True
            print("Connected to server")
        
        @self.sio.event
        def disconnect():
            self.connected = False
            print("Disconnected from server")
            
        @self.sio.on('new_message')
        def on_new_message(data):
            if self.message_callback:
                self.message_callback([data])
                
        @self.sio.on('message_history')
        def on_message_history(data):
            if self.message_callback and 'messages' in data:
                self.message_callback(data['messages'])
    
    def connect_to_server(self):
        try:
            url = f"{self.server_url}:{self.port}"
            if not self.connected:
                self.sio.connect(url)
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connected:
            self.sio.disconnect()
    
    def set_username(self, username):
        self.username = username
        return True
    
    def send_message(self, message):
        if not self.connected:
            return False
        try:
            self.sio.emit('message', {
                'username': self.username,
                'message': message
            })
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_message_history(self, since=0):
        if not self.connected:
            return False
        try:
            self.sio.emit('get_messages', {'since': since})
            return True
        except Exception as e:
            print(f"Error getting messages: {e}")
            return False
    
    def register_message_callback(self, callback):
        self.message_callback = callback
    
    def check_server(self):
        return self.connect_to_server()