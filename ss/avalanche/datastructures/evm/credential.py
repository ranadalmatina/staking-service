"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization#credentials
"""

from ..base import DataStructure
from ss.avalanche.tools import num_to_int


class SECP256K1Credential(DataStructure):
    def __init__(self, signatures: list[bytes]):
        self.type_id = num_to_int(0x00000009)
        self.signatures = signatures
        assert len(self.type_id) == 4
        for signature in self.signatures:
            assert len(signature) == 65

    def _signatures_bytes(self):
        signatures_byte_list = [sig for sig in self.signatures]
        num_inputs = num_to_int(len(self.signatures))
        return num_inputs + b''.join(signatures_byte_list)

    def to_bytes(self):
        return self.type_id + self._signatures_bytes()

Credential = SECP256K1Credential
