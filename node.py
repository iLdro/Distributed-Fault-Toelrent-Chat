# node.py

import socket
import threading
import time

class Node:
    def __init__(self, own_ip):
        self.own_ip = own_ip
        self.neighbors = set()  # Using a set to store neighbors for uniqueness
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        self.sock.bind((self.own_ip, 10000))  # Bind to own_ip and port 10000 for messaging
        self.message_history = []
        self.lamport_clock = 0  # Initial Lamport clock value
        print(f"Node initialized with IP {self.own_ip}")

    def send_message(self, message, dest_ip):
        self.lamport_clock += 1  # Increment Lamport clock before sending message
        message_with_timestamp = f"{self.lamport_clock}:{message}"
        self.sock.sendto(message_with_timestamp.encode(), (dest_ip, 10000))
        print(f"Node {self.own_ip} sent message to {dest_ip}: {message_with_timestamp}")

    def receive_messages(self):
        print(f"Node {self.own_ip} started receiving messages...")
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode()
                print(f"Node {self.own_ip} received raw message: {message}")

                if message.startswith("new node Connected:"):
                    new_neighbor_ip = message.split(":")[1]
                    if new_neighbor_ip != self.own_ip and new_neighbor_ip not in self.neighbors:
                        self.neighbors.add(new_neighbor_ip)
                        print(f"Connection established with {new_neighbor_ip} from node {self.own_ip}")
                    return


                parts = message.split(':', 1)
                if len(parts) < 2:
                    # Ignore messages that do not contain a valid timestamp
                    continue

                timestamp_str, actual_message = parts
                try:
                    timestamp = int(timestamp_str)
                except ValueError:
                    # Handle case where timestamp is not a valid integer
                    print(f"Ignoring invalid message format: {message}")
                    continue

                print(f"Node {self.own_ip} received message with timestamp {timestamp}: {actual_message}")

                # Update Lamport clock
                self.lamport_clock = max(self.lamport_clock, timestamp) + 1

                # Process message based on actual content
                self.process_message(actual_message)
            except Exception as e:
                print(f"Error receiving message on node {self.own_ip}: {e}")

    def process_message(self, message):
        print(f"Node {self.own_ip} processing message: {message}")

    def send_connection_message(self):
        time.sleep(1)  # Ensure other nodes are ready
        print(f"Node {self.own_ip} sending connection message...")
        self.broadcast_message(f"new node Connected:{self.own_ip}")

    def broadcast_message(self, message):
        self.sock.sendto(message.encode(), ('255.255.255.255', 10000))  # Broadcast message to all nodes

    def print_neighbors(self):
        print(f"Node {self.own_ip} neighbors: {self.neighbors}")

    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        time.sleep(2)
        self.send_connection_message()
        print(f"Node {self.own_ip} started and sent connection message")
