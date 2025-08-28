import socket
import logging
import os
import json
import time
import shutil

logging.basicConfig(level=logging.DEBUG, format='[CLIENT] %(asctime)s %(message)s')

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"/root/VideoSync")  # CHANGE THIS
SERVER_IP = '10.68.242.114'  # Replace with your server's IP
PORT = 5001
BUFFER_SIZE = 4096
SYNC_INTERVAL = 10  # seconds

def get_server_file_list(s):
    logging.debug("Requesting file list from server...")
    s.sendall(b'LIST')
    data = s.recv(1024*1024)
    logging.debug(f"Received file list: {len(data)} bytes")
    return json.loads(data.decode())

def download_file(s, rel_path):
    logging.debug(f"Requesting file: {rel_path}")
    s.sendall(f'GET:{rel_path}'.encode())
    status = s.recv(BUFFER_SIZE)
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
                data = s.recv(min(BUFFER_SIZE, file_size - total_bytes))
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
        logging.info(f"Downloaded: {rel_path} ({total_bytes} bytes, expected {file_size} bytes)")
        # Print file size after download
        try:
            size = os.path.getsize(abs_path)
            logging.info(f"File size on disk: {size} bytes")
        except Exception as e:
            logging.warning(f"Could not get file size: {e}")
        if total_bytes != file_size:
            logging.error(f"File size mismatch for {rel_path}: expected {file_size}, got {total_bytes}")
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
                for rel_path, server_size in server_file_dict.items():
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
