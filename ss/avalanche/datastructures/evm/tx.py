"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from ..base import DataStructure
from ss.avalanche.tools import num_to_int
from .credential import Credential


class EVMExportTx(DataStructure):
    """
    Unsigned EVM Export transaction.
    """

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

    def _inputs_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.inputs]
        num_inputs = num_to_int(len(self.inputs))
        return num_inputs + b''.join(input_byte_list)

    def _outputs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.exportedOutputs]
        num_outputs = num_to_int(len(self.exportedOutputs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        return (self.typeID + self.networkID + self.blockchainID + self.destinationChain +
               self._inputs_bytes() + self._outputs_bytes())


class EVMImportTx(DataStructure):
    """
    Unsigned EVM Import transaction.
    """

    def __init__(self, networkID: bytes, blockchainID: bytes, sourceChain: bytes,  # noqa
                 importedInputs: list[TransferableInput], outs: list[EVMOutput]):  # noqa
        # typeID for an ImportTx is 0
        self.typeID = num_to_int(0)
        self.networkID = networkID
        self.blockchainID = blockchainID
        self.sourceChain = sourceChain
        self.importedInputs = importedInputs
        self.outs = outs
        assert len(self.typeID) == 4
        assert len(self.networkID) == 4
        assert len(self.blockchainID) == 32
        assert len(self.sourceChain) == 32

    def _inputs_bytes(self) -> bytes:
        input_byte_list = [input.to_bytes() for input in self.importedInputs]
        num_inputs = num_to_int(len(self.importedInputs))
        return num_inputs + b''.join(input_byte_list)

    def _outputs_bytes(self) -> bytes:
        output_byte_list = [output.to_bytes() for output in self.outs]
        num_outputs = num_to_int(len(self.outs))
        return num_outputs + b''.join(output_byte_list)

    def to_bytes(self) -> bytes:
        return (self.typeID + self.networkID + self.blockchainID + self.sourceChain +
               self._inputs_bytes() + self._outputs_bytes())


AtomicTx = EVMExportTx | EVMImportTx

class SignedTransaction(DataStructure):
    """
    Contains an unsigned AtomicTX and credentials.
    """

    def __init__(self, atomic_tx: AtomicTx, credentials: list[Credential]):
        self.codec_id = b'00'
        self.atomic_tx = atomic_tx
        self.credentials = credentials
        assert len(self.codec_id) == 2

    def _credentials_bytes(self) -> bytes:
        credential_byte_list = [credential.to_bytes() for credential in self.credentials]
        num_credentials = num_to_int(len(self.credentials))
        return num_credentials + b''.join(credential_byte_list)

    def to_bytes(self) -> bytes:
        return self.codec_id + self.atomic_tx.to_bytes() + self._credentials_bytes()
