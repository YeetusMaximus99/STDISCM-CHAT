import socket

host = "localhost"
port = 8080
x = 1
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
#x = Max number of users
sock.listen(x)
print("The server is running and listening on port : ", port)
#Accept connection
connection, address = sock.accept() 
print("Client", connection, "has joined us recently with address : ", address)
while True:
    message = input("Type Message Here: ") 
    connection.send(message.encode())
