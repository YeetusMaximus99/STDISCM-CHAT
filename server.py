import socket
from threading import Thread
import mysql.connector
import time
from datetime import datetime, timedelta

def get_current_time():
    return (datetime.utcnow() - timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

last_checked_time = get_current_time()

def send_history(cs):
    try:
        db = mysql.connector.connect(host=host_db, user="admin", passwd="STDISCM123", db="chat_schema")
        cursor = db.cursor()
        query = "SELECT user, messagescol FROM messages ORDER BY created_at ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            messages = [f"{row[0]}:{row[1]}" for row in rows]
            full_history = "\n".join(messages) + "\n"
            cs.sendall(full_history.encode())
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Failed to send history: {e}")

def listener(cs, client_sockets):
    send_history(cs)
    while True:
        try:
            msg = cs.recv(1024).decode()
            if not msg:
                raise Exception("Client disconnected.")
            distribute_message(msg, client_sockets)
        except Exception as e:
            print(e)
            client_sockets.remove(cs)
            cs.close()
            return

def distribute_message(msg, client_sockets):
    try:
        db = mysql.connector.connect(host=host_db, user="admin", passwd="STDISCM123", db="chat_schema")
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
    for client_socket in client_sockets:
        try:
            client_socket.send((msg + "\n").encode())
        except Exception as e:
            client_sockets.remove(client_socket)
            client_socket.close()
            print(f"Failed to send to a client: {e}")

def poll_new_messages(client_sockets):
    global last_checked_time
    while True:
        try:
            db = mysql.connector.connect(host=host_db, user="admin", passwd="STDISCM123", db="chat_schema")
            cursor = db.cursor()
            query = f"SELECT user, messagescol, created_at FROM messages WHERE created_at > STR_TO_DATE('{last_checked_time}', '%Y-%m-%d %H:%i:%s') ORDER BY created_at ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                messages = [f"{row[0]}:{row[1]}" for row in rows]
                full_messages = "\n".join(messages) + "\n"
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
        host=host_db,
        user="admin",
        password="STDISCM123"
    )
    cursor = conn.cursor()

    cursor.execute(''' 
        CREATE SCHEMA IF NOT EXISTS chat_schema 
    ''')

    cursor.execute(
        ''' CREATE TABLE IF NOT EXISTS chat_schema.messages (
            user VARCHAR(255),
            messagescol LONGTEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

host = ""
host_db = ""
server_num = 0
port = 0

while (server_num != 1 or server_num != 2):
    server_num = int(input("Enter Server Number (1 or 2): "))
    if server_num == 1:
        host_db = "stdiscm-db-1.c7akos44mb75.ap-southeast-2.rds.amazonaws.com"
        
        # change these after server deployment
        host = "localhost" 
        port = 8081
        break
    elif server_num == 2:
        host_db = "stdiscm-db-2.c7akos44mb75.ap-southeast-2.rds.amazonaws.com"
        
        # change these after server deployment
        host = "localhost" 
        port = 8082
        break

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
        client_sockets.add(client_socket)
        t = Thread(target=listener, args=(client_socket, client_sockets))
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"Accepting new connection failed: {e}")

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()