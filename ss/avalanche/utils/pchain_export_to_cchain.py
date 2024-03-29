from decimal import Decimal

from hexbytes import HexBytes

from django.conf import settings

from avalanche.api import AvalancheClient
from avalanche.base58 import Base58Decoder, Base58Encoder
from avalanche.bech32 import bech32_address_from_public_key, bech32_to_bytes
from avalanche.constants import DEFAULTS
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.avm import BaseTx
from avalanche.datastructures.evm import (UTXO, SECPTransferInput, SECPTransferOutput, TransferableInput,
                                          TransferableOutput)
from avalanche.datastructures.platform import PlatformExportTx
from avalanche.models import AtomicTx
from avalanche.tools import num_to_uint32, num_to_uint64, to_nano_avax
from common.bip.bip32 import fireblocks_public_key
from common.bip.bip44_coins import Bip44Coins


class PChainExportToCChain:
    """
    Create P-Chain export to C-Chain transaction for Fireblocks.
    """

    def __init__(self, network_id):
        self.network_id = network_id
        self.amount = None

    def build_transaction(self, amount: Decimal):
        self.amount = to_nano_avax(amount)

        pub_key = fireblocks_public_key("44/1/0/0/0")
        from_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        to_address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_C_CHAIN)
        print(to_address)
        export_tx = self.build_export_tx()
        unsigned_tx = UnsignedTransaction(export_tx)
        export_tx = AtomicTx(from_derivation_path="44/1/0/0/0",
                             from_address=from_address,
                             to_derivation_path="44/1/0/0/0",
                             to_address=to_address,
                             amount=amount,
                             description="FB P-Chain export to C-Chain",
                             unsigned_transaction=Base58Encoder.CheckEncode(unsigned_tx.to_bytes()))
        export_tx.save()
        return export_tx

    def get_utxos(self):
        address = self._get_p_chain_bech32()
        client = AvalancheClient(RPC_URL=settings.AVAX_RPC_URL)
        response = client.platform_get_utxos(addresses=[address])
        print(response.json())
        return response.json()

    def _create_outputs(self):
        fee = 1000000
        total = self.amount - fee

        locktime = num_to_uint64(0)
        threshold = num_to_uint32(1)
        c_address = self._get_c_chain_address()

        avax_asset_id: str = DEFAULTS['networks'][self.network_id]['X']['avaxAssetID']
        avax_asset_id_buf = Base58Decoder.CheckDecode(avax_asset_id)

        print('-----------Outputs ---------')
        sec_out = SECPTransferOutput(num_to_uint64(total), locktime, threshold, [c_address])
        print(sec_out.to_hex())
        xfer_out = TransferableOutput(avax_asset_id_buf, sec_out)
        print(xfer_out.to_hex())
        return xfer_out

    def create_ins_and_outs(self):
        outputs: list[TransferableOutput] = []
        inputs: list[TransferableInput] = []

        xfer_out = self._create_outputs()
        outputs.append(xfer_out)

        print('-----------UTXOs + Inputs----------')

        # For each UTXO we create an input
        response = self.get_utxos()
        utxos: list[str] = response['result']['utxos']
        print(f'Num UTXOs: {len(utxos)}')
        for utxo in utxos:
            print('-----------UTXO---------')
            utxo_bytes = Base58Decoder.CheckDecode(utxo)
            print(HexBytes(utxo_bytes).hex())
            utxo = UTXO.from_bytes(utxo_bytes)
            print(utxo)

            amount = utxo.output.amount
            asset_id = utxo.asset_id

            print('-----------Input---------')
            index = num_to_uint32(0)
            sec_in = SECPTransferInput(amount=amount, address_indices=[index])
            print(sec_in.to_hex())
            xfer_in = TransferableInput(tx_id=utxo.tx_id, utxo_index=utxo.output_index, asset_id=asset_id,
                                        input=sec_in)
            print(xfer_in.to_hex())
            inputs.append(xfer_in)
            break
        return outputs, inputs

    def _get_c_chain_address(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_C_CHAIN)
        _chain, _bech32 = address.split('-')
        c_address = bech32_to_bytes(_bech32)
        print(HexBytes(c_address).hex())
        return c_address

    def _get_p_chain_bech32(self):
        # This is the only derivation path we are allowed on test workspace
        pub_key = fireblocks_public_key("44/1/0/0/0")
        address = bech32_address_from_public_key(pub_key.ToBytes(), Bip44Coins.FB_P_CHAIN)
        return address

    def build_export_tx(self):
        p_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['P']['blockchainID']
        p_chain_blockchain_id_buf = Base58Decoder.CheckDecode(p_chain_blockchain_id_str)

        c_chain_blockchain_id_str: str = DEFAULTS['networks'][self.network_id]['C']['blockchainID']
        c_chain_blockchain_id_buf = Base58Decoder.CheckDecode(c_chain_blockchain_id_str)

        network_id = num_to_uint32(5)
        outputs, inputs = self.create_ins_and_outs()
        memo = "FB P-Chain export to C-Chain".encode('utf-8')

        base_tx = BaseTx(network_id=network_id, blockchain_id=p_chain_blockchain_id_buf, outputs=[],
                         inputs=inputs, memo=memo)
        export_tx = PlatformExportTx(base_tx=base_tx, destination_chain=c_chain_blockchain_id_buf, outs=outputs)

        print('--------------------------')
        print(export_tx.to_hex())
        unsigned_tx = UnsignedTransaction(export_tx)
        print('-----------Unsigned---------')
        print(unsigned_tx.to_hex())
        print('----------HASH----------')
        print(unsigned_tx.hash().hex())
        return export_tx
