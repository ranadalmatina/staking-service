"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from ss.avalanche.tools import num_to_int
from ..base import DataStructure


class EVMOutput(DataStructure):
    """
    Output type specifying a state change to be applied to an EVM account as part of an ImportTx.
    """

    def __init__(self, address: bytes, amount: bytes, asset_id: bytes):
        self.address = address
        self.amount = amount
        self.asset_id = asset_id
        assert len(self.address) == 20
        assert len(self.amount) == 8
        assert len(self.asset_id) == 32

    def to_bytes(self):
        return self.address + self.amount + self.asset_id


class EVMInput(EVMOutput):
    """
    Input type that specifies an EVM account to deduct the funds from as part of an ExportTx.
    """

    def __init__(self, address: bytes, amount: bytes, asset_id: bytes, nonce: bytes):
        super().__init__(address, amount, asset_id)
        self.nonce = nonce
        assert len(self.nonce) == 8

    def to_bytes(self):
        return self.address + self.amount + self.asset_id + self.nonce


class SECPTransferOutput(DataStructure):
    """
    A secp256k1 transfer output allows for sending a quantity of an asset
    to a collection of addresses after a specified unix time.
    """

    def __init__(self, amount: bytes, locktime: bytes, threshold: bytes, addresses: list[bytes]):
        self.type_id = num_to_int(0x00000007)
        self.amount = amount
        self.locktime = locktime
        self.threshold = threshold
        self.addresses = addresses
        assert len(self.type_id) == 4
        assert len(self.amount) == 8
        assert len(self.locktime) == 8
        assert len(self.threshold) == 4
        for address in self.addresses:
            assert len(address) == 20

    def _address_bytes(self):
        num_addresses = num_to_int(len(self.addresses))
        return num_addresses + b''.join(self.addresses)

    def to_bytes(self):
        return self.type_id + self.amount + self.locktime + self.threshold + self._address_bytes()


class TransferableOutput(DataStructure):
    """
    Transferable outputs wrap a SECP256K1TransferOutput with an asset ID.
    """

    def __init__(self, asset_id: bytes, output: SECPTransferOutput):
        self.asset_id = asset_id
        self.output = output
        assert len(self.asset_id) == 32

    def to_bytes(self):
        return self.asset_id + self.output.to_bytes()
