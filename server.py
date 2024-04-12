import socket
from threading import Thread
import mysql.connector

def listener(cs, client_sockets):
    while True:
        try:
            # Listen for client message
            msg = cs.recv(1024).decode()
            if not msg:
                raise Exception("Client disconnected.")
        except Exception as e:
            print(e)
            #remove faulty client
            client_sockets.remove(cs)
            cs.close()
            return
        # iterate over all connected sockets and distribute message
        distribute_message(msg, client_sockets)

def distribute_message(msg, client_sockets):
    db = mysql.connector.connect(host="localhost", user="root", passwd="0000", db="new_schema")
    cursor = db.cursor()
    sql = "INSERT INTO messages (user, messagescol) VALUES (%s, %s)"
    user, content = msg.split(":", 1)  # Assume messages are in "name:message" format
    cursor.execute(sql, (user, content))
    db.commit()
    cursor.close()
    db.close()
    for client_socket in client_sockets:
        client_socket.send(msg.encode())

host = input("Enter Host Address:")
port = int(input("Enter Port Used:"))

x = 5
client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(x)
print(f"[*] Listening as {host}:{port}")

while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    client_sockets.add(client_socket)
    t = Thread(target=listener, args=(client_socket, client_sockets))
    t.daemon = True
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()