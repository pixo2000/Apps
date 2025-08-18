import customtkinter as ctk
from tkinter import messagebox, ttk
import json
import logging
from datetime import datetime
from main import create_webdav_connection, download_config, upload_config, update_config_value

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webdav_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VideoStreamerGUI:
    def __init__(self, root):
        logger.info("Initializing VideoStreamerGUI")
        self.root = root
        self.root.title("WebDAV Video Streamer")
        self.root.geometry("900x700")
        
        self.webdav = None
        self.config_data = None
        
        self.setup_ui()
        self.connect_webdav()
    
    def setup_ui(self):
        # Main tabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Videos tab
        self.videos_tab = self.tabview.add("Videos")
        self.setup_videos_tab()
        
        # Config tab
        self.config_tab = self.tabview.add("Config")
        self.setup_config_tab()
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self.root, height=40)
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Disconnected")
        self.status_label.pack(pady=10)
    
    def setup_videos_tab(self):
        # Refresh button
        self.refresh_btn = ctk.CTkButton(self.videos_tab, text="Refresh Videos", command=self.refresh_videos)
        self.refresh_btn.pack(pady=10)
        
        # Create treeview table for videos with timestamp column for sorting
        self.videos_tree = ttk.Treeview(self.videos_tab, columns=("Date", "Size", "timestamp"), show="tree headings", height=15)
        
        # Configure columns
        self.videos_tree.heading("#0", text="Name")
        self.videos_tree.heading("Date", text="Date")
        self.videos_tree.heading("Size", text="Size")
        
        self.videos_tree.column("#0", width=400, minwidth=200)
        self.videos_tree.column("Date", width=150, minwidth=100)
        self.videos_tree.column("Size", width=100, minwidth=80)
        # Hide timestamp column (used only for sorting)
        self.videos_tree.column("timestamp", width=0, stretch=False)
        self.videos_tree.heading("timestamp", text="")
        
        # Enable sorting by clicking headers
        self.videos_tree.heading("Date", command=lambda: self.sort_treeview("Date"))
        self.videos_tree.heading("Size", command=lambda: self.sort_treeview("Size"))
        self.videos_tree.heading("#0", command=lambda: self.sort_treeview("#0"))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.videos_tab, orient="vertical", command=self.videos_tree.yview)
        self.videos_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.videos_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    def setup_config_tab(self):
        # Config controls frame
        controls_frame = ctk.CTkFrame(self.config_tab)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        self.load_btn = ctk.CTkButton(controls_frame, text="Load Config", command=self.load_config)
        self.load_btn.pack(side="left", padx=5, pady=10)
        
        self.save_btn = ctk.CTkButton(controls_frame, text="Save Config", command=self.save_config)
        self.save_btn.pack(side="left", padx=5, pady=10)
        
        # Config editor
        self.config_text = ctk.CTkTextbox(self.config_tab, height=300)
        self.config_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Quick edit frame
        edit_frame = ctk.CTkFrame(self.config_tab)
        edit_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(edit_frame, text="Quick Edit", font=("Arial", 14, "bold")).pack(pady=5)
        
        key_frame = ctk.CTkFrame(edit_frame)
        key_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_frame, text="Key Path:").pack(side="left", padx=5)
        self.key_entry = ctk.CTkEntry(key_frame, placeholder_text="e.g., server.port")
        self.key_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        value_frame = ctk.CTkFrame(edit_frame)
        value_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(value_frame, text="Value:").pack(side="left", padx=5)
        self.value_entry = ctk.CTkEntry(value_frame, placeholder_text="Enter new value")
        self.value_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.update_btn = ctk.CTkButton(edit_frame, text="Update", command=self.update_config_value)
        self.update_btn.pack(pady=10)
    
    def connect_webdav(self):
        logger.info("Attempting WebDAV connection")
        try:
            self.webdav = create_webdav_connection()
            if self.webdav:
                logger.info("WebDAV connection successful")
                self.status_label.configure(text="Connected to WebDAV", text_color="green")
                self.refresh_videos()
            else:
                logger.error("WebDAV connection failed - no connection object returned")
                self.status_label.configure(text="Failed to connect", text_color="red")
        except Exception as e:
            logger.error(f"WebDAV connection error: {str(e)}", exc_info=True)
            self.status_label.configure(text=f"Connection error: {str(e)}", text_color="red")
            messagebox.showerror("Connection Error", f"Failed to connect to WebDAV: {str(e)}")
    
    def refresh_videos(self):
        logger.info("Starting video refresh")
        if not self.webdav:
            logger.warning("No WebDAV connection available")
            messagebox.showwarning("No Connection", "Please connect to WebDAV first")
            return
        
        # Clear existing items
        logger.debug("Clearing existing treeview items")
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        try:
            # Try both path formats
            paths = [
                '/Konzept MNS-Studios Krissel/Ablage Filmaterial, Fertige Filme/',
                '/Konzept%20MNS-Studios%20Krissel/Ablage%20Filmaterial%2c%20Fertige%20Filme/'
            ]
            
            files = None
            for i, path in enumerate(paths):
                logger.debug(f"Trying path {i+1}: {path}")
                try:
                    files = self.webdav.ls(path)
                    logger.info(f"Successfully accessed path: {path}")
                    break
                except Exception as e:
                    logger.debug(f"Path {i+1} failed: {str(e)}")
                    continue
            
            if not files:
                logger.error("Could not access any video directory paths")
                messagebox.showerror("Error", "Could not access video directory")
                return
            
            logger.info(f"Found {len(files)} total files")
            
            # Filter and sort videos
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
            video_files = [f for f in files if any(f.name.lower().endswith(ext) for ext in video_extensions)]
            logger.info(f"Filtered to {len(video_files)} video files")
            
            # Sort by modification time
            logger.debug("Sorting videos by modification time")
            video_files.sort(key=lambda x: getattr(x, 'mtime', 0), reverse=True)
            
            # Add video items to treeview
            logger.debug("Adding videos to treeview")
            for i, video in enumerate(video_files):
                if i % 10 == 0:  # Log every 10th video to avoid spam
                    logger.debug(f"Processing video {i+1}/{len(video_files)}: {video.name}")
                
                date_str = "Unknown"
                timestamp = 0
                if hasattr(video, 'mtime') and video.mtime:
                    try:
                        timestamp = video.mtime
                        date_str = datetime.fromtimestamp(video.mtime).strftime('%Y-%m-%d %H:%M')
                    except Exception as e:
                        logger.warning(f"Error formatting date for {video.name}: {str(e)}")
                        date_str = str(video.mtime)
                
                size_str = "Unknown"
                if hasattr(video, 'size') and video.size:
                    try:
                        size_mb = video.size / (1024 * 1024)
                        size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{size_mb/1024:.1f} GB"
                    except Exception as e:
                        logger.warning(f"Error formatting size for {video.name}: {str(e)}")
                
                filename = video.name.split('/')[-1]
                try:
                    item_id = self.videos_tree.insert("", "end", text=filename, values=(date_str, size_str, timestamp))
                except Exception as e:
                    logger.error(f"Error inserting video {filename}: {str(e)}")
            
            logger.debug("Starting default sort by date")
            # Sort by date (newest first) by default
            self.sort_treeview("Date")
            
            logger.info(f"Video refresh completed successfully - {len(video_files)} videos loaded")
            self.status_label.configure(text=f"Found {len(video_files)} videos", text_color="green")
            
        except Exception as e:
            logger.error(f"Error during video refresh: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to refresh videos: {str(e)}")
    
    def load_config(self):
        if not self.webdav:
            messagebox.showwarning("No Connection", "Please connect to WebDAV first")
            return
        
        try:
            self.config_data = download_config(self.webdav)
            if self.config_data:
                self.config_text.delete("1.0", "end")
                self.config_text.insert("1.0", json.dumps(self.config_data, indent=2, ensure_ascii=False))
                self.status_label.configure(text="Config loaded successfully", text_color="green")
            else:
                messagebox.showerror("Error", "Failed to load config")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
    
    def save_config(self):
        if not self.webdav or not self.config_data:
            messagebox.showwarning("No Data", "Please load config first")
            return
        
        try:
            # Parse current text content
            config_text = self.config_text.get("1.0", "end")
            self.config_data = json.loads(config_text)
            
            if upload_config(self.webdav, self.config_data):
                messagebox.showinfo("Success", "Config saved successfully")
                self.status_label.configure(text="Config saved", text_color="green")
            else:
                messagebox.showerror("Error", "Failed to save config")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def update_config_value(self):
        if not self.config_data:
            messagebox.showwarning("No Config", "Please load config first")
            return
        
        key_path = self.key_entry.get().strip()
        new_value = self.value_entry.get().strip()
        
        if not key_path:
            messagebox.showwarning("Missing Key", "Please enter a key path")
            return
        
        try:
            # Convert value types
            if new_value.lower() == 'true':
                new_value = True
            elif new_value.lower() == 'false':
                new_value = False
            elif new_value.isdigit():
                new_value = int(new_value)
            elif '.' in new_value and new_value.replace('.', '').isdigit():
                new_value = float(new_value)
            
            self.config_data = update_config_value(self.config_data, key_path, new_value)
            
            # Update text display
            self.config_text.delete("1.0", "end")
            self.config_text.insert("1.0", json.dumps(self.config_data, indent=2, ensure_ascii=False))
            
            messagebox.showinfo("Success", f"Updated {key_path} = {new_value}")
            self.key_entry.delete(0, "end")
            self.value_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update config: {str(e)}")

    def sort_treeview(self, column):
        """Sort treeview by column"""
        logger.debug(f"Sorting treeview by column: {column}")
        try:
            children = self.videos_tree.get_children('')
            logger.debug(f"Sorting {len(children)} items")
            
            if column == "Date":
                # Sort by timestamp for accurate date sorting
                items = []
                for child in children:
                    try:
                        timestamp = float(self.videos_tree.set(child, "timestamp") or 0)
                        items.append((timestamp, child))
                    except Exception as e:
                        logger.warning(f"Error getting timestamp for item {child}: {str(e)}")
                        items.append((0, child))
                items.sort(reverse=True)
            elif column == "Size":
                # Sort by size (largest first)
                items = []
                for child in children:
                    try:
                        size_str = self.videos_tree.set(child, "Size")
                        if 'GB' in size_str:
                            size_val = float(size_str.replace(' GB', '')) * 1024
                        elif 'MB' in size_str:
                            size_val = float(size_str.replace(' MB', ''))
                        else:
                            size_val = 0
                        items.append((size_val, child))
                    except Exception as e:
                        logger.warning(f"Error parsing size for item {child}: {str(e)}")
                        items.append((0, child))
                items.sort(reverse=True)
            else:
                # Sort alphabetically by name
                items = []
                for child in children:
                    try:
                        name = self.videos_tree.item(child, "text")
                        items.append((name, child))
                    except Exception as e:
                        logger.warning(f"Error getting name for item {child}: {str(e)}")
                        items.append(("", child))
                items.sort()
            
            logger.debug("Moving items to new positions")
            for index, (val, child) in enumerate(items):
                try:
                    self.videos_tree.move(child, '', index)
                except Exception as e:
                    logger.error(f"Error moving item {child} to position {index}: {str(e)}")
            
            logger.debug(f"Sort by {column} completed successfully")
        except Exception as e:
            logger.error(f"Error during sort operation: {str(e)}", exc_info=True)

if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoStreamerGUI(root)
    root.mainloop()
