from hexbytes import HexBytes
from django.core.management.base import BaseCommand
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.tools import num_to_uint32, num_to_uint64
from avalanche.constants import DEFAULTS
from avalanche.datastructures.evm import EVMInput, SECPTransferOutput, TransferableOutput, EVMExportTx
from avalanche.datastructures import SECP256K1Credential, UnsignedTransaction, SignedTransaction
from avalanche.api import AvalancheClient
from avalanche.web3 import AvaWeb3
from avalanche.bech32 import bech32_to_bytes, bech32_address_from_public_key
from common.bip.bip44_coins import Bip44Coins
from common.bip.bip32 import fireblocks_public_key
from fireblocks.client import get_fireblocks_client
from fireblocks.utils.raw_signing import recoverable_signature, verify_message_hash


class Command(BaseCommand):
    help = "Create an export transaction from C-Chain to P-Chain using Fireblocks."

    def handle(self, *args, **options):
        # self.build_transaction()
        self.send_to_network()

    def get_nonce(self, address):
        web3 = AvaWeb3()
        print(web3.get_balance(address))
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
        export_tx = self.build_export_tx()
        unsigned_tx = UnsignedTransaction(export_tx)
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(unsigned_tx.hash().hex())


    def build_export_tx(self):
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
        c_address = HexBytes('0x37925525b620412183D4d8F71e6f64b5e64420C4')

        amount = 1000000000
        import_fee = 1000000
        amount = amount + import_fee
        export_fee = 350937
        nonce = self.get_nonce('0x37925525b620412183D4d8F71e6f64b5e64420C4')

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

    def get_signature(self):
        pub_key = HexBytes("028d6742ba744686f0cea20e69154eed3f0bc654485ebebae5c76b9f49ff3ccb01")
        msg_hash = HexBytes("edd9b102c0113997e9f00fdca4e0b1446ac98aa1ef81f06b6266b68f2c3d778e")
        client = get_fireblocks_client()
        response = client.get_transaction_by_id(txid='f51b85a4-a5e4-4fe1-aefd-1a390e339070')
        sig = recoverable_signature(response['signedMessages'])
        verify_message_hash(pub=pub_key, msg_hash=msg_hash, sig=sig)
        return sig

    def send_to_network(self):
        export_tx = self.build_export_tx()
        print('-----------Signed---------')
        sig = self.get_signature().to_bytes()
        cred = SECP256K1Credential([sig])
        signed_tx = SignedTransaction(export_tx, [cred])
        print(signed_tx.to_hex())
        b58_signed_tx = Base58Encoder.CheckEncode(signed_tx.to_bytes())
        print(b58_signed_tx)
        print('-----------Transmission to Network-----------')
        client = AvalancheClient()
        response = client.evm_issue_tx(tx=b58_signed_tx)
        if response.status_code == 200:
            print(response.json())



