"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/avm-transaction-serialization
"""

from avalanche.constants import XChainAlias
from hexbytes import HexBytes
from avalanche.tools import num_to_uint32, uint_to_num
from ..base import DataStructure
from ..evm.inout import TransferableInput, TransferableOutput


class BaseTx(DataStructure):
    """
    AVM Base Transaction
    """
    TYPE_ID = num_to_uint32(0)

    def __init__(self, network_id: bytes, blockchain_id: bytes, outputs: list[TransferableOutput],
                 inputs: list[TransferableInput], memo: bytes):
        # typeID for an BaseTx is 0
        self.type_id = self.TYPE_ID
        self.network_id = network_id
        self.blockchain_id = blockchain_id
        self.outputs = outputs
        self.inputs = inputs
        self.memo = memo
        assert len(self.type_id) == 4
        assert len(self.network_id) == 4
        assert len(self.blockchain_id) == 32
        assert len(self.memo) < 256

    def _inputs_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.inputs]
        num_inputs = num_to_uint32(len(self.inputs))
        return num_inputs + b''.join(input_byte_list)

    def _outputs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.outputs]
        num_outputs = num_to_uint32(len(self.outputs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        memo_len = num_to_uint32(len(self.memo))
        return (self.type_id + self.network_id + self.blockchain_id + self._outputs_bytes() +
                self._inputs_bytes() + memo_len + self.memo)

    def __len__(self):
        size_outputs = sum([len(output) for output in self.outputs])
        size_inputs = sum([len(input) for input in self.inputs])
        return 52 + size_outputs + size_inputs + len(self.memo)

    @classmethod
    def from_bytes(cls, raw: bytes):
        # Ignore type_id check because it is changed by "subclasses"
        network_id = raw[4:8]
        blockchain_id = raw[8:40]
        # Generate outputs
        outputs = []
        num_outputs = uint_to_num(raw[40:44])
        offset = 44
        for i in range(num_outputs):
            output = TransferableOutput.from_bytes(raw[offset:])
            offset += len(output)
            outputs.append(output)
        # Generate inputs
        inputs = []
        num_inputs = uint_to_num(raw[offset:offset + 4])
        offset += 4
        for i in range(num_inputs):
            input = TransferableInput.from_bytes(raw[offset:])
            offset += len(input)
            inputs.append(input)
        memo_len = uint_to_num(raw[offset:offset + 4])
        offset += 4
        memo = raw[offset:offset + memo_len]
        return cls(network_id, blockchain_id, outputs, inputs, memo)

    def to_dict(self) -> dict:
        return {
            'network_id': uint_to_num(self.network_id),
            'blockchain_id': HexBytes(self.blockchain_id).hex(),
            'inputs': [input.to_dict() for input in self.inputs],
            'outputs': [output.to_dict() for output in self.outputs],
            'memo': self.memo.decode('utf-8')
        }


class AVMImportTx(DataStructure):
    """
    AVM Unsigned Import TX
    """
    TYPE_ID = num_to_uint32(3)
    SOURCE_CHAIN = XChainAlias

    def __init__(self, base_tx: BaseTx, source_chain: bytes, ins: list[TransferableInput]):
        self.base_tx = base_tx
        # BaseTX has its type_id changed
        self.base_tx.type_id = self.TYPE_ID
        self.source_chain = source_chain
        self.ins = ins
        assert len(self.source_chain) == 32

    def _ins_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.ins]
        num_inputs = num_to_uint32(len(self.ins))
        return num_inputs + b''.join(input_byte_list)

    def to_bytes(self) -> bytes:
        return self.base_tx.to_bytes() + self.source_chain + self._ins_bytes()

    def __len__(self):
        size_ins = sum([len(input) for input in self.ins])
        return 36 + size_ins + len(self.base_tx)

    @classmethod
    def from_bytes(cls, raw: bytes):
        type_id = raw[0:4]
        assert type_id == cls.TYPE_ID
        base = BaseTx.from_bytes(raw)
        offset = len(base)
        source_chain = raw[offset:offset+32]
        num_inputs = uint_to_num(raw[offset+32:offset+36])
        assert num_inputs == 1
        input = TransferableInput.from_bytes(raw[offset+36:])
        return cls(base, source_chain, [input])

    def to_dict(self) -> dict:
        return {
            'base_tx': self.base_tx.to_dict(),
            'source_chain': HexBytes(self.source_chain).hex(),
            'ins': [input.to_dict() for input in self.ins],
        }


class AVMExportTx(DataStructure):
    """
    AVM Unsigned Export TX
    """
    TYPE_ID = num_to_uint32(4)
    SOURCE_CHAIN = XChainAlias

    def __init__(self, base_tx: BaseTx, destination_chain: bytes, outs: list[TransferableOutput]):
        self.base_tx = base_tx
        # BaseTX has its type_id changed
        self.base_tx.type_id = self.TYPE_ID
        self.destination_chain = destination_chain
        self.outs = outs
        assert len(self.destination_chain) == 32

    def _outs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.outs]
        num_outputs = num_to_uint32(len(self.outs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        return self.base_tx.to_bytes() + self.destination_chain + self._outs_bytes()

    def __len__(self):
        size_outs = sum([len(output) for output in self.outs])
        return 36 + size_outs + len(self.base_tx)

    @classmethod
    def from_bytes(cls, raw: bytes):
        type_id = raw[0:4]
        assert type_id == cls.TYPE_ID
        base = BaseTx.from_bytes(raw)
        offset = len(base)
        destination_chain = raw[offset:offset + 32]
        num_outputs = uint_to_num(raw[offset + 32:offset + 36])
        assert num_outputs == 1
        output = TransferableOutput.from_bytes(raw[offset + 36:])
        return cls(base, destination_chain, [output])

    def to_dict(self) -> dict:
        return {
            'base_tx': self.base_tx.to_dict(),
            'destination_chain': HexBytes(self.destination_chain).hex(),
            'outs': [output.to_dict() for output in self.outs],
        }
