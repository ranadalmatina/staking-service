import binascii
import random
import hashlib


def generate_random_address(currency_code: str) -> str:
    randbytes = str(random.random()).encode('utf-8')

    if 'ETH' in currency_code:
        m = hashlib.sha3_256()
        m.update(randbytes)
        hash_ = m.digest()
        return '0x' + binascii.hexlify(hash_[12:]).decode()
