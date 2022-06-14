from bip_utils.bip.bip32.bip32_base import Bip32PublicKey
from hexbytes import HexBytes
from web3 import Web3
from web3.types import Wei

from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.bech32 import bech32_address_from_public_key, bech32_to_bytes
from avalanche.constants import DEFAULTS
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.evm import EVMExportTx, EVMInput, SECPTransferOutput, TransferableOutput
from avalanche.models import AtomicTx
from avalanche.tools import num_to_uint32, num_to_uint64
from common.bip.bip32 import eth_address_from_public_key
from common.bip.bip44_coins import Bip44Coins


def create_cchain_export_to_pchain(
        network_id: int,
        nonce,
        from_public_key: Bip32PublicKey,
        to_public_key: Bip32PublicKey,
        derivation_path: str,
        amount: Wei):

    from_address = eth_address_from_public_key(from_public_key.RawCompressed().ToBytes())
    to_address = bech32_address_from_public_key(to_public_key.RawCompressed().ToBytes(), Bip44Coins.FB_P_CHAIN)
    pchain_address = pchain_address_from_address(to_address)

    export_tx = build_export_tx(
        network_id=network_id,
        from_address=from_address,
        to_address_pchain=pchain_address,
        amount=amount,
        nonce=nonce,
    )

    unsigned_tx = UnsignedTransaction(export_tx)
    export_tx_model = AtomicTx(from_derivation_path=derivation_path,
                               from_address=from_address,
                               to_derivation_path=derivation_path,
                               to_address=to_address,
                               # TODO: Storing the value in wei fails - is this correct?
                               amount=Web3.fromWei(amount, 'ether'),
                               description="Export AVAX from C-Chain to P-Chain",
                               unsigned_transaction=Base58Encoder.CheckEncode(unsigned_tx.to_bytes()))
    export_tx_model.save()


def build_export_tx(network_id: int, from_address: str, to_address_pchain: str, amount: Wei, nonce: int) -> EVMExportTx:
    import_fee = 1000000
    export_fee = 350937
    locktime = num_to_uint64(0)
    threshold = num_to_uint32(1)

    p_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['P']['blockchainID']
    p_chain_blockchain_id_buf = Base58Decoder.CheckDecode(p_chain_blockchain_id_str)

    c_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['C']['blockchainID']
    c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

    avax_asset_id: str = DEFAULTS['networks'][network_id]['X']['avaxAssetID']
    avax_asset_id_buf = Base58Decoder.CheckDecode(avax_asset_id)

    c_address = HexBytes(from_address)

    amount = amount + import_fee

    in1 = EVMInput(c_address, num_to_uint64(amount + export_fee), avax_asset_id_buf, num_to_uint64(nonce))

    sec_out = SECPTransferOutput(num_to_uint64(amount), locktime, threshold, [to_address_pchain])

    xfer_out = TransferableOutput(avax_asset_id_buf, sec_out)

    export_tx = EVMExportTx(
        num_to_uint32(network_id),
        c_chain_blockchain_id_buf,
        p_chain_blockchain_id_buf,
        [in1],
        [xfer_out]
    )

    return export_tx


def pchain_address_from_address(address: str):
    _chain, _bech32 = address.split('-')
    p_address = bech32_to_bytes(_bech32)
    return p_address
