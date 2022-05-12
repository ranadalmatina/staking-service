# Imports
from typing import Any, Union
from bip_utils.addr.addr_dec_utils import AddrDecUtils
from bip_utils.addr.atom_addr import AtomAddrDecoder, AtomAddrEncoder
from bip_utils.addr.iaddr_decoder import IAddrDecoder
from bip_utils.addr.iaddr_encoder import IAddrEncoder
from bip_utils.ecc import IPublicKey
from .coin_conf import CoinsConf


class _AvaxAddrUtils:
    """Avax address utility class."""

    @staticmethod
    def DecodeAddr(addr: str,
                   prefix: str,
                   hrp: str) -> bytes:
        """
        Decode an Avax address to bytes.
        Args:
            addr (str)  : Address string
            prefix (str): Address prefix
            hrp (str)   : Address HRP
        Returns:
            bytes: Public key hash bytes
        Raises:
            ValueError: If the address encoding is not valid
        """
        addr_no_prefix = AddrDecUtils.ValidateAndRemovePrefix(addr, prefix)
        return AtomAddrDecoder.DecodeAddr(addr_no_prefix, hrp=hrp)


class FujiPChainAddrDecoder(IAddrDecoder):
    """
    Avax P-Chain address decoder class.
    It allows the Avax P-Chain address decoding.
    """

    @staticmethod
    def DecodeAddr(addr: str,
                   **kwargs: Any) -> bytes:
        """
        Decode an Avax P-Chain address to bytes.
        Args:
            addr (str): Address string
            **kwargs  : Not used
        Returns:
            bytes: Public key hash bytes
        Raises:
            ValueError: If the address encoding is not valid
        """
        return _AvaxAddrUtils.DecodeAddr(addr,
                                         CoinsConf.FujiPChain.Params("addr_prefix"),
                                         CoinsConf.FujiPChain.Params("addr_hrp"))


class FujiPChainAddrEncoder(IAddrEncoder):
    """
    Avax P-Chain address encoder class.
    It allows the Avax P-Chain address encoding.
    """

    @staticmethod
    def EncodeKey(pub_key: Union[bytes, IPublicKey],
                  **kwargs: Any) -> str:
        """
        Encode a public key to Avax P-Chain address.
        Args:
            pub_key (bytes or IPublicKey): Public key bytes or object
            **kwargs                     : Not used
        Returns:
            str: Address string
        Raises:
            ValueError: If the public key is not valid
            TypeError: If the public key is not secp256k1
        """
        prefix = CoinsConf.FujiPChain.Params("addr_prefix")
        return prefix + AtomAddrEncoder.EncodeKey(pub_key,
                                                  hrp=CoinsConf.FujiPChain.Params("addr_hrp"))


class FujiXChainAddrDecoder(IAddrDecoder):
    """
    Avax X-Chain address decoder class.
    It allows the Avax X-Chain address decoding.
    """

    @staticmethod
    def DecodeAddr(addr: str,
                   **kwargs: Any) -> bytes:
        """
        Decode an Avax X-Chain address to bytes.
        Args:
            addr (str): Address string
            **kwargs  : Not used
        Returns:
            bytes: Public key hash bytes
        Raises:
            ValueError: If the address encoding is not valid
        """
        return _AvaxAddrUtils.DecodeAddr(addr,
                                         CoinsConf.FujiXChain.Params("addr_prefix"),
                                         CoinsConf.FujiXChain.Params("addr_hrp"))


class FujiXChainAddrEncoder(IAddrEncoder):
    """
    Avax Testnet X-Chain address encoder class.
    It allows the Avax X-Chain address encoding.
    """

    @staticmethod
    def EncodeKey(pub_key: Union[bytes, IPublicKey],
                  **kwargs: Any) -> str:
        """
        Encode a public key to Avax X-Chain address.
        Args:
            pub_key (bytes or IPublicKey): Public key bytes or object
            **kwargs                     : Not used
        Returns:
            str: Address string
        Raises:
            ValueError: If the public key is not valid
            TypeError: If the public key is not secp256k1
        """
        prefix = CoinsConf.FujiXChain.Params("addr_prefix")
        return prefix + AtomAddrEncoder.EncodeKey(pub_key,
                                                  hrp=CoinsConf.FujiXChain.Params("addr_hrp"))


class FujiCChainAddrEncoder(IAddrEncoder):
    """
    Avax Testnet C-Chain address encoder class.
    It allows the Avax Testnet Bech32 C-Chain address encoding.
    """

    @staticmethod
    def EncodeKey(pub_key: Union[bytes, IPublicKey],
                  **kwargs: Any) -> str:
        """
        Encode a public key to Avax C-Chain address.
        Args:
            pub_key (bytes or IPublicKey): Public key bytes or object
            **kwargs                     : Not used
        Returns:
            str: Address string
        Raises:
            ValueError: If the public key is not valid
            TypeError: If the public key is not secp256k1
        """
        prefix = 'C-'
        return prefix + AtomAddrEncoder.EncodeKey(pub_key,
                                                  hrp=CoinsConf.FujiXChain.Params("addr_hrp"))
