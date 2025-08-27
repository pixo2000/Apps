import socket
import os

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001       # Port to listen on
BUFFER_SIZE = 4096

# Directory where files are stored
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"[SERVER] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"[SERVER] Connected by {addr}")
            filename = conn.recv(BUFFER_SIZE).decode().strip()
            filepath = os.path.join(FILE_DIR, filename)
            if os.path.isfile(filepath):
                conn.sendall(b'EXISTS')
                with open(filepath, 'rb') as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        conn.sendall(bytes_read)
                print(f"[SERVER] Sent file: {filename}")
            else:
                conn.sendall(b'NOFILE')
                print(f"[SERVER] File not found: {filename}")
