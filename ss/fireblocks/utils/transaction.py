import logging

from ..models import Transaction
from .deposit import get_or_create_deposit, update_deposit_status
from .withdrawal import get_or_create_withdrawal, update_withdrawal_status

logger = logging.getLogger(__name__)


def match_transaction(transaction: Transaction):
    """
    Match the Transaction object to a VaultWithdrawal or VaultDeposit.
    Update the status of the deposit or withdrawal after matching.
    """
    if transaction.deposit is None and transaction.withdrawal is None:

        # Try to find the ExternalWallet, VaultAsset and VaultWalletAddress for this transaction
        external_wallet = transaction.get_external_wallet()
        address = transaction.get_vault_wallet_address()
        vault_asset = transaction.get_vault_asset()

        if external_wallet and vault_asset:
            # This is a withdrawal transaction. We don't create VaultWithdrawals by default
            withdrawal = get_or_create_withdrawal(transaction=transaction, create=False)
            if withdrawal:
                update_withdrawal_status(transaction=transaction)

        elif address and vault_asset:
            # This is a deposit transaction
            deposit = get_or_create_deposit(transaction=transaction)
            if deposit:
                update_deposit_status(transaction=transaction)


def update_status(transaction: Transaction):
    """
    Update the status of the linked VaultDeposit or VaultWithdrawal.
    """
    if transaction.deposit:
        update_deposit_status(transaction=transaction)
    elif transaction.withdrawal:
        update_withdrawal_status(transaction=transaction)
