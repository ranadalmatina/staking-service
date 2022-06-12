from bip_utils import Bech32Decoder, Bip32Secp256k1, Bip44PublicKey

from common.bip import Bip44Coins, Bip44ConfGetter
from common.bip.address import FujiCChainAddrEncoder


def bech32_to_bytes(addr: str)-> bytes:
    if addr.startswith('fuji'):
        return Bech32Decoder.Decode('fuji', addr)
    assert addr.startswith('avax')
    return Bech32Decoder.Decode('avax', addr)


def bech32_address_from_public_key(public_key: bytes, coin: Bip44Coins):
    if coin in (Bip44Coins.FB_C_CHAIN, Bip44Coins.AVAX_C_CHAIN, Bip44Coins.AVAX_C_CHAIN):
        # The default derivation is Ethereum style address. But we want Bech32
        bip32_ctx = Bip32Secp256k1.FromPublicKey(public_key)
        return FujiCChainAddrEncoder.EncodeKey(bip32_ctx.PublicKey().KeyObject())

    bip32_ctx = Bip32Secp256k1.FromPublicKey(public_key)
    derived_ctx = Bip44PublicKey(bip32_ctx.PublicKey(), Bip44ConfGetter.GetConfig(coin))
    return derived_ctx.ToAddress()


def address_from_public_key(public_key: bytes, coin: Bip44Coins):
    """
    Derive address given the public key and the coin type. By default Avalanche C-Chain
    addresses use the Etheruem style addressing. To get Bech32 style address, use the
    function above.
    :param public_key:
    :param coin:
    :return:
    """
    bip32_ctx = Bip32Secp256k1.FromPublicKey(public_key)
    derived_ctx = Bip44PublicKey(bip32_ctx.PublicKey(), Bip44ConfGetter.GetConfig(coin))
    return derived_ctx.ToAddress()
