import socket
from threading import Thread

def listener(sock):
    while True:
        rcv = sock.recv(1024).decode()
        print("\n" + rcv + "\n")
        
# Request server and port
host = input("Enter server address (default: localhost): ") or "localhost"
port = int(input("Enter port (default: 8000) ") or "8000")

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
sock.connect((host, port))
name = input("Enter your name: ")

# Receive message
t = Thread(target = listener, args = (sock,))

t.daemon = True
t.start()

while True:
    msg = input()
    if (msg == "quit"):
        break
    msg = name + ":" + msg
    sock.send(msg.encode())
    
sock.close()