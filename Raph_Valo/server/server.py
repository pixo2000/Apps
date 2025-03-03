import socket
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    print(f"[CONNECTION] {addr} Disconnected")
                    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
                    connected = False
                else:
                    print(f"[{addr}] {msg}")
                    conn.send("Msg received".encode(FORMAT))
        except ConnectionResetError:
            print(f"[CONNECTION] {addr}: Connection was forcibly closed by the client")
            connected = False
        except Exception as e:
            print(f"[ERROR] {e}")
            connected = False
    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()