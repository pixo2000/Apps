import time
import client.client as client
import server.server as server

def main():
    server.run()
    time.sleep(1)
    client.run()

if __name__ == '__main__':
    main()