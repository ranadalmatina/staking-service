def num_to_int(num: int) -> bytes:
    return int.to_bytes(num, 4, byteorder='big', signed=False)

def num_to_long(num: int) -> bytes:
    return int.to_bytes(num, 8, byteorder='big', signed=False)
