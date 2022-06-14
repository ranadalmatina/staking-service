import logging

from celery import shared_task

from .models import AtomicTx, ChainSwap
from .utils.chain_swap import create_import_tx
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
    # First check if any ChainSwap objects have failed AtomicTx children. If they do fail the entire swap
    for swap in ChainSwap.objects.filter(status__in=[ChainSwap.STATUS.EXPORTING, ChainSwap.STATUS.IMPORTING]):
        if swap.should_fail():
            swap.fail()
            swap.save()
            logger.error(f'Chainswap {swap} failed')

    # Process each status in turn
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
        create_import_fn = create_import_tx(source_chain=swap.source_chain)
        create_import_fn(swap=swap)
        # swap.refresh_from_db()
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
