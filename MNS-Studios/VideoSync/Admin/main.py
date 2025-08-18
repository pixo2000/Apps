import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from pathlib import Path

class VideoSyncAdmin:
    def __init__(self, server_host='localhost', server_port=5000):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.playlist = []  # List of video paths
        self.clients = {}  # {client_id: {'volume': volume, 'status': status}}
        
        # Initialize UI
        self.initialize_ui()
        
        # Connect to server
        self.connect_to_server()
        
        # Start UI main loop
        self.root.mainloop()

    def initialize_ui(self):
        self.root = tk.Tk()
        self.root.title("VideoSync Admin Panel")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame with two columns
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column for playlist
        playlist_frame = ttk.LabelFrame(main_frame, text="Playlist")
        playlist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Playlist controls
        playlist_controls = ttk.Frame(playlist_frame)
        playlist_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(playlist_controls, text="Add Video", command=self.add_video).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_controls, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_controls, text="Clear All", command=self.clear_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_controls, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_controls, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=2)
        
        # Playlist listbox
        self.playlist_listbox = tk.Listbox(playlist_frame, selectmode=tk.SINGLE)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Playback controls
        playback_controls = ttk.Frame(playlist_frame)
        playback_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(playback_controls, text="Play", command=self.play).pack(side=tk.LEFT, padx=2)
        ttk.Button(playback_controls, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=2)
        ttk.Button(playback_controls, text="Previous", command=self.previous).pack(side=tk.LEFT, padx=2)
        ttk.Button(playback_controls, text="Next", command=self.next).pack(side=tk.LEFT, padx=2)
        
        # Right column for client management
        client_frame = ttk.LabelFrame(main_frame, text="Clients")
        client_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Server connection controls
        connection_frame = ttk.Frame(client_frame)
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(connection_frame, text="Server:").pack(side=tk.LEFT, padx=2)
        self.server_entry = ttk.Entry(connection_frame)
        self.server_entry.insert(0, self.server_host)
        self.server_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=2)
        
        # Client list with treeview
        self.client_tree = ttk.Treeview(client_frame, columns=("ID", "Status", "Volume"))
        self.client_tree.heading("#0", text="")
        self.client_tree.heading("ID", text="Client ID")
        self.client_tree.heading("Status", text="Status")
        self.client_tree.heading("Volume", text="Volume")
        self.client_tree.column("#0", width=0, stretch=tk.NO)
        self.client_tree.column("ID", width=150)
        self.client_tree.column("Status", width=100)
        self.client_tree.column("Volume", width=70)
        self.client_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Client volume controls
        volume_frame = ttk.Frame(client_frame)
        volume_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT, padx=2)
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        ttk.Button(volume_frame, text="Set Volume", command=self.set_client_volume).pack(side=tk.LEFT, padx=2)
        ttk.Button(volume_frame, text="Set All Volumes", command=self.set_all_volumes).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected to server")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def connect_to_server(self):
        if self.connected:
            self.disconnect()
            return
        
        server_host = self.server_entry.get()
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_host, self.server_port))
            
            # Send admin connection message
            self.send_message({'type': 'admin_connect'})
            
            self.connected = True
            self.status_var.set(f"Connected to server at {server_host}:{self.server_port}")
            self.connect_button.config(text="Disconnect")
            
            # Start a thread to receive messages from the server
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
            self.status_var.set("Connection failed")

    def disconnect(self):
        if not self.connected:
            return
        
        try:
            self.socket.close()
            self.connected = False
            self.status_var.set("Disconnected from server")
            self.connect_button.config(text="Connect")
            self.clear_client_list()
            
        except Exception as e:
            print(f"Error during disconnect: {e}")

    def send_message(self, message):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Not connected to server. Please connect first.")
            return
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect()

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
        
        if msg_type == 'client_list':
            # Update client list
            self.clear_client_list()
            clients = message.get('clients', [])
            for client in clients:
                client_id = client.get('id')
                volume = client.get('volume', 100)
                self.clients[client_id] = {'volume': volume, 'status': 'unknown'}
                self.client_tree.insert("", tk.END, values=(client_id, "Connected", volume))
        
        elif msg_type == 'client_connected':
            # Add new client to the list
            client = message.get('client', {})
            client_id = client.get('id')
            volume = client.get('volume', 100)
            self.clients[client_id] = {'volume': volume, 'status': 'connected'}
            self.client_tree.insert("", tk.END, values=(client_id, "Connected", volume))
            self.status_var.set(f"Client {client_id} connected")
        
        elif msg_type == 'client_disconnected':
            # Remove client from the list
            client_id = message.get('client_id')
            if client_id in self.clients:
                del self.clients[client_id]
                # Find and remove from treeview
                for item in self.client_tree.get_children():
                    if self.client_tree.item(item)['values'][0] == client_id:
                        self.client_tree.delete(item)
                        break
                self.status_var.set(f"Client {client_id} disconnected")
        
        elif msg_type == 'client_status':
            # Update client status
            client_id = message.get('client_id')
            status = message.get('status', {})
            
            if client_id in self.clients:
                self.clients[client_id]['status'] = status
                
                # Update in treeview
                for item in self.client_tree.get_children():
                    if self.client_tree.item(item)['values'][0] == client_id:
                        playing_status = "Playing" if status.get('playing', False) else "Idle"
                        self.client_tree.item(item, values=(client_id, playing_status, status.get('volume', 100)))
                        break
        
        elif msg_type == 'error':
            # Display error message
            messagebox.showerror("Server Error", message.get('message', 'Unknown error'))

    def clear_client_list(self):
        # Clear the client treeview
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        self.clients = {}

    def add_video(self):
        # Open file dialog to select video files
        filepaths = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=(("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv"), ("All files", "*.*"))
        )
        
        if not filepaths:
            return
        
        # Add selected files to playlist
        for path in filepaths:
            self.playlist.append(path)
            self.playlist_listbox.insert(tk.END, os.path.basename(path))
        
        # Send updated playlist to server
        self.update_server_playlist()

    def remove_selected(self):
        # Remove selected video from playlist
        selected = self.playlist_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        self.playlist.pop(index)
        self.playlist_listbox.delete(index)
        
        # Send updated playlist to server
        self.update_server_playlist()

    def clear_playlist(self):
        # Clear the entire playlist
        self.playlist = []
        self.playlist_listbox.delete(0, tk.END)
        
        # Send updated playlist to server
        self.update_server_playlist()

    def move_up(self):
        # Move selected item up in the playlist
        selected = self.playlist_listbox.curselection()
        if not selected or selected[0] == 0:
            return
        
        index = selected[0]
        item = self.playlist.pop(index)
        self.playlist.insert(index - 1, item)
        
        # Update listbox
        item_text = self.playlist_listbox.get(index)
        self.playlist_listbox.delete(index)
        self.playlist_listbox.insert(index - 1, item_text)
        self.playlist_listbox.selection_set(index - 1)
        
        # Send updated playlist to server
        self.update_server_playlist()

    def move_down(self):
        # Move selected item down in the playlist
        selected = self.playlist_listbox.curselection()
        if not selected or selected[0] == self.playlist_listbox.size() - 1:
            return
        
        index = selected[0]
        item = self.playlist.pop(index)
        self.playlist.insert(index + 1, item)
        
        # Update listbox
        item_text = self.playlist_listbox.get(index)
        self.playlist_listbox.delete(index)
        self.playlist_listbox.insert(index + 1, item_text)
        self.playlist_listbox.selection_set(index + 1)
        
        # Send updated playlist to server
        self.update_server_playlist()

    def update_server_playlist(self):
        # Send updated playlist to server
        if self.connected:
            self.send_message({'type': 'set_playlist', 'playlist': self.playlist})
            self.status_var.set(f"Playlist updated: {len(self.playlist)} videos")

    def play(self):
        # Send play command to server
        if self.connected:
            self.send_message({'type': 'play'})
            self.status_var.set("Play command sent")

    def pause(self):
        # Send pause command to server
        if self.connected:
            self.send_message({'type': 'pause'})
            self.status_var.set("Pause command sent")

    def previous(self):
        # Send previous command to server
        if self.connected:
            self.send_message({'type': 'previous'})
            self.status_var.set("Previous command sent")

    def next(self):
        # Send next command to server
        if self.connected:
            self.send_message({'type': 'next'})
            self.status_var.set("Next command sent")

    def set_client_volume(self):
        # Set volume for selected client
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a client first")
            return
        
        client_id = self.client_tree.item(selected[0])['values'][0]
        volume = int(self.volume_slider.get())
        
        if self.connected:
            self.send_message({'type': 'set_volume', 'client_id': client_id, 'volume': volume})
            self.status_var.set(f"Volume set to {volume} for client {client_id}")

    def set_all_volumes(self):
        # Set volume for all clients
        volume = int(self.volume_slider.get())
        
        if self.connected:
            self.send_message({'type': 'set_volume', 'client_id': 'all', 'volume': volume})
            self.status_var.set(f"Volume set to {volume} for all clients")

    def on_close(self):
        self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    admin = VideoSyncAdmin()
