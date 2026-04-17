import time
from node import Node
from wallet import Wallet

node1 = Node('localhost', 5001)
node2 = Node('localhost', 5002)
node3 = Node('localhost', 5003)
node4 = Node('localhost', 5004)

node1.start()
node2.start()
node3.start()
node4.start()

time.sleep(1)

node1.connect_to_peer('localhost', 5002)
node2.connect_to_peer('localhost', 5003)
node2.connect_to_peer('localhost', 5004)

time.sleep(1)

print("\n=== Peer Discovery ===\n")
node1.discover_peers()
time.sleep(1)
node2.discover_peers()
time.sleep(1)
node3.discover_peers()
time.sleep(1)
node4.discover_peers()

time.sleep(2)

print("\n=== Creating Transactions ===\n")
node1.create_transaction(node2.wallet.get_public_key(), 50)
time.sleep(1)
node2.create_transaction(node3.wallet.get_public_key(), 25)
time.sleep(1)
node3.create_transaction(node4.wallet.get_public_key(), 15)
time.sleep(1)
node4.create_transaction(node1.wallet.get_public_key(), 10)

time.sleep(2)

print("\n=== Mining Node 1 ===\n")
node1.mine()

time.sleep(2)

print("\n=== Mining Node 2 ===\n")
node2.mine()

time.sleep(3)

print("\n=== Balances ===\n")
print(f"Node1: {node1.get_balance(node1.wallet.get_public_key())}")
print(f"Node2: {node2.get_balance(node2.wallet.get_public_key())}")
print(f"Node3: {node3.get_balance(node3.wallet.get_public_key())}")
print(f"Node4: {node4.get_balance(node4.wallet.get_public_key())}")

print("\n=== Chain Lengths ===\n")
print(f"Node1 chain: {len(node1.blockchain.chain)} blocks")
print(f"Node2 chain: {len(node2.blockchain.chain)} blocks")
print(f"Node3 chain: {len(node3.blockchain.chain)} blocks")
print(f"Node4 chain: {len(node4.blockchain.chain)} blocks")

print("\n=== Peer Lists ===\n")
print(f"Node1 peers: {[p[1] for p in node1.peers]}")
print(f"Node2 peers: {[p[1] for p in node2.peers]}")
print(f"Node3 peers: {[p[1] for p in node3.peers]}")
print(f"Node4 peers: {[p[1] for p in node4.peers]}")
