import logging

from celery import shared_task

from .models import AtomicTx
from .utils.tx_builder import send_for_signing, check_for_signature, broadcast_transaction

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
