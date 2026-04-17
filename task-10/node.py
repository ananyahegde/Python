import socket
import threading
import json
import time
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from block import Block

class Node:
    """
    Represents a single participant in the blockchain network.
    Runs a socket server to communicate with peers, mines blocks,
    manages a mempool, and maintains its own copy of the blockchain.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.wallet = Wallet()
        self.blockchain = Blockchain()
        self.mempool: list[Transaction] = []
        self.peers: list[tuple] = []
        self.DIFFICULTY = 4

    def start(self):
        """Starts the node's socket server in a background thread."""
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()
        print(f"[NODE-{self.port}] Listening on port {self.port} | Wallet: {self.wallet.get_address()}")

    def _listen(self):
        """Listens for incoming peer connections."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self._handle_peer, args=(conn,), daemon=True)
            thread.start()

    def _handle_peer(self, conn: socket.socket):
        """Handles an incoming message from a peer."""
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            message = json.loads(data.decode())
            self._process_message(message)
        except Exception as e:
            print(f"[NODE-{self.port}] Error handling peer: {e}")
        finally:
            conn.close()

    def _process_message(self, message: dict):
        """Routes incoming messages to the correct handler."""
        if message['type'] == 'block':
            self._receive_block(message['data'])
        elif message['type'] == 'transaction':
            self._receive_transaction(message['data'])

    def connect_to_peer(self, host: str, port: int):
        """Registers a peer node to broadcast to."""
        self.peers.append((host, port))
        print(f"[NODE-{self.port}] Connected to peer {port}")

    def _broadcast(self, message: dict):
        """Sends a message to all known peers."""
        for host, port in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                s.sendall(json.dumps(message).encode())
                s.close()
            except Exception as e:
                print(f"[NODE-{self.port}] Failed to reach peer {port}: {e}")

    def create_transaction(self, recipient_public_key: str, amount: float):
        """Creates, signs, and broadcasts a transaction."""
        tx = Transaction(self.wallet.get_public_key(), recipient_public_key, amount)
        tx.sign(self.wallet)
        if tx.is_valid():
            self.mempool.append(tx)
            self._broadcast({
                'type': 'transaction',
                'data': {
                    'sender': tx.sender_public_key,
                    'recipient': tx.recipient_public_key,
                    'amount': tx.amount,
                    'signature': tx.signature
                }
            })
            print(f"[NODE-{self.port}] Transaction created: {tx}")

    def _receive_transaction(self, data: dict):
        """Validates and adds an incoming transaction to the mempool."""
        tx = Transaction(data['sender'], data['recipient'], data['amount'])
        tx.signature = data['signature']
        if tx.is_valid():
            self.mempool.append(tx)
            print(f"[NODE-{self.port}] Transaction received and added to mempool")

    def mine(self):
        """
        Mines a new block from mempool transactions.
        Finds a nonce such that the block hash starts with
        enough zeros to satisfy the difficulty target.
        """
        if not self.mempool:
            print(f"[NODE-{self.port}] Mempool is empty, nothing to mine")
            return

        transactions = self.mempool[:5]
        last_block = self.blockchain.get_last_block()

        block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            transactions=[t.to_dict() for t in transactions],
            prev_hash=last_block.hash
        )

        print(f"[NODE-{self.port}] Mining block #{block.index} ({len(transactions)} transactions)...")
        print(f"Difficulty: {self.DIFFICULTY} (hash must start with '{'0' * self.DIFFICULTY}')")

        start = time.time()
        while not block.hash.startswith("0" * self.DIFFICULTY):
            block.nonce += 1
            block.hash = block.compute_hash()

        elapsed = time.time() - start
        print(f"[NODE-{self.port}] Block #{block.index} mined in {elapsed:.2f}s")
        print(f"Hash: {block.hash}")
        print(f"Nonce: {block.nonce}")

        self.blockchain.chain.append(block)

        for tx in transactions:
            self.mempool.remove(tx)

        self._broadcast_block(block)

    def _broadcast_block(self, block: Block):
        """Serializes and broadcasts a mined block to all peers."""
        print(f"[NODE-{self.port}] Broadcasting block #{block.index} to peers...")
        self._broadcast({
            'type': 'block',
            'data': {
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': block.transactions,
                'prev_hash': block.prev_hash,
                'nonce': block.nonce,
                'hash': block.hash
            }
        })

    def _receive_block(self, data: dict):
        """Validates and appends a block received from a peer."""
        block = Block(
            index=data['index'],
            timestamp=data['timestamp'],
            transactions=data['transactions'],
            prev_hash=data['prev_hash'],
            nonce=data['nonce']
        )
        block.hash = data['hash']

        if self.blockchain.add_block(block):
            print(f"[NODE-{self.port}] Received block #{block.index} — Accepted (chain height: {len(self.blockchain.chain)})")
        else:
            print(f"[NODE-{self.port}] Received block #{block.index} — Rejected")

    def get_balance(self, public_key: str) -> float:
        """
        Calculates a wallet's balance by walking the entire chain.
        Balance = all coins received - all coins sent.
        """
        balance = 0.0
        for block in self.blockchain.chain:
            for tx in block.transactions:
                if tx['recipient'] == public_key:
                    balance += tx['amount']
                if tx['sender'] == public_key:
                    balance -= tx['amount']
        return balance
