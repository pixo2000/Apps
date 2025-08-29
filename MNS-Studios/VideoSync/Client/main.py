import socket
import logging
import os
import json
import time
import shutil
import socket as pysocket  # To avoid conflict with main socket import
import threading
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.DEBUG, format='[CLIENT] %(asctime)s %(message)s')

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"C:\Users\pixo2000\Downloads\SyncClient")  # CHANGE THIS
SERVER_IP = 'localhost'  # Replace with your server's IP
PORT = 5001
BUFFER_SIZE = 4096
SYNC_INTERVAL = 10  # seconds
SERVER_WEB_PORT = 64137
LOCAL_MEDIA_CONTROL_PORT = 64138
CLIENT_HTTP_PORT = 64139
CLIENT_NAME = os.environ.get('CLIENT_NAME', os.uname().nodename if hasattr(os, 'uname') else 'Client')

# Register client with server

def register_with_server(volume=100):
    try:
        url = f'http://{SERVER_IP}:{SERVER_WEB_PORT}/register'
        requests.post(url, json={'name': CLIENT_NAME, 'volume': volume}, timeout=2)
    except Exception as e:
        logging.warning(f"Could not register with server: {e}")

def heartbeat_thread():
    while True:
        register_with_server()
        time.sleep(30)

def start_heartbeat():
    threading.Thread(target=heartbeat_thread, daemon=True).start()

# HTTP server for volume control
app = Flask(__name__)

@app.route('/set_volume', methods=['POST'])
def set_volume():
    data = request.get_json(force=True)
    vol = int(data.get('volume', 100))
    # Forward to local media player
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', LOCAL_MEDIA_CONTROL_PORT))
            s.sendall(f'SETVOLUME:{vol}'.encode())
            s.recv(16)
        logging.info(f"Set local media player volume to {vol}% via remote command.")
        return jsonify({'status': 'ok'})
    except Exception as e:
        logging.warning(f"Could not set volume on media player: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/control', methods=['POST'])
def control():
    data = request.get_json(force=True)
    action = data.get('action')
    # Forward to local media player
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', LOCAL_MEDIA_CONTROL_PORT))
            if action == 'play':
                s.sendall(b'PLAY')
            elif action == 'pause':
                s.sendall(b'PAUSE')
            elif action == 'next':
                s.sendall(b'NEXT')
            elif action == 'prev':
                s.sendall(b'PREV')
            elif action == 'set_index':
                idx = data.get('index', 0)
                s.sendall(f'SETINDEX:{idx}'.encode())
            else:
                return jsonify({'status': 'error', 'error': 'Unknown action'}), 400
            s.recv(16)
        logging.info(f"Sent media control command: {action}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        logging.warning(f"Could not send control command to media player: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/playlist')
def get_playlist():
    # Forward to local media player
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', LOCAL_MEDIA_CONTROL_PORT))
            s.sendall(b'GETPLAYLIST')
            response = s.recv(4096).decode()
        playlist_data = json.loads(response)
        return jsonify(playlist_data)
    except Exception as e:
        logging.warning(f"Could not get playlist from media player: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/skip', methods=['POST'])
def skip():
    data = request.get_json(force=True)
    seconds = data.get('seconds', 10)
    # Forward to local media player
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', LOCAL_MEDIA_CONTROL_PORT))
            s.sendall(f'SKIP:{seconds}'.encode())
            s.recv(16)
        logging.info(f"Sent skip command: {seconds} seconds")
        return jsonify({'status': 'ok'})
    except Exception as e:
        logging.warning(f"Could not send skip command to media player: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/playing_status')
def get_playing_status():
    # Forward to local media player
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', LOCAL_MEDIA_CONTROL_PORT))
            s.sendall(b'GETPLAYINGSTATUS')
            response = s.recv(1024).decode()
        status_data = json.loads(response)
        return jsonify(status_data)
    except Exception as e:
        logging.warning(f"Could not get playing status from media player: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def start_http_server():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=CLIENT_HTTP_PORT, debug=False, use_reloader=False), daemon=True).start()

def get_server_file_list(s):
    logging.debug("Requesting file list from server...")
    s.sendall(b'LIST')
    data = s.recv(1024*1024)
    logging.debug(f"Received file list: {len(data)} bytes")
    return json.loads(data.decode())

def download_file(s, rel_path):
    logging.debug(f"Requesting file: {rel_path}")
    s.sendall(f'GET:{rel_path}'.encode())
    # Read exactly 6 bytes for status
    status = b''
    while len(status) < 6:
        chunk = s.recv(6 - len(status))
        if not chunk:
            break
        status += chunk
    logging.debug(f"Received status for {rel_path}: {status}")
    if status == b'EXISTS':
        # Read 16-byte file size header
        file_size_bytes = b''
        while len(file_size_bytes) < 16:
            chunk = s.recv(16 - len(file_size_bytes))
            if not chunk:
                break
            file_size_bytes += chunk
        file_size = int(file_size_bytes.decode())
        abs_path = os.path.join(SYNC_FOLDER, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        total_bytes = 0
        with open(abs_path, 'wb') as f:
            while total_bytes < file_size:
                chunk_size = min(BUFFER_SIZE, file_size - total_bytes)
                data = s.recv(chunk_size)
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
            f.flush()
            os.fsync(f.fileno())
        logging.info(f"Downloaded: {rel_path} ({total_bytes} bytes, expected {file_size} bytes)")
        # Print file size after download
        try:
            size = os.path.getsize(abs_path)
            logging.info(f"File size on disk: {size} bytes")
        except Exception as e:
            logging.warning(f"Could not get file size: {e}")
        if total_bytes != file_size or size != file_size:
            logging.error(f"File size mismatch for {rel_path}: expected {file_size}, got {total_bytes} (written), {size} (on disk)")
    else:
        logging.warning(f"File not found on server: {rel_path}")

def local_file_list():
    file_list = []
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, SYNC_FOLDER)
            file_list.append(rel_path.replace('\\', '/'))
    logging.debug(f"Local file list: {file_list}")
    return file_list

def delete_local_file(rel_path):
    abs_path = os.path.join(SYNC_FOLDER, rel_path)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
        logging.info(f"Deleted local file: {rel_path}")
    else:
        logging.warning(f"Tried to delete non-existent file: {rel_path}")

def notify_media_player_reload():
    try:
        with pysocket.socket(pysocket.AF_INET, pysocket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 64138))
            s.sendall(b'RELOAD')
            s.recv(16)
        logging.info("Notified media player to reload playlist.")
    except Exception as e:
        logging.warning(f"Could not notify media player: {e}")

def sync_with_server():
    while True:
        try:
            logging.debug("Starting sync cycle...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(15)
                s.connect((SERVER_IP, PORT))
                logging.debug(f"Connected to server.")
                server_files = get_server_file_list(s)
                local_files = local_file_list()
                # Build a dict of local file sizes
                local_sizes = {f: os.path.getsize(os.path.join(SYNC_FOLDER, f)) for f in local_files if os.path.isfile(os.path.join(SYNC_FOLDER, f))}
                server_file_dict = {f['name']: f['size'] for f in server_files}
                # Download new/changed files
                playlist_changed = False
                
                # Special handling for playlist.txt - always check content
                playlist_file = 'playlist.txt'
                if playlist_file in server_file_dict:
                    server_playlist_size = server_file_dict[playlist_file]
                    local_playlist_path = os.path.join(SYNC_FOLDER, playlist_file)
                    
                    should_download_playlist = False
                    if playlist_file not in local_files:
                        should_download_playlist = True
                        logging.info(f"Playlist file missing locally, downloading")
                    elif local_sizes[playlist_file] != server_playlist_size:
                        should_download_playlist = True
                        logging.info(f"Playlist file size changed ({local_sizes[playlist_file]} -> {server_playlist_size}), downloading")
                    else:
                        # Same size, but let's download anyway to check for content changes
                        should_download_playlist = True
                        logging.debug(f"Playlist file same size, downloading to check content")
                    
                    if should_download_playlist:
                        # Read current content before downloading
                        old_content = ""
                        if os.path.exists(local_playlist_path):
                            try:
                                with open(local_playlist_path, 'r', encoding='utf-8') as f:
                                    old_content = f.read()
                            except Exception:
                                pass
                        
                        download_file(s, playlist_file)
                        
                        # Check if content actually changed
                        new_content = ""
                        if os.path.exists(local_playlist_path):
                            try:
                                with open(local_playlist_path, 'r', encoding='utf-8') as f:
                                    new_content = f.read()
                            except Exception:
                                pass
                        
                        if old_content != new_content:
                            playlist_changed = True
                            logging.info(f"Playlist content actually changed")
                        else:
                            logging.debug(f"Playlist content unchanged")
                
                # Handle other files normally
                for rel_path, server_size in server_file_dict.items():
                    if rel_path == playlist_file:
                        continue  # Already handled above
                        
                    needs_download = (
                        rel_path not in local_files or
                        (rel_path in local_sizes and local_sizes[rel_path] != server_size)
                    )
                    if needs_download:
                        logging.info(f"File '{rel_path}' will be downloaded (missing or size mismatch)")
                        download_file(s, rel_path)
                
                # Delete files not on server
                for rel_path in local_files:
                    if rel_path not in server_file_dict:
                        delete_local_file(rel_path)
                        if rel_path == playlist_file:
                            playlist_changed = True
                            
            if playlist_changed:
                notify_media_player_reload()
            logging.debug("Sync cycle complete.")
        except Exception as e:
            logging.error(f"Sync error: {e}")
        time.sleep(SYNC_INTERVAL)

def list_files_with_sizes(base_folder):
    file_info = {}
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, base_folder).replace('\\', '/')
            try:
                size = os.path.getsize(abs_path)
            except Exception:
                size = -1
            file_info[rel_path] = size
    return file_info

if __name__ == "__main__":
    os.makedirs(SYNC_FOLDER, exist_ok=True)
    start_heartbeat()
    start_http_server()
    logging.info(f"Syncing to local folder: {SYNC_FOLDER}")
    # List all files and sizes on client
    print("[CLIENT] Files and sizes in sync folder:")
    client_files = list_files_with_sizes(SYNC_FOLDER)
    for rel_path, size in client_files.items():
        print(f"  {rel_path}: {size} bytes")
    # List all files and sizes on server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SERVER_IP, PORT))
            s.sendall(b'LIST')
            data = s.recv(1024*1024)
            server_files = json.loads(data.decode())
            print("[SERVER] Files and sizes in sync folder:")
            for fileinfo in server_files:
                rel_path = fileinfo['name']
                size = fileinfo['size']
                print(f"  {rel_path}: {size} bytes")
    except Exception as e:
        print(f"[SERVER] Could not list server files: {e}")
    sync_with_server()
