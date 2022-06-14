import logging

from celery import shared_task

from django.db import transaction

from .models import AtomicTx, ChainSwap
from .utils.pchain_import_from_cchain import PChainImportFromPChain
from .utils.tx_builder import broadcast_transaction, check_for_signature, send_for_signing

logger = logging.getLogger(__name__)


@shared_task
def process_atomic_transaction():
    """
    Check all transactions in the NEW state. Send these transactions to Fireblocks for signing
    Check all transactions in the AWAITING_SIGNATURE state. Once signatures are ready will be turned into signed
    transactions, ready for transmission.
    Check all transactions in the SIGNED state. Broadcast these transactions to the avalanche network.
    """
    logger.info('Processing atomic transactions')
    for tx in AtomicTx.objects.filter(status=AtomicTx.STATUS.NEW):
        logger.info(f'Sending transaction {tx} with status: {tx.status} for signing')
        send_for_signing(tx)
    for tx in AtomicTx.objects.filter(status=AtomicTx.STATUS.AWAITING_SIGNATURE):
        logger.info(f'Checking transaction {tx} with status: {tx.status} for signature')
        check_for_signature(tx)
    for tx in AtomicTx.objects.filter(status=AtomicTx.STATUS.SIGNED):
        logger.info(f'Broadcasting transaction {tx} with status: {tx.status}')
        broadcast_transaction(tx)


@shared_task
def process_chain_swap():
    """
    Process a complete chain swap including both atomic transactions that
    constitute the entire swap.
    """
    logger.info('Processing Chain swap')
    for swap in ChainSwap.objects.filter(status=ChainSwap.STATUS.NEW):
        swap.exporting()
        swap.save()
        process_atomic_transaction()
    for swap in ChainSwap.objects.filter(status=ChainSwap.STATUS.EXPORTING):
        if swap.export_complete():
            swap.exported()
            swap.save()
        else:
            process_atomic_transaction()
    for swap in ChainSwap.objects.filter(status=ChainSwap.STATUS.EXPORTED):
        # Create import
        with transaction.atomic():
            import_ = PChainImportFromPChain(network_id=5)
            import_tx = import_.build_transaction()
            swap.import_tx = import_tx
            swap.save()

        swap.importing()
        swap.save()
        process_atomic_transaction()
    for swap in ChainSwap.objects.filter(status=ChainSwap.STATUS.IMPORTING):
        if swap.import_complete():
            assert swap.export_complete()
            swap.complete()
            swap.save()
        else:
            process_atomic_transaction()

    # TODO filter for ChainSwap that are incomplete and check for failed AtomicTxs
    # Then fail the ChainSwap object too
