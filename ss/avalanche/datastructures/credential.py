"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization#credentials
"""

from ..base import DataStructure
from hexbytes import HexBytes
from avalanche.tools import num_to_uint32


class SECP256K1Credential(DataStructure):
    """
    A secp256k1 credential contains a list of 65-byte recoverable signatures.
    """
    TYPE_ID = num_to_uint32(0x00000009)

    def __init__(self, signatures: list[bytes]):
        self.type_id = self.TYPE_ID
        self.signatures = signatures
        assert len(self.type_id) == 4
        for signature in self.signatures:
            assert len(signature) == 65

    def _signatures_bytes(self):
        signatures_byte_list = [sig for sig in self.signatures]
        num_inputs = num_to_uint32(len(self.signatures))
        return num_inputs + b''.join(signatures_byte_list)

    def to_bytes(self):
        return self.type_id + self._signatures_bytes()

    def __len__(self):
        return 8 + 65 * len(self.signatures)

    def to_dict(self) -> dict:
        return {
            'signatures': [HexBytes(sig).hex() for sig in self.signatures]
        }

Credential = SECP256K1Credential
