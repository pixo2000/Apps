import socket
import threading

HOST = '0.0.0.0'
PORT = 65432

clients = []
CAPS_LOCK = False

# Broadcast CAPS_LOCK state to all clients
def broadcast_caps_lock():
    for client in clients:
        try:
            client.sendall(str(CAPS_LOCK).encode())
        except:
            pass

def handle_client(conn, addr):
    global CAPS_LOCK
    clients.append(conn)
    conn.sendall(str(CAPS_LOCK).encode())  # Send initial state
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            if msg in ['True', 'False']:
                new_state = msg == 'True'
                if new_state != CAPS_LOCK:
                    CAPS_LOCK = new_state
                    broadcast_caps_lock()
    finally:
        clients.remove(conn)
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    start_server()
