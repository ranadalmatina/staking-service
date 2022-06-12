from eth_keys.datatypes import NonRecoverableSignature, PublicKey, Signature
from hexbytes import HexBytes


def recoverable_signature(signed_messages: list[dict]):
    assert len(signed_messages) == 1
    signed_message = signed_messages[0]
    assert signed_message['derivationPath'] == [44, 1, 0, 0, 0]
    assert signed_message['algorithm'] == 'MPC_ECDSA_SECP256K1'
    full_sig = HexBytes(signed_message['signature']['fullSig'])
    r = HexBytes(signed_message['signature']['r'])
    s = HexBytes(signed_message['signature']['s'])
    v = signed_message['signature']['v']
    assert isinstance(v, int)

    nrs = NonRecoverableSignature(signature_bytes=full_sig)
    print(nrs)
    sig = Signature(vrs=(v, int.from_bytes(r, byteorder='big'), int.from_bytes(s, byteorder='big')))
    return sig


def verify_message_hash(pub: bytes, msg_hash: bytes, sig: Signature):
    pub_key = PublicKey.from_compressed_bytes(pub)
    assert pub_key.verify_msg_hash(message_hash=msg_hash, signature=sig)
