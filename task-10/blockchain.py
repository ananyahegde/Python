import time
import hashlib
import json
from block import Block

class Blockchain:
    """
    Represents the full chain of blocks.
    Handles block addition and chain validation.
    """

    def __init__(self):
        self.chain: list[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Creates the first block in the chain with hardcoded values."""
        genesis = Block(
            index=0,
            timestamp=1231006505,
            transactions=[],
            prev_hash="0" * 64
        )
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        """
        Validates and adds a new block to the chain.
        Returns True if added, False if invalid.
        """
        last = self.get_last_block()

        if block.prev_hash != last.hash:
            return False

        if block.hash != block.compute_hash():
            return False

        self.chain.append(block)
        return True

    def is_valid(self) -> bool:
        """
        Walks the entire chain and verifies every block.
        Checks hash integrity and linkage between blocks.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False

            if current.prev_hash != previous.hash:
                return False

        return True
