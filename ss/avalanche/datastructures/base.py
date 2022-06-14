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

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Return a dictionary representation of this object where all values
        are in a human-readable form. This method is used with the __str__
        method to show nested Datastructures in an easy to understand manner.
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        return str(self.to_dict())
