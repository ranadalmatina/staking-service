from decimal import Decimal


def num_to_uint16(num: int) -> bytes:
    return int.to_bytes(num, 2, byteorder='big', signed=False)

def num_to_uint32(num: int) -> bytes:
    return int.to_bytes(num, 4, byteorder='big', signed=False)

def num_to_uint64(num: int) -> bytes:
    return int.to_bytes(num, 8, byteorder='big', signed=False)

def uint_to_num(uint: bytes) -> int:
    return int.from_bytes(uint, byteorder='big', signed=False)

def from_nano_avax(amount: Decimal) -> Decimal:
    """
    Convert from nAVAX to AVAX
    :param amount: amount in nAVAX
    :return: amount in AVAX
    """
    return amount / Decimal('10')**9

def to_nano_avax(amount: Decimal) -> Decimal:
    """
    Convert from AVAX to nAVAX
    :param amount: amount in AVAX
    :return: amount in nAVAX
    """
    return amount * Decimal('10')**9
