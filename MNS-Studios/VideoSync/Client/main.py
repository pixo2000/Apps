import socket
import logging
import os
import json
import time
import shutil

logging.basicConfig(level=logging.DEBUG, format='[CLIENT] %(asctime)s %(message)s')

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"C:/Users/Paul.Schoeneck.INFORMATIK/Downloads/SyncClient")  # CHANGE THIS
SERVER_IP = 'localhost'  # Replace with your server's IP
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
        abs_path = os.path.join(SYNC_FOLDER, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'wb') as f:
            total_bytes = 0
            while True:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
            logging.info(f"Downloaded: {rel_path} ({total_bytes} bytes)")
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
                # Download new/changed files
                for rel_path in server_files:
                    if rel_path not in local_files:
                        download_file(s, rel_path)
                # Delete files not on server
                for rel_path in local_files:
                    if rel_path not in server_files:
                        delete_local_file(rel_path)
            logging.debug("Sync cycle complete.")
        except Exception as e:
            logging.error(f"Sync error: {e}")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    os.makedirs(SYNC_FOLDER, exist_ok=True)
    logging.info(f"Syncing to local folder: {SYNC_FOLDER}")
    sync_with_server()
