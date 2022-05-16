"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from typing import Union
import hashlib
from ..base import DataStructure
from avalanche.tools import num_to_uint16, num_to_uint32, uint_to_num
from .credential import Credential
from .inout import EVMInput, EVMOutput, TransferableInput, TransferableOutput

class EVMExportTx(DataStructure):
    """
    Unsigned EVM Export transaction.
    """
    TYPE_ID = num_to_uint32(1)

    def __init__(self, network_id: bytes, blockchain_id: bytes, destination_chain: bytes,
                 inputs: list[EVMInput], exported_outs: list[TransferableOutput]):
        # typeID for an ExportTx is 1
        self.type_id = self.TYPE_ID
        self.network_id = network_id
        self.blockchain_id = blockchain_id
        self.destination_chain = destination_chain
        self.inputs = inputs
        self.exported_outs = exported_outs
        assert len(self.type_id) == 4
        assert len(self.network_id) == 4
        assert len(self.blockchain_id) == 32
        assert len(self.destination_chain) == 32

    def _inputs_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.inputs]
        num_inputs = num_to_uint32(len(self.inputs))
        return num_inputs + b''.join(input_byte_list)

    def _outputs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.exported_outs]
        num_outputs = num_to_uint32(len(self.exported_outs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        return self.type_id + self.network_id + self.blockchain_id + self.destination_chain + self._inputs_bytes() + self._outputs_bytes()

    def __len__(self):
        return 80 + len(self.inputs) + len(self.exported_outs)

    @classmethod
    def _inputs_from_bytes(cls, raw: bytes):
        num_inputs = uint_to_num(raw[72:76])
        start_offset = 76
        end_offset = start_offset + 68  #EVMInput always 68 bytes long
        inputs = []
        # For now we know there is only one input, later remove this check
        assert num_inputs == 1
        for i in range(num_inputs):
            inputs.append(EVMInput.from_bytes(raw[start_offset:end_offset]))
            start_offset = end_offset
            end_offset += 68
        return inputs

    @classmethod
    def from_bytes(cls, raw: bytes):
        type_id = raw[0:4]
        assert type_id == cls.TYPE_ID
        network_id = raw[4:8]
        blockchain_id = raw[8:40]
        destination_chain = raw[40:72]
        inputs = cls._inputs_from_bytes(raw)
        # Generate outputs
        output_offset = 76 + 68 * len(inputs)
        num_outputs = uint_to_num(raw[output_offset:output_offset+4])
        assert num_outputs == 1
        exported_outs = TransferableOutput.from_bytes(raw[output_offset+4:])
        return cls(network_id, blockchain_id, destination_chain, inputs, exported_outs)



class EVMImportTx(DataStructure):
    """
    Unsigned EVM Import transaction.
    """

    def __init__(self, network_id: bytes, blockchain_id: bytes, source_chain: bytes,
                 imported_inputs: list[TransferableInput], outs: list[EVMOutput]):
        # typeID for an ImportTx is 0
        self.type_id = num_to_uint32(0)
        self.network_id = network_id
        self.blockchain_id = blockchain_id
        self.source_chain = source_chain
        self.imported_inputs = imported_inputs
        self.outs = outs
        assert len(self.type_id) == 4
        assert len(self.network_id) == 4
        assert len(self.blockchain_id) == 32
        assert len(self.source_chain) == 32

    def _inputs_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.imported_inputs]
        num_inputs = num_to_uint32(len(self.imported_inputs))
        return num_inputs + b''.join(input_byte_list)

    def _outputs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.outs]
        num_outputs = num_to_uint32(len(self.outs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        return (self.type_id + self.network_id + self.blockchain_id + self.source_chain +
               self._inputs_bytes() + self._outputs_bytes())


# TODO upgrade to Python 3.10
AtomicTx = Union[EVMExportTx, EVMImportTx]


class UnsignedTransaction(DataStructure):
    """
    Undocumented UnsignedTransaction ported from Avalanche.js
    """

    def __init__(self, atomic_tx: AtomicTx):
        self.codec_id = num_to_uint16(0)
        self.atomic_tx = atomic_tx
        assert len(self.codec_id) == 2

    def to_bytes(self) -> bytes:
        return self.codec_id + self.atomic_tx.to_bytes()

    def hash(self) -> bytes:
        m = hashlib.sha256()
        m.update(self.to_bytes())
        return m.digest()

    @classmethod
    def from_bytes(cls, raw: bytes):
        codec_id = uint_to_num(raw[0:2])
        assert codec_id == 0
        atomic_tx = EVMExportTx.from_bytes(raw[2:])
        return cls(atomic_tx)



class SignedTransaction(DataStructure):
    """
    Contains an unsigned AtomicTX and credentials.
    """

    def __init__(self, atomic_tx: AtomicTx, credentials: list[Credential]):
        self.codec_id = num_to_uint16(0)
        self.atomic_tx = atomic_tx
        self.credentials = credentials
        assert len(self.codec_id) == 2

    def _credentials_bytes(self) -> bytes:
        credential_byte_list = [credential.to_bytes() for credential in self.credentials]
        num_credentials = num_to_uint32(len(self.credentials))
        return num_credentials + b''.join(credential_byte_list)

    def to_bytes(self) -> bytes:
        return self.codec_id + self.atomic_tx.to_bytes() + self._credentials_bytes()
