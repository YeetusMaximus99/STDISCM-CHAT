import socket
import time
from threading import Thread

def reconnect():
    retry_count = 0
    while True:
        if retry_count >= 5:
            break
        try:
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((host, port))
            print("Reconnected to the server.")
            return new_sock
        except socket.error:
            print("Connection failed. Retrying...")
            retry_count += 1
            time.sleep(3)

def stop_reconnect():
    while True:
        host = input("Enter server address (default localhost): ") or "localhost"
        port = int(input("Enter port (default 8000): ") or "8000")

def listener(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("Server connection was lost. Reconnecting...")
                sock = reconnect()  # Attempt to reconnect
                continue
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                print("\n" + line + "\n")
        except ConnectionResetError:
            print("Connection was reset by the server. Reconnecting...")
            sock = reconnect()  # Reconnect on connection reset error
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == '__main__':
    connected = False
    while not connected:
        host = input("Enter server address (default localhost): ") or "localhost"
        port = int(input("Enter port (default 8000): ") or "8000")
        # Create socket and connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            connected = True
        except socket.error as e:
            print(f"Could not connect to server: {e}")
            connected = False
            sock = reconnect()

    name = input("Enter your name: ")
    t = Thread(target=listener, args=(sock,))
    t.daemon = True
    t.start()

    while True:
        msg = input()
        if msg == "quit":
            break
        msg = name + ":" + msg
        try:
            sock.send(msg.encode())
        except socket.error:
            print("Sending failed. Server might be down. Reconnecting...")
            sock = reconnect()  # Reconnect if sending fails

    sock.close()