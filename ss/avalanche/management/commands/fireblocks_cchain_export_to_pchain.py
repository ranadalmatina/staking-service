from hexbytes import HexBytes
from decimal import Decimal
from django.core.management.base import BaseCommand
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.tools import num_to_uint32, num_to_uint64
from avalanche.constants import DEFAULTS
from avalanche.datastructures.evm import EVMInput, SECPTransferOutput, TransferableOutput, EVMExportTx
from avalanche.datastructures import UnsignedTransaction
from avalanche.web3 import AvaWeb3
from avalanche.models import AtomicTx
from avalanche.bech32 import bech32_to_bytes, bech32_address_from_public_key
from common.bip.bip44_coins import Bip44Coins
from common.bip.bip32 import fireblocks_public_key, eth_address_from_public_key


class Command(BaseCommand):
    help = "Create an export transaction from C-Chain to P-Chain using Fireblocks."

    def handle(self, *args, **options):
        self.build_transaction()

    def get_nonce(self, address):
        web3 = AvaWeb3()
        print(web3.get_balance_ether(address))
        return web3.get_nonce(address)

    def get_to_address(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        _chain, _bech32 = address.split('-')
        p_address = bech32_to_bytes(_bech32)
        print(HexBytes(p_address).hex())
        return p_address

    def build_transaction(self):
        pub_key = fireblocks_public_key("44/1/0/0/0")
        from_address = eth_address_from_public_key(pub_key.ToBytes())
        to_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        export_tx = self.build_export_tx(from_address)
        unsigned_tx = UnsignedTransaction(export_tx)
        export_tx = AtomicTx(from_derivation_path="44/1/0/0/0",
                             from_address=from_address,
                             to_derivation_path="44/1/0/0/0",
                             to_address=to_address,
                             amount=Decimal("1000000000"),
                             description="Export AVAX from C-Chain to P-Chain",
                             unsigned_transaction=Base58Encoder.CheckEncode(unsigned_tx.to_bytes()))
        export_tx.save()
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(unsigned_tx.hash().hex())

    def build_export_tx(self, from_address: str):
        network_id = 5
        p_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['P']['blockchainID']
        assert p_chain_blockchain_id_str == "11111111111111111111111111111111LpoYY"
        p_chain_blockchain_id_buf = Base58Decoder.CheckDecode(p_chain_blockchain_id_str)

        c_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['C']['blockchainID']
        assert c_chain_blockchain_id_str == 'yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp'
        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

        avax_asset_id: str = DEFAULTS['networks'][network_id]['X']['avaxAssetID']
        assert avax_asset_id == 'U8iRqJoiJm8xZHAacmvYyZVwqQx6uDNtQeP3CQ6fcgQk3JqnK'
        avax_asset_id_buf = Base58Decoder.CheckDecode(avax_asset_id)

        p_address = self.get_to_address()
        c_address = HexBytes(from_address)

        amount = 1000000000
        import_fee = 1000000
        amount = amount + import_fee
        export_fee = 350937
        nonce = self.get_nonce(from_address)

        locktime = num_to_uint64(0)
        threshold = num_to_uint32(1)
        network_id = num_to_uint32(5)

        print('-----------Inputs / Outputs ---------')
        in1 = EVMInput(c_address, num_to_uint64(amount + export_fee), avax_asset_id_buf, num_to_uint64(nonce))
        print(in1.to_hex())
        sec_out = SECPTransferOutput(num_to_uint64(amount), locktime, threshold, [p_address])
        print(sec_out.to_hex())
        xfer_out = TransferableOutput(avax_asset_id_buf, sec_out)
        print(xfer_out.to_hex())
        export_tx = EVMExportTx(network_id, c_chain_blockchain_id_buf, p_chain_blockchain_id_buf, [in1], [xfer_out])
        print('--------------------------')
        print(export_tx.to_hex())
        return export_tx
