import socket
from threading import Thread
def listener(sock):
    while True:
        rcv = sock.recv(1024).decode()
        print("\n" +rcv+ "\n")

host = "localhost"
port = 8000 # Changed the port to match the load balancer's port
#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect to server
sock.connect((host, port))
name = input("Enter your name: ")
#recieve message
t = Thread(target=listener,args =(sock,))

t.daemon = True

t.start()


while True:
    msg = input()
    if(msg == "quit"):
        break
    msg = name + ":" + msg
    sock.send(msg.encode())
sock.close()


