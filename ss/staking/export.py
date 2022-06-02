from django.conf import settings
from avalanche.web3 import AvaWeb3
from avalanche.transactions import create_cchain_export_to_pchain
from common.bip.bip32 import public_key_from_string, eth_address_from_public_key


class Export:

    def run_export_to_pchain(self):
        client = AvaWeb3(RPC_URL=settings.AVAX_RPC_URL)
        custody_balance = client.get_balance(settings.CUSTODY_WALLET_ADDRESS)
        if custody_balance < settings.EXPORT_THRESHOLD_AVAX:
            return

        try:
            derivation_path = "44/1/0/0/0"

            from_key = public_key_from_string(settings.FIREBLOCKS_XPUB, derivation_path)
            from_address = eth_address_from_public_key(from_key.RawCompressed().ToBytes())

            nonce = client.get_nonce(from_address)

            create_cchain_export_to_pchain(
                network_id=settings.NETWORK_ID,
                from_public_key=from_key,
                to_public_key=from_key,  # Use the same key on both sides of the chain?
                amount=custody_balance,
                nonce=nonce,
                derivation_path=derivation_path,
            )
        except Exception as e:
            print(e)
            return
