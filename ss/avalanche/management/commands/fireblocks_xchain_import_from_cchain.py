from hexbytes import HexBytes
from django.core.management.base import BaseCommand
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.tools import num_to_uint32, num_to_uint64
from avalanche.constants import DEFAULTS
from avalanche.datastructures.evm import SECPTransferOutput, TransferableOutput, SECPTransferInput, TransferableInput
from avalanche.datastructures.avm import BaseTx, AVMImportTx
from avalanche.datastructures.evm import UTXO
from avalanche.datastructures import UnsignedTransaction, SECP256K1Credential, SignedTransaction
from avalanche.api import avm_get_utxos, avm_issue_tx
from avalanche.bech32 import bech32_to_bytes, bech32_address_from_public_key
from common.bip.bip44_coins import Bip44Coins
from common.bip.bip32 import fireblocks_public_key
from fireblocks.client import get_fireblocks_client
from fireblocks.utils.raw_signing import recoverable_signature, verify_message_hash


class Command(BaseCommand):
    help = 'Create X-Chain import from C-Chain transaction for Fireblocks.'

    def __init__(self):
        super().__init__()
        self.network_id = 5

    def handle(self, *args, **options):
        # self.build_import_tx()
        self.send_to_network()

    def get_utxos(self):
        address = self._get_x_chain_bech32()
        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        response = avm_get_utxos(addresses=[address], source_chain=c_chain_blockchain_id_str)
        print(response.json())
        return response.json()

    def create_ins_and_outs(self):
        outputs: list[TransferableOutput] = []
        inputs: list[TransferableInput] = []

        # For each UTXO we create this set of ins and outs
        response = self.get_utxos()
        utxos: list[str] = response['result']['utxos']
        for utxo in utxos:
            utxo_bytes = Base58Decoder.CheckDecode(utxo)
            print(HexBytes(utxo_bytes).hex())
            utxo = UTXO.from_bytes(utxo_bytes)
            print(utxo)

            amount = utxo.output.amount
            asset_id = utxo.asset_id
            locktime = num_to_uint64(0)
            threshold = num_to_uint32(1)
            x_address = self._get_x_chain_address()

            print('-----------Outputs ---------')
            # TODO were missing a fee here for amount
            sec_out = SECPTransferOutput(amount, locktime, threshold, [x_address])
            print(sec_out.to_hex())
            xfer_out = TransferableOutput(asset_id, sec_out)
            outputs.append(xfer_out)
            print(xfer_out.to_hex())
            print('-----------Inputs ---------')
            index = num_to_uint32(0)
            sec_in = SECPTransferInput(amount=amount, address_indices=[index])
            print(sec_in.to_hex())
            xfer_in = TransferableInput(tx_id=utxo.tx_id, utxo_index=utxo.output_index, asset_id=asset_id,
                                        input=sec_in)
            print(xfer_in.to_hex())
            inputs.append(xfer_in)
        return outputs, inputs

    def _get_x_chain_address(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_X_CHAIN)
        _chain, _bech32 = address.split('-')
        x_address = bech32_to_bytes(_bech32)
        print(HexBytes(x_address).hex())
        return x_address

    def _get_x_chain_bech32(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_X_CHAIN)
        return address

    def build_import_tx(self):
        x_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['X']['blockchainID']
        assert x_chain_blockchain_id_str == '2JVSBoinj9C2J33VntvzYtVJNZdN2NKiwwKjcumHUWEb5DbBrm'
        x_chain_blockchain_id_buf = Base58Decoder.CheckDecode(x_chain_blockchain_id_str)

        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        assert c_chain_blockchain_id_str == 'yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp'
        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

        network_id = num_to_uint32(5)
        outputs, inputs = self.create_ins_and_outs()
        memo = "FB X-Chain import from C-Chain".encode('utf-8')

        base_tx = BaseTx(network_id=network_id, blockchain_id=x_chain_blockchain_id_buf, outputs=outputs,
                         inputs=[], memo=memo)
        import_tx = AVMImportTx(base_tx=base_tx, source_chain=c_chain_blockchain_id_buf, ins=inputs)


        print('--------------------------')
        print(import_tx.to_hex())
        unsigned_tx = UnsignedTransaction(import_tx)
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(HexBytes(unsigned_tx.hash()).hex())
        return import_tx

    def get_signature(self):
        pub_key = HexBytes("028d6742ba744686f0cea20e69154eed3f0bc654485ebebae5c76b9f49ff3ccb01")
        msg_hash = HexBytes("8eeda5cf6b6c6ac18b5760663eacf51c5acb8c0a8bbc5c3f4f0e9c47d1c61337")
        client = get_fireblocks_client()
        response = client.get_transaction_by_id(txid='cfd8959c-7811-4f98-ab3e-cbf594ffbcca')
        sig = recoverable_signature(response['signedMessages'])
        verify_message_hash(pub=pub_key, msg_hash=msg_hash, sig=sig)
        return sig

    def send_to_network(self):
        import_tx = self.build_import_tx()
        print('-----------Signed---------')
        sig = self.get_signature().to_bytes()
        cred = SECP256K1Credential([sig])
        signed_tx = SignedTransaction(import_tx, [cred])
        print(signed_tx.to_hex())
        b58_signed_tx = Base58Encoder.CheckEncode(signed_tx.to_bytes())
        print(b58_signed_tx)
        print('-----------Transmission to Network-----------')
        response = avm_issue_tx(tx=b58_signed_tx)
        if response.status_code == 200:
            print(response.json())

