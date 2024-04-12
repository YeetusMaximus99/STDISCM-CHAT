import socket
from threading import Thread
import mysql.connector

def listener(cs, client_sockets, all_sockets, server_id):
    db = mysql.connector.connect(host = "localhost", user = "root", passwd = "0000", db = "new_schema")
    mycursor = db.cursor()
    while True:
        try:
            msg = cs.recv(1024).decode()
            if msg:  # Check if message is not empty
                # Logically separate user and message for database insertion
                user, message = msg.split(':', 1)  # Assuming all messages are in 'user:message' format

                # Insert into the database
                sql = "INSERT INTO messages (user, messagescol) VALUES (%s, %s)"
                val = (user, message)
                mycursor.execute(sql, val)
                db.commit()

                # Send to all clients
                for client_socket in client_sockets:
                    if client_socket != cs:  # Do not echo to the sender
                        try:
                            client_socket.send(msg.encode())
                        except Exception:
                            client_sockets.remove(client_socket)
                            client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
            client_sockets.remove(cs)
            cs.close()
            return  # Exit the thread if error occurs

if __name__ == "__main__":
    host = input("Enter Host Address:")
    port = int(input("Enter Port Used:"))

    server_id = input("Enter server ID (1 or 2):")

    client_sockets = set()
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)  # Accept max 5 clients simultaneously
    print(f"[*] Listening as {host}:{port}")

    try:  # Use try block to handle graceful shutdown
        while True:
            client_socket, client_address = s.accept()
            print(f"[+] {client_address} connected.")
            client_sockets.add(client_socket)
            t = Thread(target=listener, args=(client_socket, client_sockets, server_id))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        for cs in client_sockets:
            cs.close()
        s.close()