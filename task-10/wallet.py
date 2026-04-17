from ecdsa import SigningKey, SECP256k1
import hashlib

class Wallet:
    """
    Represents a participant in the network.
    Holds a public/private key pair used to sign and verify transactions.
    """

    def __init__(self):
        self._private_key = SigningKey.generate(curve=SECP256k1)
        self._public_key = self._private_key.get_verifying_key()

    def get_address(self) -> str:
        """
        Returns a shortened hex representation of the public key.
        This is the wallet's public identity on the network.
        """
        return "0x" + self._public_key.to_string().hex()[:8] + "..."

    def get_public_key(self) -> str:
        """Returns the full public key as a hex string."""
        return self._public_key.to_string().hex()

    def sign(self, data: str) -> str:
        """
        Signs a string of data with the private key.
        Returns the signature as a hex string.
        """
        return self._private_key.sign(data.encode()).hex()

    @staticmethod
    def verify(public_key_hex: str, data: str, signature_hex: str) -> bool:
        """
        Verifies a signature against the data and public key.
        Returns True if valid, False otherwise.
        """
        from ecdsa import VerifyingKey, BadSignatureError
        try:
            vk = VerifyingKey.from_string(
                bytes.fromhex(public_key_hex),
                curve=SECP256k1
            )
            vk.verify(bytes.fromhex(signature_hex), data.encode())
            return True
        except BadSignatureError:
            return False
