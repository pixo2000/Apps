import socket
import os
import threading
import json
import time
import logging

# Set the folder to sync at the top
SYNC_FOLDER = os.path.abspath(r"C:/Users/Paul.Schoeneck.INFORMATIK/Downloads/SyncServer")  # CHANGE THIS
HOST = '0.0.0.0'
PORT = 5001
BUFFER_SIZE = 4096

logging.basicConfig(level=logging.DEBUG, format='[SERVER] %(asctime)s %(message)s')

# Helper to get all files (relative paths) in the sync folder
def get_all_files():
    file_list = []
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, SYNC_FOLDER)
            file_list.append(rel_path.replace('\\', '/'))
    logging.debug(f"Current server file list: {file_list}")
    return file_list

def handle_client(conn, addr):
    logging.info(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(BUFFER_SIZE).decode().strip()
            if not data:
                logging.debug(f"No data received from {addr}, closing connection.")
                break
            logging.debug(f"Received command from {addr}: {data}")
            if data == 'LIST':
                files = get_all_files()
                response = json.dumps(files).encode()
                conn.sendall(response)
                logging.debug(f"Sent file list to {addr} ({len(response)} bytes)")
            elif data.startswith('GET:'):
                rel_path = data[4:]
                abs_path = os.path.join(SYNC_FOLDER, rel_path)
                if os.path.isfile(abs_path):
                    conn.sendall(b'EXISTS')
                    logging.debug(f"Sending file to {addr}: {rel_path}")
                    with open(abs_path, 'rb') as f:
                        total_bytes = 0
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            conn.sendall(bytes_read)
                            total_bytes += len(bytes_read)
                    logging.info(f"Sent file to {addr}: {rel_path} ({total_bytes} bytes)")
                else:
                    conn.sendall(b'NOFILE')
                    logging.warning(f"File not found for {addr}: {rel_path}")
            else:
                conn.sendall(b'INVALID')
                logging.warning(f"Invalid command from {addr}: {data}")
    except Exception as e:
        logging.error(f"Error with {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Connection closed for {addr}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)
    logging.info(f"Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
