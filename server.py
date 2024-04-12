import socket
from threading import Thread
import mysql.connector
def listener(cs,client_sockets):
    while True:
        try:
            # Listen for client message
            msg = cs.recv(1024).decode()
        except Exception as e:
            print(e)
            #remove faulty client
            client_sockets.remove(cs)
        # iterate over all connected sockets
        for client_socket in client_sockets:
            # and send the message
            db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="MoonbeaN!?0645",  # your password
                     db="new_schema")
            mycursor = db.cursor()
            sql= "INSERT INTO messages (user,messagescol) VALUES (%s,%s)"
            val = ("test",msg.encode())
            mycursor.execute(sql, val)
            db.commit()
            client_socket.send(msg.encode())
            
host = input("Enter Host Address:")
port =int(input("Enter Port Used:"))

x = 5
client_sockets = set()
s = socket.socket()
#Port is made reuseable
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#bind port to address
s.bind((host, port))
#amount of clients that can listen
s.listen(x)
print(f"[*] Listening as {host}:{port}")


while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} is here!")
    # add client
    client_sockets.add(client_socket)
    # Thread to listen for client
    t = Thread(target=listener, args=(client_socket,client_sockets))
    t.daemon = True
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
