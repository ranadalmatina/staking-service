from avalanche.constants import PChainAlias
from ..avm import AVMImportTx, AVMExportTx
from avalanche.tools import num_to_uint32


class PlatformImportTx(AVMImportTx):
    """
    Platform Unsigned Import TX
    """
    TYPE_ID = num_to_uint32(0x00000011)
    SOURCE_CHAIN = PChainAlias



class PlatformExportTx(AVMExportTx):
    """
    Platform Unsigned Export TX
    """
    TYPE_ID = num_to_uint32(0x00000012)
    SOURCE_CHAIN = PChainAlias
