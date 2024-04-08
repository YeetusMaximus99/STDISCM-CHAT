import socket
from threading import Thread

class RoundRobinLoadBalancer:
    def __init__(self, host, port, servers):
        self.host = host
        self.port = port
        self.servers = servers
        self.current_server = 0
        self.setup()
    
    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Load balancer running on {self.host}:{self.port}")
        
    def get_next_server(self):
        # Attempt to connect to the next available server
        for _ in range(len(self.servers)):
            server = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            try:
                # Check if server is up
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.connect(server)
                test_socket.close()
                return server
            except socket.error:
                print(f"Server {server} is down. Trying next server...")
        raise Exception("All servers seem to be down.")
        
    def handle_client(self, client_socket):
        try:
            server_host, server_port = self.get_next_server()
        except Exception as e:
            print(e)
            client_socket.close()
            return
            
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_host, server_port))
        except socket.error as e:
            print(f"Failed to connect to server {server_host}:{server_port}. Error: {e}")
            client_socket.close()
            return
        
        client_to_server = Thread(target = self.forward, args = (client_socket, server_socket))
        server_to_client = Thread(target = self.forward, args = (server_socket, client_socket))
    
        client_to_server.start()
        server_to_client.start()
        
        client_to_server.join()
        server_to_client.join()
        
    def forward(self, source, destination):
        while True:
            try:
                data = source.recv(1024)
                if not data:
                    break
                destination.send(data)
            except Exception as e:
                print(e)
                break
                
    def start(self):
        while True:
            client_socket, _ = self.socket.accept()
            Thread(target = self.handle_client, args = (client_socket,)).start()
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8000
    SERVERS = [("192.168.1.101", 8081), ("192.168.1.102", 8082)] # Sample only; these are our other server instances.
    load_balancer = RoundRobinLoadBalancer(HOST, PORT, SERVERS)
    load_balancer.start()