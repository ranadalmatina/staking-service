from decimal import Decimal
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware
from django.core.management.base import BaseCommand
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.tools import num_to_uint32, num_to_uint64
from avalanche.constants import DEFAULTS
from avalanche.datastructures.evm import (EVMInput, SECPTransferOutput, TransferableOutput, EVMExportTx,
    UnsignedTransaction, SECP256K1Credential, SignedTransaction)


class Command(BaseCommand):
    help = 'Test data structures and transaction building.'

    def handle(self, *args, **options):
        self.build_transaction()

    def setup_web3(self):
        RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"
        web3 = Web3(Web3.HTTPProvider(RPC_URL))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        from_address = web3.toChecksumAddress("0x37925525b620412183D4d8F71e6f64b5e64420C4")
        amount = web3.fromWei(web3.eth.get_balance(from_address), 'ether')
        assert amount == Decimal('28.9994225')
        return web3

    def get_nonce(self):
        web3 = self.setup_web3()
        from_address_hex = web3.toChecksumAddress("0xb50a61ca779487fc19acca5c7e5d61b547ab710a")
        nonce = web3.eth.getTransactionCount(from_address_hex)
        return nonce

    def build_transaction(self):
        network_id = 5
        x_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['X']['blockchainID']
        assert x_chain_blockchain_id_str == '2JVSBoinj9C2J33VntvzYtVJNZdN2NKiwwKjcumHUWEb5DbBrm'

        x_chain_blockchain_id_buf = Base58Decoder.CheckDecode(x_chain_blockchain_id_str)
        print(x_chain_blockchain_id_buf)
        c_chain_blockchain_id_str: str = DEFAULTS['networks'][network_id]['C']['blockchainID']
        assert c_chain_blockchain_id_str == 'yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp'

        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)
        print(c_chain_blockchain_id_buf)
        avax_asset_id: str = DEFAULTS['networks'][network_id]['X']['avaxAssetID']
        assert avax_asset_id == 'U8iRqJoiJm8xZHAacmvYyZVwqQx6uDNtQeP3CQ6fcgQk3JqnK'
        avax_asset_id_buf = Base58Decoder.CheckDecode(avax_asset_id)

        # print(HexBytes(avax_asset_id_buf).hex())
        # print(len(avax_asset_id_buf))
        # print(avax_asset_id_buf)
        # print(Base58Decoder.CheckDecode(avax_asset_id))
        # print(HexBytes(Base58Decoder.CheckDecode(avax_asset_id)).hex())

        c_address = HexBytes('0xb50a61Ca779487fC19aCcA5c7e5d61B547AB710a')
        x_address = HexBytes('31f21e090ec0bcbca55f69befc579552eaab9aea')
        amount = 100000000
        import_fee = 1000000
        amount = amount + import_fee
        export_fee = 350937
        nonce = self.get_nonce()

        locktime = num_to_uint64(0)
        threshold = num_to_uint32(1)
        network_id = num_to_uint32(5)

        in1 = EVMInput(c_address, num_to_uint64(amount + export_fee), avax_asset_id_buf, num_to_uint64(nonce))
        print(in1.to_hex())
        sec_out = SECPTransferOutput(num_to_uint64(amount), locktime, threshold, [x_address])
        print(sec_out.to_hex())
        xfer_out = TransferableOutput(avax_asset_id_buf, sec_out)
        print(xfer_out.to_hex())
        export_tx = EVMExportTx(network_id, c_chain_blockchain_id_buf, x_chain_blockchain_id_buf, [in1], [xfer_out])
        print('--------------------------')
        print(export_tx.to_hex())
        unsigned_tx = UnsignedTransaction(export_tx)
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print(HexBytes(unsigned_tx.hash()).hex())

        print('-----------Signed---------')
        sig = HexBytes('0xfadc2af5271dbcf7f13af906cb9e14fcc6be42ced68076b68013f491f16897818cbecce262e7ada285c55fdb01ac5d2c7451b8821803456b1be92c78bd17d4cd00')
        cred = SECP256K1Credential([sig])
        signed_tx = SignedTransaction(export_tx, [cred])
        print(signed_tx.to_hex())
        b58_signed_tx = Base58Encoder.CheckEncode(signed_tx.to_bytes())
        print(b58_signed_tx)
