import socket
import threading

SERVER_IP = '0.0.0.0'
SERVER_PORT = 5000

clients = []

# Broadcast clipboard content to all clients except sender
def broadcast(data, sender_sock):
    for client in clients:
        if client != sender_sock:
            try:
                client.sendall(data)
                print(f"[DEBUG] Broadcasted clipboard data to {client.getpeername()}")
            except Exception as e:
                print(f"[DEBUG] Failed to send to {client.getpeername()}: {e}")

def handle_client(sock, addr):
    print(f'[DEBUG] Client connected: {addr}')
    clients.append(sock)
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            print(f"[DEBUG] Received clipboard data from {addr}: {data[:50].decode('utf-8', errors='replace')}")
            broadcast(data, sock)
    except Exception as e:
        print(f"[DEBUG] Exception in client {addr}: {e}")
    finally:
        print(f'[DEBUG] Client disconnected: {addr}')
        clients.remove(sock)
        sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f'[DEBUG] Server listening on {SERVER_IP}:{SERVER_PORT}')
    while True:
        client_sock, addr = server.accept()
        print(f"[DEBUG] Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == '__main__':
    main()
