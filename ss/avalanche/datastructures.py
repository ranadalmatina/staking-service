"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from hexbytes import HexBytes
from .tools import num_to_int

class EVMOutput:
    def __init__(self, address: bytes, amount: bytes, asset_id: bytes):
        self.address = address
        self.amount = amount
        self.asset_id = asset_id
        assert len(self.address) == 20
        assert len(self.amount) == 8
        assert len(self.asset_id) == 32

    def to_bytes(self, hex=False):
        serialized = self.address + self.amount + self.asset_id
        if hex:
            return HexBytes(serialized).hex()
        return serialized


class EVMInput(EVMOutput):
    def __init__(self, address: bytes, amount: bytes, asset_id: bytes, nonce: bytes):
        super().__init__(address, amount, asset_id)
        self.nonce = nonce
        assert len(self.nonce) == 8

    def to_bytes(self, hex=False):
        serialized = self.address + self.amount + self.asset_id + self.nonce
        if hex:
            return HexBytes(serialized).hex()
        return serialized


class SECPTransferOutput:
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
        for address in addresses:
            assert len(address) == 20

    def address_bytes(self):
        num_addresses = num_to_int(len(self.addresses))
        return num_addresses + b''.join(self.addresses)

    def to_bytes(self, hex=False):
        serialized = self.type_id + self.amount + self.locktime + self.threshold + self.address_bytes()
        if hex:
            return HexBytes(serialized).hex()
        return serialized


class TransferableOutput:
    def __init__(self, asset_id: bytes, output: SECPTransferOutput):
        self.asset_id = asset_id
        self.output = output
        assert len(self.asset_id) == 32

    def to_bytes(self, hex=False):
        serialized = self.asset_id + self.output.to_bytes()
        if hex:
            return HexBytes(serialized).hex()
        return serialized


class EVMExportTx:
    def __init__(self, networkID: bytes, blockchainID: bytes, destinationChain: bytes,  # noqa
                 inputs: list[EVMInput], exportedOutputs: list[TransferableOutput]):  # noqa
        # typeID for an ExportTx is 1
        self.typeID = num_to_int(1)
        self.networkID = networkID
        self.blockchainID = blockchainID
        self.destinationChain = destinationChain
        self.inputs = inputs
        self.exportedOutputs = exportedOutputs
        assert len(self.typeID) == 4
        assert len(self.networkID) == 4
        assert len(self.blockchainID) == 32
        assert len(self.destinationChain) == 32

    def inputs_bytes(self):
        input_byte_list = [input.to_bytes() for input in self.inputs]
        num_inputs = num_to_int(len(self.inputs))
        return num_inputs + b''.join(input_byte_list)

    def outputs_bytes(self):
        output_byte_list = [output.to_bytes() for output in self.exportedOutputs]
        num_outputs = num_to_int(len(self.exportedOutputs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self, hex=False):
        serialized = self.typeID + self.networkID + self.blockchainID + self.destinationChain + self.inputs_bytes() + self.outputs_bytes()
        if hex:
            return HexBytes(serialized).hex()
        return serialized
