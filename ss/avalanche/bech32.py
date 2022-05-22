from bip_utils import Bech32Decoder
from common.bip import Bip44ConfGetter, Bip44Coins
from bip_utils import Bip44PublicKey, Bip32Secp256k1


def bech32_to_bytes(addr: str)-> bytes:
    if addr.startswith('fuji'):
        return Bech32Decoder.Decode('fuji', addr)
    assert addr.startswith('avax')
    return Bech32Decoder.Decode('avax', addr)


def bech32_address_from_public_key(public_key: bytes, coin: Bip44Coins):
    bip32_ctx = Bip32Secp256k1.FromPublicKey(public_key)
    derived_ctx = Bip44PublicKey(bip32_ctx.PublicKey(), Bip44ConfGetter.GetConfig(coin))
    return derived_ctx.ToAddress()
