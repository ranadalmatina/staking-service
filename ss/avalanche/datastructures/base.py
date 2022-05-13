"""
Data structures required when creating transactions on Avalanche. Designed from
the specifications located at
https://docs.avax.network/specs/coreth-atomic-transaction-serialization
"""

from abc import ABC, abstractmethod
from hexbytes import HexBytes


class DataStructure(ABC):
    """
    Abstract parent class for all Avalanche data structures.
    """

    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Returns a byte representation of the data structure.
        :return:
        """
        raise NotImplementedError

    def to_hex(self) -> str:
        """
        Returns a hex string representation of the data structure bytes.
        :return:
        """
        return HexBytes(self.to_bytes()).hex()
