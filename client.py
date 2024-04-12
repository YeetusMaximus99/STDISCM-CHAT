import socket
from threading import Thread

def reconnect():
    while True:
        try:
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((host, port))
            print("You may now be reconnected, yay! Do give it time, though.")
            return new_sock
        except socket.error:
            print("Connection failed. Retrying...")
            time.sleep(3)

def listener(sock):
    while True:
        try:
            rcv = sock.recv(1024).decode()
            if not rcv:
                print("Server connection was lost. Reconnecting...")
                sock = reconnect()  # Attempt to reconnect
                continue  # Continue listening with new socket
            print("\n" + rcv + "\n")
        except ConnectionResetError:
            print("Connection was reset by the server. Reconnecting...")
            sock = reconnect()  # Reconnect on connection reset error
        except Exception as e:
            print(f"An error occurred: {e}")
            break

host = input("Enter server address (default localhost): ") or "localhost"
port = int(input("Enter port (default 8000): ") or "8000")

# Create socket and connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((host, port))
except socket.error as e:
    print(f"Could not connect to server: {e}")
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