from django.conf import settings
from bip_utils import EthAddrEncoder
from bip_utils.bip.bip32 import Bip32Secp256k1
from bip_utils.ecc.secp256k1_keys_coincurve import Secp256k1PublicKeyCoincurve


def fireblocks_public_key(derivation_path="44/1/0/0/0"):
    fireblocks_xpub = settings.FIREBLOCKS_XPUB
    return public_key_from_string(fireblocks_xpub, derivation_path).RawCompressed()


def public_key_from_string(public_key_str: str, derivation_path="44/1/0/0/0"):
    bip32_ctx = Bip32Secp256k1.FromExtendedKey(public_key_str)
    derrived = bip32_ctx.DerivePath(derivation_path)
    return derrived.PublicKey()


def eth_address_from_public_key(public_key: bytes):
    secp_pub = Secp256k1PublicKeyCoincurve.FromBytes(public_key)
    addr = EthAddrEncoder.EncodeKey(secp_pub)
    return addr
