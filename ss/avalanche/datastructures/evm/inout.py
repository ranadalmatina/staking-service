"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from hexbytes import HexBytes
from avalanche.tools import num_to_uint32, uint_to_num
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

    def __len__(self):
        return 60

    @classmethod
    def from_bytes(cls, raw: bytes):
        assert len(raw) == 60
        address = raw[0:20]
        amount = raw[20:28]
        asset_id = raw[28:60]
        return cls(address, amount, asset_id)

    def to_dict(self) -> dict:
        return {
            'address': HexBytes(self.address).hex(),
            'amount': uint_to_num(self.amount),
            'asset_id': HexBytes(self.asset_id).hex(),
        }


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

    def __len__(self):
        return 68

    @classmethod
    def from_bytes(cls, raw: bytes):
        assert len(raw) == 68
        address = raw[0:20]
        amount = raw[20:28]
        asset_id = raw[28:60]
        nonce = raw[60:68]
        return cls(address, amount, asset_id, nonce)

    def to_dict(self) -> dict:
        return {
            'address': HexBytes(self.address).hex(),
            'amount': uint_to_num(self.amount),
            'asset_id': HexBytes(self.asset_id).hex(),
            'nonce': uint_to_num(self.nonce),
        }


class SECPTransferOutput(DataStructure):
    """
    A secp256k1 transfer output allows for sending a quantity of an asset
    to a collection of addresses after a specified unix time.
    """
    TYPE_ID = num_to_uint32(0x00000007)

    def __init__(self, amount: bytes, locktime: bytes, threshold: bytes, addresses: list[bytes]):
        self.type_id = self.TYPE_ID
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
        num_addresses = num_to_uint32(len(self.addresses))
        return num_addresses + b''.join(self.addresses)

    def to_bytes(self):
        return self.type_id + self.amount + self.locktime + self.threshold + self._address_bytes()

    def __len__(self):
        return 28 + 20 * len(self.addresses)

    @classmethod
    def from_bytes(cls, raw: bytes):
        type_id = raw[0:4]
        assert type_id == cls.TYPE_ID
        amount = raw[4:12]
        locktime = raw[12:20]
        threshold = raw[20:24]
        num_addresses = uint_to_num(raw[24:28])
        assert num_addresses == 1
        addresses = [raw[28:48]]
        return cls(amount, locktime, threshold, addresses)

    def to_dict(self) -> dict:
        addresses_hex = [HexBytes(address).hex() for address in self.addresses]
        return {
            'amount': uint_to_num(self.amount),
            'locktime': uint_to_num(self.locktime),
            'threshold': uint_to_num(self.threshold),
            'addresses': addresses_hex,
        }


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

    def __len__(self):
        return 32 + len(self.output)

    @classmethod
    def from_bytes(cls, raw: bytes):
        asset_id = raw[0:32]
        output = SECPTransferOutput.from_bytes(raw[32:])
        return cls(asset_id, output)

    def to_dict(self) -> dict:
        return {
            'asset_id': HexBytes(self.asset_id).hex(),
            'output': self.output.to_dict()
        }


class SECPTransferInput(DataStructure):
    """
    A secp256k1 transfer input allows for spending an unspent secp256k1 transfer output.
    """
    TYPE_ID = num_to_uint32(0x00000005)

    def __init__(self, amount: bytes, address_indices: list[bytes]):
        self.type_id = self.TYPE_ID
        self.amount = amount
        self.address_indices = address_indices
        assert len(self.type_id) == 4
        assert len(self.amount) == 8
        for address_index in self.address_indices:
            assert len(address_index) == 4

    def _address_indices_bytes(self):
        num_indices = num_to_uint32(len(self.address_indices))
        return num_indices + b''.join(self.address_indices)

    def to_bytes(self):
        return self.type_id + self.amount + self._address_indices_bytes()

    def __len__(self):
        return 16 + 4 * len(self.address_indices)

    @classmethod
    def from_bytes(cls, raw: bytes):
        type_id = raw[0:4]
        assert type_id == cls.TYPE_ID
        amount = raw[4:12]
        num_indices = uint_to_num(raw[12:16])
        # Parse all address indices
        address_indices = []
        offset = 16
        for i in range(num_indices):
            address_indices.append(raw[offset:offset + 4])
            offset += 4
        return cls(amount, address_indices)

    def to_dict(self) -> dict:
        return {
            'amount': uint_to_num(self.amount),
            'address_indices': [uint_to_num(addr_indx) for addr_indx in self.address_indices]
        }


class TransferableInput(DataStructure):
    """
    Transferable Input wraps a SECP256K1TransferInput.
    Transferable inputs describe a specific UTXO with a provided transfer input.
    """

    def __init__(self, tx_id: bytes, utxo_index: bytes, asset_id: bytes, input: SECPTransferInput):
        self.tx_id = tx_id
        self.utxo_index = utxo_index
        self.asset_id = asset_id
        self.input = input
        assert len(self.tx_id) == 32
        assert len(self.utxo_index) == 4
        assert len(self.asset_id) == 32

    def to_bytes(self):
        return self.tx_id + self.utxo_index + self.asset_id + self.input.to_bytes()

    def __len__(self):
        return 68 + len(self.input)

    @classmethod
    def from_bytes(cls, raw: bytes):
        tx_id = raw[0:32]
        utxo_index = raw[32:36]
        asset_id = raw[36:68]
        input = SECPTransferInput.from_bytes(raw[68:])
        return cls(tx_id, utxo_index, asset_id, input)

    def to_dict(self) -> dict:
        return {
            'tx_id': HexBytes(self.tx_id).hex(),
            'utxo_index': uint_to_num(self.utxo_index),
            'asset_id': HexBytes(self.asset_id).hex(),
            'input': self.input.to_dict(),
        }
