def num_to_uint16(num: int) -> bytes:
    return int.to_bytes(num, 2, byteorder='big', signed=False)

def num_to_uint32(num: int) -> bytes:
    return int.to_bytes(num, 4, byteorder='big', signed=False)

def num_to_uint64(num: int) -> bytes:
    return int.to_bytes(num, 8, byteorder='big', signed=False)

def uint_to_num(uint: bytes) -> int:
    return int.from_bytes(uint, byteorder='big', signed=False)
