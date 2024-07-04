import socket
import threading

class CentralServer:
    def __init__(self, port):
        self.port = port
        self.nodes = {}  # Dictionary to store connected nodes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        print(f"Central Server initialized on port {self.port}")

    def listen(self):
        print("Central Server listening...")
        while True:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            print(f"Central Server received message from {addr}: {message}")
            if message.startswith("new node Connected:"):
                new_node_port = int(message.split(":")[1])
                if new_node_port not in self.nodes:
                    self.nodes[new_node_port] = addr[0]  # Store node port and IP address
                    print(f"Node {new_node_port} connected. Informing other nodes... with message ")
                    self.notify_nodes(message, new_node_port)

    def notify_nodes(self, message, exclude_port):
        for node_port in self.nodes:
            if node_port != exclude_port:
                node_ip = self.nodes[node_port]
                self.sock.sendto(message.encode(), (node_ip, node_port))
                print(f"Notifying Node {node_port} at {node_ip}")

    def start(self):
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()
        print("Central Server started and listening...")
