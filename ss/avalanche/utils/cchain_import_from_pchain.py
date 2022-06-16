from decimal import Decimal

from hexbytes import HexBytes

from django.conf import settings

from avalanche.api import AvalancheClient
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.bech32 import bech32_address_from_public_key, bech32_to_bytes
from avalanche.constants import DEFAULTS
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.evm import UTXO, EVMImportTx, EVMOutput, SECPTransferInput, TransferableInput
from avalanche.models import AtomicTx
from avalanche.tools import num_to_uint32, num_to_uint64, uint_to_num
from common.bip.bip32 import eth_address_from_public_key, fireblocks_public_key
from common.bip.bip44_coins import Bip44Coins


class CChainImportFromPChain:
    """
    Create a C-Chain import transaction from P-Chain using Fireblocks.
    """

    def __init__(self, network_id):
        self.network_id = network_id

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
        from_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        to_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_C_CHAIN)
        import_tx = self.build_import_tx(to_address)
        unsigned_tx = UnsignedTransaction(import_tx)
        import_tx = AtomicTx(from_derivation_path="44/1/0/0/0",
                             from_address=from_address,
                             to_derivation_path="44/1/0/0/0",
                             to_address=to_address,
                             amount=Decimal("1000000000"),
                             description="Import AVAX from P-Chain to C-Chain",
                             unsigned_transaction=Base58Encoder.CheckEncode(unsigned_tx.to_bytes()))
        import_tx.save()
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(unsigned_tx.hash().hex())
        return import_tx

    def get_utxos(self, destination_address):
        client = AvalancheClient(RPC_URL=settings.AVAX_RPC_URL)
        response = client.evm_get_utxos(addresses=[destination_address], source_chain='P')
        print(response.json())
        return response.json()

    def _get_c_chain_address(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        c_hex_address = eth_address_from_public_key(pub_key.ToBytes())
        addr_bytes = HexBytes(c_hex_address)
        print(addr_bytes.hex())
        return addr_bytes

    def create_ins_and_outs(self, destination_address):
        inputs: list[TransferableInput] = []
        outputs: list[EVMOutput] = []

        # For each UTXO we create this set of ins and outs
        response = self.get_utxos(destination_address=destination_address)
        utxos: list[str] = response['result']['utxos']
        for utxo in utxos:
            utxo_bytes = Base58Decoder.CheckDecode(utxo)
            print(HexBytes(utxo_bytes).hex())
            utxo = UTXO.from_bytes(utxo_bytes)
            print(utxo)

            amount = utxo.output.amount
            asset_id = utxo.asset_id

            print('-----------Inputs ---------')
            index = num_to_uint32(0)
            sec_in = SECPTransferInput(amount=amount, address_indices=[index])
            print(sec_in.to_hex())
            xfer_in = TransferableInput(tx_id=utxo.tx_id, utxo_index=utxo.output_index, asset_id=asset_id,
                                        input=sec_in)
            print(xfer_in.to_hex())
            inputs.append(xfer_in)

            print('-----------Outputs ---------')
            c_hex_address = self._get_c_chain_address()
            import_fee = 350937
            amount_less_fee = num_to_uint64(uint_to_num(amount) - import_fee)

            evm_output = EVMOutput(address=c_hex_address, amount=amount_less_fee, asset_id=asset_id)
            outputs.append(evm_output)

        return outputs, inputs

    def build_import_tx(self, to_address: str):
        p_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['P']['blockchainID']
        p_chain_blockchain_id_buf = Base58Decoder.CheckDecode(p_chain_blockchain_id_str)

        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

        network_id = num_to_uint32(5)

        print('-----------Inputs / Outputs ---------')
        outputs, inputs = self.create_ins_and_outs(destination_address=to_address)
        print('---------ImportTX---------')
        import_tx = EVMImportTx(network_id, c_chain_blockchain_id_buf, p_chain_blockchain_id_buf, inputs, outputs)
        print('--------------------------')
        print(import_tx.to_hex())
        return import_tx
