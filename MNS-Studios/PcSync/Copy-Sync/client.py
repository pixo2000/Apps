import socket
import threading
import pyperclip
import time

SERVER_IP = '127.0.0.1'  # Change to your server's IP
SERVER_PORT = 5000

# Connect to server
def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    return s

# Send clipboard content to server
def send_clipboard(sock):
    last_clipboard = pyperclip.paste()
    while True:
        current = pyperclip.paste()
        if current != last_clipboard:
            try:
                sock.sendall(current.encode('utf-8'))
                last_clipboard = current
            except Exception:
                break
        time.sleep(0.5)

# Receive clipboard updates from server
def receive_clipboard(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            text = data.decode('utf-8')
            pyperclip.copy(text)
        except Exception:
            break

def main():
    sock = connect_to_server()
    threading.Thread(target=send_clipboard, args=(sock,), daemon=True).start()
    receive_clipboard(sock)

if __name__ == '__main__':
    main()
