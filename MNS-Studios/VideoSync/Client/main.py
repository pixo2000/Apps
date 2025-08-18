import socket
import json
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog  # Added simpledialog import
import os
import sys
import uuid

# Check if VLC is installed
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    

class VideoSyncClient:
    def __init__(self, server_host='localhost', server_port=5000):
        # Check if VLC is available before proceeding
        if not VLC_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "VLC Not Found", 
                "Python-VLC module is not installed. Please install it with:\n\n"
                "pip install python-vlc\n\n"
                "Also make sure VLC media player is installed on your system."
            )
            root.destroy()
            sys.exit(1)
            
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = str(uuid.uuid4())
        self.socket = None
        self.connected = False
        self.player = None
        self.volume = 100
        self.window = None
        self.status = "idle"
        
        # Initialize UI
        self.initialize_ui()
        
        # Initialize VLC
        self.initialize_vlc()
        
        # Connect to server
        self.connect_to_server()
        
        # Start UI main loop
        self.window.mainloop()

    def initialize_ui(self):
        self.window = tk.Tk()
        self.window.title("VideoSync Client")
        self.window.geometry("400x300")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.status_label = tk.Label(self.window, text="Status: Not connected")
        self.status_label.pack(pady=10)
        
        self.video_frame = tk.Frame(self.window, bg="black", width=400, height=225)
        self.video_frame.pack(pady=10)
        
        self.connect_button = tk.Button(self.window, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=5)
        
        self.fullscreen_button = tk.Button(self.window, text="Toggle Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(pady=5)
        
        # Volume slider
        self.volume_frame = tk.Frame(self.window)
        self.volume_frame.pack(pady=5)
        
        tk.Label(self.volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                      command=self.set_volume)
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.LEFT, padx=5)
        
        # Set up key bindings for ESC to exit fullscreen
        self.window.bind('<Escape>', lambda e: self.exit_fullscreen())
        
        # Flag for fullscreen state
        self.is_fullscreen = False

    def initialize_vlc(self):
        # Initialize VLC instance
        self.instance = vlc.Instance()
        # Create a MediaPlayer
        self.player = self.instance.media_player_new()
        
        # Get handle for the video frame
        if sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif sys.platform == "darwin":  # macOS
            self.player.set_nsobject(self.video_frame.winfo_id())
        else:  # Linux
            self.player.set_xwindow(self.video_frame.winfo_id())
        
        # Set initial volume
        self.player.audio_set_volume(self.volume)

    def connect_to_server(self):
        if self.connected:
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Send client connection message
            self.send_message({'type': 'client_connect', 'id': self.client_id})
            
            self.connected = True
            self.status_label.config(text="Status: Connected")
            self.connect_button.config(text="Disconnect", command=self.disconnect)
            
            # Start a thread to receive messages from the server
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Start sending periodic status updates
            threading.Thread(target=self.send_status_updates, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")

    def disconnect(self):
        if not self.connected:
            return
        
        try:
            if self.player.is_playing():
                self.player.stop()
            
            self.socket.close()
            self.connected = False
            self.status_label.config(text="Status: Disconnected")
            self.connect_button.config(text="Connect", command=self.connect_to_server)
            
        except Exception as e:
            print(f"Error during disconnect: {e}")

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    # Connection closed by server
                    self.disconnect()
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.disconnect()
                break

    def handle_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'play':
            video_path = message.get('video')
            self.play_video(video_path)
            self.status = "playing"
        
        elif msg_type == 'pause':
            if self.player.is_playing():
                self.player.pause()
            self.status = "paused"
        
        elif msg_type == 'set_volume':
            volume = message.get('volume', 100)
            self.volume = volume
            self.volume_slider.set(volume)
            self.player.audio_set_volume(volume)
            print(f"Volume set to {volume}")

    def play_video(self, video_path):
        try:
            # Create a Media object
            media = self.instance.media_new(video_path)
            # Set the media to the player
            self.player.set_media(media)
            # Play the video
            self.player.play()
            
            # Update status
            self.status_label.config(text=f"Status: Playing {os.path.basename(video_path)}")
            
            # Monitor for end of video
            threading.Thread(target=self.monitor_playback, daemon=True).start()
            
        except Exception as e:
            print(f"Error playing video: {e}")
            self.status = "error"

    def monitor_playback(self):
        # Wait a bit for player to start
        time.sleep(1)
        
        # Check if player is playing
        while self.player.is_playing() and self.connected:
            time.sleep(1)
        
        # Video ended (not due to stop/pause command)
        if self.connected and self.status == "playing":
            self.status = "idle"
            self.send_message({'type': 'video_ended'})
            self.status_label.config(text="Status: Video ended")

    def send_message(self, message):
        if not self.connected:
            return
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect()

    def send_status_updates(self):
        while self.connected:
            self.send_message({
                'type': 'status_update',
                'status': {
                    'playing': self.player.is_playing(),
                    'volume': self.volume,
                    'state': self.status
                }
            })
            time.sleep(5)  # Send update every 5 seconds

    def set_volume(self, val):
        try:
            volume = int(val)
            self.volume = volume
            self.player.audio_set_volume(volume)
            # Don't send to server as it might conflict with admin control
        except Exception as e:
            print(f"Error setting volume: {e}")

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        self.window.attributes('-fullscreen', True)
        self.is_fullscreen = True
        # Hide controls in fullscreen mode
        self.connect_button.pack_forget()
        self.fullscreen_button.pack_forget()
        self.volume_frame.pack_forget()
        # Resize video frame
        self.video_frame.config(width=self.window.winfo_width(), height=self.window.winfo_height())

    def exit_fullscreen(self):
        self.window.attributes('-fullscreen', False)
        self.is_fullscreen = False
        # Show controls again
        self.connect_button.pack(pady=5)
        self.fullscreen_button.pack(pady=5)
        self.volume_frame.pack(pady=5)
        # Reset video frame size
        self.video_frame.config(width=400, height=225)

    def on_close(self):
        self.disconnect()
        self.window.destroy()

if __name__ == "__main__":
    # Ask for server address on startup
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    server_host = simpledialog.askstring("Server Address", "Enter server IP address:", initialvalue="localhost")
    if not server_host:
        server_host = "localhost"
    
    root.destroy()
    
    client = VideoSyncClient(server_host=server_host)
