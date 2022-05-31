from decimal import Decimal
from hexbytes import HexBytes
from django.core.management.base import BaseCommand
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.tools import num_to_uint32, num_to_uint64, uint_to_num
from avalanche.constants import DEFAULTS
from avalanche.datastructures.evm import SECPTransferOutput, TransferableOutput, SECPTransferInput, TransferableInput
from avalanche.datastructures.avm import BaseTx
from avalanche.datastructures.platform import PlatformImportTx
from avalanche.datastructures.evm import UTXO
from avalanche.datastructures import UnsignedTransaction
from avalanche.api import AvalancheClient
from avalanche.models import AtomicTx
from avalanche.bech32 import bech32_to_bytes, bech32_address_from_public_key
from common.bip.bip44_coins import Bip44Coins
from common.bip.bip32 import fireblocks_public_key, eth_address_from_public_key


class Command(BaseCommand):
    help = 'Create P-Chain import from C-Chain transaction for Fireblocks.'

    def __init__(self):
        super().__init__()
        self.network_id = 5

    def handle(self, *args, **options):
        pub_key = fireblocks_public_key("44/1/0/0/0")
        from_address = eth_address_from_public_key(pub_key.ToBytes())
        to_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        import_tx = self.build_import_tx()
        unsigned_tx = UnsignedTransaction(import_tx)
        import_tx = AtomicTx(from_derivation_path="44/1/0/0/0",
                             from_address=from_address,
                             to_derivation_path="44/1/0/0/0",
                             to_address=to_address,
                             amount=Decimal("1000000000"),
                             description="FB P-Chain import from C-Chain",
                             unsigned_transaction=Base58Encoder.CheckEncode(unsigned_tx.to_bytes()))
        import_tx.save()

    def get_utxos(self):
        address = self._get_p_chain_bech32()
        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        client = AvalancheClient()
        response = client.platform_get_utxos(addresses=[address], source_chain=c_chain_blockchain_id_str)
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
            fee = 1000000
            amt = uint_to_num(amount) - fee
            asset_id = utxo.asset_id
            locktime = num_to_uint64(0)
            threshold = num_to_uint32(1)
            p_address = self._get_p_chain_address()

            print('-----------Outputs ---------')
            sec_out = SECPTransferOutput(num_to_uint64(amt), locktime, threshold, [p_address])
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

    def _get_p_chain_address(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        _chain, _bech32 = address.split('-')
        p_address = bech32_to_bytes(_bech32)
        print(HexBytes(p_address).hex())
        return p_address

    def _get_p_chain_bech32(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        return address

    def build_import_tx(self):
        p_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['P']['blockchainID']
        assert p_chain_blockchain_id_str == "11111111111111111111111111111111LpoYY"
        p_chain_blockchain_id_buf = Base58Decoder.CheckDecode(p_chain_blockchain_id_str)

        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        assert c_chain_blockchain_id_str == 'yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp'
        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

        network_id = num_to_uint32(5)
        outputs, inputs = self.create_ins_and_outs()
        memo = "FB P-Chain import from C-Chain".encode('utf-8')

        base_tx = BaseTx(network_id=network_id, blockchain_id=p_chain_blockchain_id_buf, outputs=outputs,
                         inputs=[], memo=memo)
        import_tx = PlatformImportTx(base_tx=base_tx, source_chain=c_chain_blockchain_id_buf, ins=inputs)


        print('--------------------------')
        print(import_tx.to_hex())
        unsigned_tx = UnsignedTransaction(import_tx)
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(unsigned_tx.hash().hex())
        return import_tx
