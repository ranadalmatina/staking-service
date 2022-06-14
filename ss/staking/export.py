import logging
import traceback

from web3 import Web3

from django.conf import settings

from avalanche.models import AtomicTx
from avalanche.transactions import create_cchain_export_to_pchain
from avalanche.web3 import AvaWeb3
from common.bip.bip32 import eth_address_from_public_key, public_key_from_string

logger = logging.getLogger(__name__)


pending_states = [AtomicTx.STATUS.NEW, AtomicTx.STATUS.SUBMITTED,
                  AtomicTx.STATUS.AWAITING_SIGNATURE, AtomicTx.STATUS.SIGNED, AtomicTx.STATUS.BROADCAST]


class Export:

    def run_export_to_pchain(self):
        client = AvaWeb3(RPC_URL=settings.AVAX_RPC_URL)
        custody_balance = client.get_balance(settings.CUSTODY_WALLET_ADDRESS)
        threshold_wei = Web3.toWei(settings.EXPORT_THRESHOLD_AVAX, 'ether')
        if custody_balance < threshold_wei:
            logger.info(f'Custody balance {custody_balance} is below threshold of {threshold_wei}')
            return

        # If there's a pending export, don't create another one
        existing = AtomicTx.objects.filter(status__in=pending_states)
        if len(existing):
            tx = existing.first()
            logger.info(f'Found an existing pending export transaction: {tx.id} for {tx.amount} AVAX')
            return

        logger.info(f'Custody balance over threshold, exporting: {custody_balance}')
        try:
            derivation_path = "44/1/0/0/0"

            from_key = public_key_from_string(settings.FIREBLOCKS_XPUB, derivation_path)
            from_address = eth_address_from_public_key(from_key.RawCompressed().ToBytes())

            # Remove 1 AVAX so we always have enough for gas.
            amount = custody_balance - Web3.toWei(1, 'ether')
            nonce = client.get_nonce(from_address)

            create_cchain_export_to_pchain(
                network_id=settings.NETWORK_ID,
                from_public_key=from_key,
                to_public_key=from_key,  # Use the same key on both sides of the chain?
                amount=amount,
                nonce=nonce,
                derivation_path=derivation_path,
            )
        except Exception as e:
            logger.error(e)
            traceback.print_tb(e.__traceback__)
            return
