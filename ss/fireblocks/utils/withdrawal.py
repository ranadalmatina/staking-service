import logging

from django.conf import settings

from ..client import get_fireblocks_client
from ..exceptions import BroadcastFailed, IllegalWithdrawalState
from ..models import Transaction, VaultAccount, VaultWithdrawal

logger = logging.getLogger(__name__)


def _match_withdrawal(transaction: Transaction, create=False):
    """
    Look for an existing VaultWithdrawal object that matches this transaction
    (using transaction ID).
    Fall back to the older style of getting or creating a VaultWithdrawal
    using other data from the Transaction object if the initial lookup fails.
    """
    try:
        # First see if a VaultWithdrawal has this transaction ID stored against it
        return VaultWithdrawal.objects.get(transaction_id=transaction.tx_id)
    except VaultWithdrawal.DoesNotExist:
        # If nothing exists, try a more complex lookup or create a new VaultWithdrawal.
        return _get_or_create_withdrawal(transaction, create)


def _get_or_create_withdrawal(transaction: Transaction, create=False):
    """
    Find an existing VaultWithdrawal for the given transaction and link them together.
    Create a new linked VaultWithdrawal for the given transaction if an existing one
    cannot be found.

    @param: transaction - The transaction to link
    @param: create - Set this to True to create a new VaultWithdrawal if an existing
                    match cannot be found
    """
    # Try to find the ExternalWallet, VaultAsset and Trader for this transaction
    external_wallet = transaction.get_external_wallet()
    vault_asset = transaction.get_vault_asset()

    if external_wallet and vault_asset:
        # Get the ExternalWalletAsset that contains the address of the Withdrawal
        external_wallet_asset = external_wallet.get_external_wallet_asset(asset=vault_asset)

        if external_wallet_asset:

            # Try to find matching SENT withdrawal, taking the most recently created withdrawal if more than one exists
            try:
                withdrawal = VaultWithdrawal.objects.filter(
                    created_date__lte=transaction.created_at,
                    wallet_asset=external_wallet_asset,
                    amount=transaction.amount,
                    status=VaultWithdrawal.STATUS.SENT,
                    transaction__isnull=True,
                ).latest()
            except VaultWithdrawal.DoesNotExist:
                if create:
                    # Create a SENT withdrawal to match this transaction
                    withdrawal = VaultWithdrawal.objects.create(
                        # When creating missing withdrawals we set the created date manually.
                        created_date=transaction.created_at,
                        wallet_asset=external_wallet_asset,
                        amount=transaction.amount,
                        status=VaultWithdrawal.STATUS.SENT)
                else:
                    return None

            return withdrawal
    return None


def get_or_create_withdrawal(transaction: Transaction, create=False):
    """
    Find an existing VaultWithdrawal for the given transaction and link them together.
    Create a new linked VaultWithdrawal for the given transaction if an existing one
    cannot be found.

    @param: transaction - The transaction to link
    @param: create - Set this to True to create a new VaultWithdrawal if an existing
                    match cannot be found
    """
    # Transaction can only be linked to either a withdrawal or a deposit not both
    assert transaction.deposit is None

    # Check to ensure we don't already have a linked withdrawal
    if transaction.withdrawal is not None:
        return transaction.withdrawal

    withdrawal = _match_withdrawal(transaction, create)
    if withdrawal is not None:
        # Link the withdrawal to the transaction
        transaction.withdrawal = withdrawal
        transaction.save()

    return withdrawal


def update_withdrawal_status(transaction: Transaction):
    transaction.refresh_from_db()
    if transaction.withdrawal is None:
        logger.warning(f'Unable to update withdrawal status because Transaction {transaction} does not have a linked '
                       f'withdrawal')
        return

    withdrawal = transaction.withdrawal
    if transaction.status == 'COMPLETED':
        withdrawal.confirm()
        withdrawal.save()
    elif transaction.status == 'FAILED':
        withdrawal.fail()
        withdrawal.save()


def broadcast_withdrawal(withdrawal: VaultWithdrawal):
    """
    Given a Withdrawal object, execute the given Withdrawal transaction against Fireblocks.
    """
    # We only send withdrawals with status SENT to Fireblocks
    if withdrawal.status != VaultWithdrawal.STATUS.QUEUED:
        raise IllegalWithdrawalState(f'Unable to process VaultWithdrawal with status: {withdrawal.status}')

    vault_account = VaultAccount.objects.get(vault_id=settings.FIREBLOCKS_DEFAULT_VAULT_ID)
    vault_asset = withdrawal.asset
    external_wallet = withdrawal.wallet_asset.wallet

    # Call fireblocks and create new withdrawal transaction
    fb = get_fireblocks_client()
    response = fb.external_wallet_withdrawal(vault_account_id=vault_account.vault_id, asset_id=vault_asset.asset_id,
                                             external_wallet_id=external_wallet.id, amount=withdrawal.amount)
    msg = f'Withdrawal transaction response: {response}'

    if 'id' in response:
        logger.info(msg)
        withdrawal.transaction_id = response['id']
        # Status only updates to SENT after we confirm the transaction broadcast
        withdrawal.send()
        withdrawal.save()
    else:
        logger.error(msg)
        raise BroadcastFailed(msg)

    return response
