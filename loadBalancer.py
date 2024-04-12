import socket
import time
from threading import Thread

class RoundRobinLoadBalancer:
    def __init__(self, host, port, servers):
        self.host = host
        self.port = port
        self.servers = servers
        self.current_server = 0  # Ensure this is initialized
        self.server_status = {server: True for server in servers}  # track server status
        self.setup()
    
    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Load balancer running on {self.host}:{self.port}")
        Thread(target=self.check_servers, daemon=True).start()  # background thread to check server status
    
    def check_servers(self):
        while True:
            for server in self.servers:
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.connect(server)
                    test_socket.close()
                    self.server_status[server] = True
                except socket.error:
                    self.server_status[server] = False
                    print(f"Server {server} is down.")
            time.sleep(2)  # check every 2 seconds
    
    def get_next_server(self):
        starting_index = self.current_server
        while True:
            server = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            if self.server_status[server]:
                return server
            if self.current_server == starting_index:
                raise Exception("All servers seem to be down.")
        
    def handle_client(self, client_socket):
        while True:
            try:
                server_host, server_port = self.get_next_server()
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((server_host, server_port))
                client_to_server = Thread(target=self.forward, args=(client_socket, server_socket))
                server_to_client = Thread(target=self.forward, args=(server_socket, client_socket))
                client_to_server.start()
                server_to_client.start()
                client_to_server.join()
                server_to_client.join()
                break  # Exit loop once the threads complete
            except Exception as e:
                print(f"Retrying connection. Error: {e}")
                time.sleep(1)  # Wait a bit before retrying to connect to a server

    def forward(self, source, destination):
        try:
            while True:
                data = source.recv(1024)
                if not data:
                    source.close()
                    destination.close()
                    break
                destination.send(data)
        except Exception as e:
            print(e)
            source.close()
            destination.close()

    def start(self):
        while True:
            client_socket, _ = self.socket.accept()
            Thread(target=self.handle_client, args=(client_socket,)).start()
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8000
    SERVERS = [("localhost", 8081), ("localhost", 8082)]
    load_balancer = RoundRobinLoadBalancer(HOST, PORT, SERVERS)
    load_balancer.start()