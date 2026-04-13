import hashlib
import json

class Block:
    """
    Represents a single block in the blockchain. Each block holds a list of transactions,
    a reference to the previous block's hash, and a nonce used during mining. 

    compute_hash() computes the hash for the current block from all fields except itself.
    """
    def __init__(self, index: int, timestamp: float, transactions: list, prev_hash: str, nonce: int = 0, hash: str = ""):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.hash = hash

    def compute_hash(self):
        data = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'prev_hash': self.prev_hash,
            'nonce': self.nonce
        })

        encoded = data.encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()
