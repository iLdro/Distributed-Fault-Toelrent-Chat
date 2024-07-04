# main.py

import time
from node import Node  # Import your Node class from node.py

if __name__ == "__main__":
    print("Starting main script...")
    
    # Create nodes with respective IP addresses
    node1 = Node(own_ip='127.0.0.1')
    node2 = Node(own_ip='127.0.0.2')
    node3 = Node(own_ip='127.0.0.3')

    # Start nodes
    node1.start()
    node2.start()
    node3.start()

    # Wait for nodes to connect and update neighbors
    time.sleep(5)  # Adjust timing as needed to ensure nodes connect

    # Print initial neighbors (should be empty initially)
    node1.print_neighbors()
    node2.print_neighbors()
    node3.print_neighbors()


    print("Main script complete")
