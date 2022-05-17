from bip_utils import Bech32Decoder

def bech32_to_bytes(addr: str)-> bytes:
    if addr.startswith('fuji'):
        return Bech32Decoder.Decode('fuji', addr)
    assert addr.startswith('avax')
    return Bech32Decoder.Decode('avax', addr)
