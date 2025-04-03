import requests
import json
import time

class ChatClient:
    def __init__(self, server_url="http://localhost", port=5500):
        self.server_url = f"{server_url}:{port}"
        self.username = "Anonymous"
        self.last_message_index = 0
    
    def set_username(self, username):
        self.username = username
    
    def send_message(self, message):
        try:
            response = requests.post(
                f"{self.server_url}/api/send",
                json={"username": self.username, "message": message},
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_new_messages(self):
        try:
            response = requests.get(
                f"{self.server_url}/api/messages?since={self.last_message_index}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.last_message_index = data['total']
                return data['messages']
            return []
        except requests.exceptions.RequestException:
            return []
    
    def check_server(self):
        try:
            response = requests.get(f"{self.server_url}/api/ping", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
