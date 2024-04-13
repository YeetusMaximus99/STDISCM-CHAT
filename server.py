import socket
from threading import Thread
import mysql.connector
import time
from datetime import datetime, timedelta
import threading

def get_current_time():
    return (datetime.utcnow() - timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

last_checked_time = get_current_time()
client_sockets_lock = threading.Lock()  # Lock for managing access to client_sockets set

def send_history(cs):
    try:
        db = mysql.connector.connect(host="localhost", user="root", passwd="WENKWONK420", db="new_schema")
        cursor = db.cursor()
        query = "SELECT user, messagescol FROM messages ORDER BY created_at ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        messages = [f"{row[0]}:{row[1]}" for row in rows]
        full_history = "\n".join(messages) + "\n"
        cs.sendall(full_history.encode())
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Failed to send history: {e}")

def replicate_data(msg):
    for server in other_servers:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server)
            sock.sendall(msg.encode() + b'\n')
            sock.close()
        except Exception as e:
            print(f"Failed to replicate to {server}: {e}")

def listener(cs, client_sockets):
    send_history(cs)
    while True:
        try:
            msg = cs.recv(1024).decode()
            if not msg:
                raise Exception("Client disconnected.")
            distribute_message(msg, client_sockets)
            replicate_data(msg)
        except Exception as e:
            print(e)
            with client_sockets_lock:
                client_sockets.remove(cs)
            cs.close()
            return

def distribute_message(msg, client_sockets):
    try:
        db = mysql.connector.connect(host="localhost", user="root", passwd="WENKWONK420", db="new_schema")
        cursor = db.cursor()
        sql = "INSERT INTO messages (user, messagescol, created_at) VALUES (%s, %s, NOW())"
        user, content = msg.split(":", 1)
        cursor.execute(sql, (user, content))
        db.commit()
        cursor.close()
        db.close()
        broadcast_message(msg, client_sockets)
    except Exception as e:
        print(f"Error distributing message: {e}")

def broadcast_message(msg, client_sockets):
    with client_sockets_lock:
        clients_to_remove = []
        for client_socket in client_sockets:
            try:
                client_socket.send((msg + "\n").encode())
            except Exception as e:
                clients_to_remove.append(client_socket)
                print(f"Failed to send to a client: {e}")
        for client in clients_to_remove:
            client_sockets.remove(client)
            client.close()

def poll_new_messages(client_sockets):
    global last_checked_time
    while True:
        try:
            db = mysql.connector.connect(host="localhost", user="root", passwd="WENKWONK420", db="new_schema")
            cursor = db.cursor()
            query = f"SELECT user, messagescol, created_at FROM messages WHERE created_at > STR_TO_DATE('{last_checked_time}', '%Y-%m-%d %H:%i:%s') ORDER BY created_at ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                messages = [f"{row[0]}:{row[1]}" for row in rows]
                full_messages = "\n".join(messages) + "\n"
                with client_sockets_lock:
                    for client_socket in client_sockets:
                        client_socket.send(full_messages.encode())
                last_checked_time = rows[-1][2].strftime('%Y-%m-%d %H:%M:%S')
            cursor.close()
            db.close()
        except Exception as e:
            print(f"Error polling new messages: {e}")
        time.sleep(1)

def create_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="WENKWONK420"
    )
    cursor = conn.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS new_schema")

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS new_schema.messages (
            user VARCHAR(255),
            messagescol LONGTEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"
    )
    conn.commit()
    conn.close()

host = '0.0.0.0'  # Listen on all network interfaces
port = int(input("Enter Port Used: "))

create_database()

x = 5
client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(x)
print(f"[*] Listening as {host}:{port}")

polling_thread = Thread(target=poll_new_messages, args=(client_sockets,))
polling_thread.daemon = True
polling_thread.start()

while True:
    try:
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} connected.")
        with client_sockets_lock:
            client_sockets.add(client_socket)
        t = Thread(target=listener, args=(client_socket, client_sockets))
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"Accepting new connection failed: {e}")

# Close client sockets
for cs in client_sockets:
    cs.close()
# Close server socket
s.close()