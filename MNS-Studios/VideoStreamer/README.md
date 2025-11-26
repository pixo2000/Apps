# Video Streamer 🎬

A simple web-based video playlist manager and player for streaming videos from your PC to a Raspberry Pi (or any device with a browser).

## NOT WORKING

Same problem as VideoSync: The Raspi does not have enough computing power :(

## Features

- ✅ Upload videos via web interface
- ✅ Drag-and-drop playlist reordering
- ✅ Delete videos
- ✅ Rename video titles
- ✅ Auto-play videos in sequence
- ✅ Browser-based fullscreen playback
- ✅ Restart playback remotely
- ✅ Keyboard shortcuts for player control
- ✅ Automatic playlist updates
- ✅ Beautiful, modern UI

## Setup Instructions

### On Your PC (Server)

1. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```powershell
   python main.py
   ```

3. **Access the management interface:**
   - Open your browser and go to: `http://localhost:5000`
   - Upload videos, arrange playlist, manage content

4. **Find your PC's IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (usually something like `192.168.1.x`)

### On Raspberry Pi (Player)

1. **Open the player:**
   ```bash
   chromium-browser http://YOUR_PC_IP:5000/player
   ```
   Replace `YOUR_PC_IP` with your PC's IP address (e.g., `192.168.1.100`)

2. **Click anywhere on the screen to start playback** (required by browser autoplay policies)

3. **For fullscreen/kiosk mode:**
   ```bash
   chromium-browser --kiosk --autoplay-policy=no-user-gesture-required http://YOUR_PC_IP:5000/player
   ```
   
   **Note:** Even in kiosk mode, you may need to click once to start due to browser security policies.

4. **Alternative - Use Firefox:**
   ```bash
   firefox --kiosk http://YOUR_PC_IP:5000/player
   ```

3. **Auto-start on boot (optional):**
   
   Create a file: `~/.config/autostart/video-player.desktop`
   ```ini
   [Desktop Entry]
   Type=Application
   Name=Video Player
   Exec=chromium-browser --kiosk --autoplay-policy=no-user-gesture-required http://YOUR_PC_IP:5000/player
   ```

## Usage

### Management Interface (`http://localhost:5000`)

- **Upload Videos:** Click "Choose Video Files" button
- **Reorder Playlist:** Drag and drop videos using the ☰ handle
- **Rename Videos:** Click "✏️ Rename" button
- **Delete Videos:** Click "🗑️ Delete" button
- **Restart Playback:** Click "🔄 Restart Playback" to restart the player from the beginning

### Player Interface (`http://YOUR_PC_IP:5000/player`)

**Keyboard Shortcuts:**
- `→` or `N` - Next video
- `←` or `P` - Previous video
- `Space` - Pause/Play
- `R` - Restart current video
- `F11` - Toggle fullscreen (in most browsers)

**Features:**
- Auto-plays videos in sequence
- Loops playlist when finished
- Shows current video info (fades after 5 seconds)
- Automatically checks for playlist updates every 10 seconds
- Checks for restart signals every 5 seconds

## Supported Video Formats

- MP4
- AVI
- MKV
- MOV
- WebM
- FLV
- WMV

## Network Requirements

- Both PC and Raspberry Pi must be on the same network
- Make sure your firewall allows connections on port 5000
- For Windows, you may need to create a firewall rule:
  ```powershell
  New-NetFirewallRule -DisplayName "Video Streamer" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
  ```

## Tips

1. **Video Compatibility:** H.264 encoded MP4 files work best across all browsers
2. **Performance:** The server streams videos directly, so ensure good network speed
3. **Large Files:** The upload limit is 5GB per file (configurable in `main.py`)
4. **Remote Access:** To access from other networks, consider using a VPN or port forwarding (not recommended for security reasons)

## Troubleshooting

### Videos won't play on Raspberry Pi
- Check that the PC's IP address is correct
- Ensure the server is running on your PC
- Try opening the player URL in a regular browser first to test

### Upload fails
- Check that the video format is supported
- Ensure the file is under 5GB
- Check disk space on your PC

### Playback is choppy
- Your network speed may be too slow
- Try using lower resolution videos
- Ensure no other devices are using bandwidth

### Browser won't go fullscreen
- Click anywhere on the page first
- Try pressing F11
- Use the `--kiosk` flag when starting the browser

## Project Structure

```
VideoStreamer/
├── main.py                 # Flask server
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/
│   ├── index.html         # Management interface
│   └── player.html        # Video player
├── videos/                # Uploaded videos (created automatically)
├── playlist.json          # Playlist data (created automatically)
└── restart_flag.txt       # Restart signal (temporary)
```

## Development

To run in debug mode (auto-reloads on code changes):
```powershell
python main.py
```

The server runs on `0.0.0.0:5000` by default, making it accessible from other devices on your network.

## License

Free to use and modify as needed!
