import socket
import threading
import json
import time

class Node:
    def __init__(self, node_id, num_nodes, host, port):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.host = host
        self.port = port
        self.send_seq = 0
        self.delivered = [0] * num_nodes
        self.buffer = set()
        self.private_clocks = [0] * num_nodes
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)  # Set a timeout to avoid indefinite blocking

        # Bind socket with retry logic for higher ports
        bound = False
        while not bound:
            try:
                self.sock.bind((host, port))
                bound = True
                print(f"Node {self.node_id} bound to port {port}")
            except PermissionError:
                port += 1

        self.recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.recv_thread.start()

    def broadcast(self, message):
        deps = self.delivered.copy()
        deps[self.node_id] = self.send_seq
        msg = {'type': 'broadcast', 'sender': self.node_id, 'deps': deps, 'message': message}
        self.send_seq += 1
        self.send_to_all(json.dumps(msg))
        # Process the message as if it was received locally
        self.handle_broadcast(msg)
        print(f"Node {self.node_id} broadcasted message: {message}")

    def send_private_message(self, receiver, message):
        self.private_clocks[self.node_id] += 1
        private_msg = {'type': 'private', 'sender': self.node_id, 'receiver': receiver, 'clock': self.private_clocks[self.node_id], 'message': message}
        self.sock.sendto(json.dumps(private_msg).encode(), ('localhost', 7000 + receiver))
        print(f"Node {self.node_id} sent private message to Node {receiver}: {message}")

    def send_to_all(self, msg):
        for i in range(self.num_nodes):
            if i != self.node_id:
                self.sock.sendto(msg.encode(), ('localhost', 7000 + i))

    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = json.loads(data.decode())
                print(f"Node {self.node_id} received message: {msg}")
                if msg['type'] == 'broadcast':
                    self.handle_broadcast(msg)
                elif msg['type'] == 'private':
                    self.handle_private_message(msg)
            except socket.timeout:
                continue
            except Exception as e:
                if str(e) != "Socket is closed":
                    print(f"Node {self.node_id} encountered an error: {e}")

    def handle_broadcast(self, msg):
        sender = msg['sender']
        deps = msg['deps']
        message = msg['message']
        self.buffer.add((sender, tuple(deps), message))
        self.process_buffer()

    def process_buffer(self):
        while True:
            deliverable = False
            for sender, deps, message in list(self.buffer):
                if all(deps[i] <= self.delivered[i] for i in range(self.num_nodes)):
                    print(f"Node {self.node_id} delivered broadcast message from Node {sender}: {message}")
                    self.buffer.remove((sender, deps, message))
                    self.delivered[sender] = max(self.delivered[sender], deps[sender]) + 1
                    deliverable = True
            if not deliverable:
                break

    def handle_private_message(self, msg):
        sender = msg['sender']
        if msg['clock'] == self.private_clocks[sender] + 1:
            print(f"Node {self.node_id} delivered private message from Node {sender}: {msg['message']}")
            self.private_clocks[sender] = msg['clock']
        else:
            print(f"Node {self.node_id} received out-of-order private message from Node {sender}: {msg['message']}")

    def stop(self):
        self.running = False
        self.sock.close()
        self.recv_thread.join()

    def print_clocks(self):
        print(f"Node {self.node_id} delivered clock: {self.delivered}")
        print(f"Node {self.node_id} private clocks: {self.private_clocks}")

if __name__ == "__main__":
    nodes = []
    num_nodes = 9

    for i in range(num_nodes):
        nodes.append(Node(i, num_nodes, 'localhost', 7000 + i))

    # Give some time for all threads to start
    time.sleep(2)

    # Broadcast messages from various nodes
    nodes[0].broadcast("Hello from Node 0")
    nodes[1].broadcast("Hello from Node 1")
    nodes[2].broadcast("Hello from Node 2")

    # Private messages between nodes
    nodes[3].send_private_message(4, "Private Hello from Node 3 to Node 4")
    nodes[5].send_private_message(6, "Private Hello from Node 5 to Node 6")
    nodes[7].send_private_message(8, "Private Hello from Node 7 to Node 8")

    # Give some time for message processing
    time.sleep(5)

    # Stop all nodes and print their clocks
    for node in nodes:
        node.stop()

    # Allow some time for threads to stop
    time.sleep(1)

    # Print clocks for all nodes
    for node in nodes:
        node.print_clocks()
