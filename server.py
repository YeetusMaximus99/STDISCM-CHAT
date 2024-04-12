import socket
from threading import Thread
import mysql.connector

def send_history(cs):
    try:
        db = mysql.connector.connect(host="localhost", user="root", passwd="0000", db="new_schema")
        cursor = db.cursor()
        query = "SELECT user, messagescol FROM messages"
        cursor.execute(query)
        rows = cursor.fetchall()
        messages = [f"{row[0]}:{row[1]}" for row in rows]
        full_history = "\n".join(messages) + "\n"
        cs.sendall(full_history.encode())  # Use sendall to ensure all data is sent
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Failed to send history: {e}")

def listener(cs, client_sockets):
    send_history(cs)  # Send chat history upon new client connection
    while True:
        try:
            msg = cs.recv(1024).decode()
            if not msg:
                raise Exception("Client disconnected.")
        except Exception as e:
            print(e)
            client_sockets.remove(cs)
            cs.close()
            return
        distribute_message(msg, client_sockets)

def distribute_message(msg, client_sockets):
    try:
        db = mysql.connector.connect(host="localhost", user="root", passwd="0000", db="new_schema")
        cursor = db.cursor()
        sql = "INSERT INTO messages (user, messagescol) VALUES (%s, %s)"
        user, content = msg.split(":", 1)
        cursor.execute(sql, (user, content))
        db.commit()
        cursor.close()
        db.close()
        for client_socket in client_sockets:
            client_socket.send((msg + "\n").encode())
    except Exception as e:
        print(f"Error distributing message: {e}")

host = input("Enter Host Address: ")
port = int(input("Enter Port Used: "))

x = 5
client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(x)
print(f"[*] Listening as {host}:{port}")

while True:
    try:
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} connected.")
        client_sockets.add(client_socket)
        t = Thread(target=listener, args=(client_socket, client_sockets))
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"Accepting new connection failed: {e}")

# This part of the code will generally not be reached
# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()