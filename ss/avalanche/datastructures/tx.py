"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

import hashlib

from avalanche.tools import num_to_uint16, num_to_uint32, uint_to_num

from .avm.tx import AVMExportTx, AVMImportTx
from .base import DataStructure
from .credential import Credential
from .evm.tx import EVMExportTx, EVMImportTx
from .platform.tx import PlatformExportTx, PlatformImportTx
from .types import AtomicTx


class UnsignedTransaction(DataStructure):
    """
    Undocumented UnsignedTransaction ported from Avalanche.js
    """
    TYPE_MAP = {
        EVMExportTx.TYPE_ID: EVMExportTx,
        EVMImportTx.TYPE_ID: EVMImportTx,
        AVMImportTx.TYPE_ID: AVMImportTx,
        AVMExportTx.TYPE_ID: AVMExportTx,
        PlatformExportTx.TYPE_ID: PlatformExportTx,
        PlatformImportTx.TYPE_ID: PlatformImportTx,
    }

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
        type_id = raw[2:6]
        AtomicTxClass = cls.TYPE_MAP[type_id]
        atomic_tx = AtomicTxClass.from_bytes(raw[2:])
        return cls(atomic_tx)

    def get_tx_type(self):
        return self.TYPE_MAP[self.atomic_tx.TYPE_ID]

    def get_source_chain(self):
        tx_type = self.get_tx_type()
        return tx_type.SOURCE_CHAIN

    def to_dict(self) -> dict:
        return {
            'atomic_tx': self.atomic_tx.to_dict(),
        }


class SignedTransaction(DataStructure):
    """
    Contains an unsigned AtomicTX and credentials.
    """
    CODEC_ID = num_to_uint16(0)

    def __init__(self, atomic_tx: AtomicTx, credentials: list[Credential]):
        self.codec_id = self.CODEC_ID
        self.atomic_tx = atomic_tx
        self.credentials = credentials
        assert len(self.codec_id) == 2

    def _credentials_bytes(self) -> bytes:
        credential_byte_list = [credential.to_bytes() for credential in self.credentials]
        num_credentials = num_to_uint32(len(self.credentials))
        return num_credentials + b''.join(credential_byte_list)

    def to_bytes(self) -> bytes:
        return self.codec_id + self.atomic_tx.to_bytes() + self._credentials_bytes()

    def to_dict(self) -> dict:
        return {
            'atomic_tx': self.atomic_tx.to_dict(),
            'credentials': [cred.to_dict() for cred in self.credentials]
        }
