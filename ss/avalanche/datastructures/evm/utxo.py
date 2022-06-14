from hexbytes import HexBytes

from avalanche.tools import num_to_uint16, uint_to_num

from ..base import DataStructure
from .inout import SECPTransferOutput


class UTXO(DataStructure):
    """
    A UTXO is a standalone representation of a transaction output.
    """
    CODEC_ID = num_to_uint16(0)

    def __init__(self, tx_id: bytes, output_index: bytes, asset_id: bytes, output: SECPTransferOutput):
        self.codec_id = self.CODEC_ID
        self.tx_id = tx_id
        self.output_index = output_index
        self.asset_id = asset_id
        self.output = output
        assert len(self.codec_id) == 2
        assert len(self.tx_id) == 32
        assert len(self.output_index) == 4
        assert len(self.asset_id) == 32

    def to_bytes(self):
        return self.codec_id + self.tx_id + self.output_index + self.asset_id + self.output.to_bytes()

    def __len__(self):
        return 70 + len(self.output)

    @classmethod
    def from_bytes(cls, raw: bytes):
        codec_id = raw[0:2]
        assert codec_id == cls.CODEC_ID
        tx_id = raw[2:34]
        utxo_index = raw[34:38]
        asset_id = raw[38:70]
        output = SECPTransferOutput.from_bytes(raw[70:])
        return cls(tx_id, utxo_index, asset_id, output)

    def to_dict(self) -> dict:
        return {
            'tx_id': HexBytes(self.tx_id).hex(),
            'output_index': uint_to_num(self.output_index),
            'asset_id': HexBytes(self.asset_id).hex(),
            'output': self.output.to_dict()
        }
