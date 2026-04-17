import json
from wallet import Wallet

class Transaction:
    """
    Represents a transfer of coins between two wallets.
    Must be signed by the sender before being broadcast to the network.
    """

    def __init__(self, sender_public_key: str, recipient_public_key: str, amount: float):
        self.sender_public_key = sender_public_key
        self.recipient_public_key = recipient_public_key
        self.amount = amount
        self.signature: str = ""

    def to_dict(self) -> dict:
        return {
            'sender': self.sender_public_key,
            'recipient': self.recipient_public_key,
            'amount': self.amount
        }

    def sign(self, wallet: Wallet) -> None:
        """
        Signs the transaction with the sender's wallet.
        Raises an error if the wallet doesn't match the sender.
        """
        if wallet.get_public_key() != self.sender_public_key:
            raise Exception("You can only sign transactions from your own wallet.")
        data = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = wallet.sign(data)

    def is_valid(self) -> bool:
        """
        Verifies the transaction signature.
        Returns False if unsigned or if the signature doesn't match.
        """
        if not self.signature:
            return False
        data = json.dumps(self.to_dict(), sort_keys=True)
        return Wallet.verify(self.sender_public_key, data, self.signature)

    def __repr__(self) -> str:
        return f"Transaction(from={self.sender_public_key[:8]}..., to={self.recipient_public_key[:8]}..., amount={self.amount})"
