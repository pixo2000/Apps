import socket
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='[CLIENT] %(message)s')

SERVER_IP = 'localhost'  # Replace with your server's IP
PORT = 5001
BUFFER_SIZE = 4096

filename = input("Enter the filename to download: ").strip()
download_path = os.path.abspath(filename)
logging.debug(f"Attempting to connect to {SERVER_IP}:{PORT}")
logging.debug(f"Download path will be: {download_path}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((SERVER_IP, PORT))
        logging.debug(f"Connected to server.")
        s.sendall(filename.encode())
        logging.debug(f"Requested file: {filename}")
        status = s.recv(BUFFER_SIZE)
        logging.debug(f"Received status: {status}")
        if status == b'EXISTS':
            with open(download_path, 'wb') as f:
                while True:
                    data = s.recv(BUFFER_SIZE)
                    if not data:
                        break
                    f.write(data)
            logging.info(f"File '{filename}' downloaded successfully at: {download_path}")
        else:
            logging.warning(f"File '{filename}' not found on server.")
    except Exception as e:
        logging.error(f"Error: {e}")
