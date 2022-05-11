import logging

from django_fsm import TransitionNotAllowed

from django.conf import settings

from ..client import get_fireblocks_client
from ..models import FireblocksWallet, Transaction, VaultAccount, VaultAsset, VaultDeposit, VaultWalletAddress, LabelledAddress

logger = logging.getLogger(__name__)


# TODO find all useages and fix
def create_new_deposit(address: LabelledAddress, asset: VaultAsset):
    """
    Given a Trader and a VaultAsset, create a new VaultDeposit object to record
    this traders request to deposit coins. If an existing VaultDeposit object
    already exists with status NEW, then reuse this VaultDeposit.
    """
    try:
        # Reuse existing VaultDeposit if VaultDeposit with status NEW already exists
        deposit = VaultDeposit.objects.get(address=address, status=VaultDeposit.STATUS.NEW)
    except VaultDeposit.DoesNotExist:
        # Create brand new deposit
        deposit = VaultDeposit.objects.create(address=address)
    except VaultDeposit.MultipleObjectsReturned as e:
        # This is an error in the database and should never occur in normal operation
        logger.exception(e)
        deposit = VaultDeposit.objects.filter(address=address, status=VaultDeposit.STATUS.NEW).first()
    return deposit


def _create_deposit_address(vault_asset: VaultAsset) -> VaultWalletAddress:
    """
    Create a new deposit address in the default vault account on Fireblocks
    given a VaultAsset and a Trader.
    The address becomes uniquely linked to the given trader by storing their
    ID on Fireblocks.
    """
    vault_account = VaultAccount.objects.get(vault_id=settings.FIREBLOCKS_DEFAULT_VAULT_ID)

    # Call fireblocks and create new address
    fb = get_fireblocks_client()
    address_data = fb.generate_new_address(
        vault_account_id=vault_account.vault_id,
        asset_id=vault_asset.asset_id)

    defaults = {
        'tag': address_data['tag'],
        'type': address_data.get('type', 'Deposit'),
    }

    # Generate a new FireblocksWallet if needed
    wallet, created = FireblocksWallet.objects.get_or_create(vault_account=vault_account, asset=vault_asset)

    # Create the VaultWalletAddress object under the above wallet
    address, created = VaultWalletAddress.objects.get_or_create(
        wallet=wallet, address=address_data['address'], defaults=defaults)
    return address


def update_deposit_status(transaction: Transaction):
    transaction.refresh_from_db()
    if transaction.deposit is None:
        logger.warning(f'Unable to update deposit status because Transaction {transaction} does not have a linked '
                       f'deposit')
        return

    deposit = transaction.deposit
    try:
        if transaction.status == 'CONFIRMING':
            deposit.receive()
        elif transaction.status == 'COMPLETED':
            deposit.confirm()
    except TransitionNotAllowed as e:
        # If we attempt to perform an illegal transition, ignore it but log a warning
        logger.warning(e)
    else:
        deposit.save()


# TODO add the from address
def _get_or_create_deposit(address: VaultWalletAddress, transaction: Transaction):
    """
    Find an existing VaultDeposit that matches the given address and transaction.
    The account and address have been previously derived from the transaction data.
    Create a new linked VaultDeposit using this data if an existing one cannot be found.
    Finally link the transaction and deposit together.
    """
    # Try to find matching deposit, taking the most recently modified/created deposit if more than one exists
    try:
        deposit = VaultDeposit.objects.filter(
            # Deposit must have been created before the Transaction was created
            created_date__lte=transaction.created_at,
            address=address,
            status=VaultDeposit.STATUS.NEW,
            transaction__isnull=True,
        ).latest()
    except VaultDeposit.DoesNotExist:
        # Create a new deposit to match this transaction
        deposit = VaultDeposit.objects.create(
            # When creating missing deposits we set the created date manually.
            created_date=transaction.created_at,
            address=address)

    # Link the deposit to the transaction
    transaction.deposit = deposit
    transaction.save()
    return deposit


def get_or_create_deposit(transaction: Transaction):
    """
    Find an existing VaultDeposit for the given transaction and link them together.
    Create a new linked VaultDeposit for the given transaction if an existing one
    cannot be found.
    """
    # Transaction can only be linked to either a withdrawal or a deposit not both
    assert transaction.withdrawal is None

    # Check to ensure we don't already have a linked deposit
    if transaction.deposit is not None:
        return transaction.deposit

    # Try to find the VaultWalletAddress and VaultAsset for this transaction
    address = transaction.get_vault_wallet_address()
    vault_asset = transaction.get_vault_asset()

    if address and vault_asset:
        if vault_asset.is_erc_20:
            # Find data for ETH deposit
            vault_account = transaction.get_vault_account()
            if vault_account:
                return _get_or_create_deposit(address, transaction)
        else:
            # Find data for BTC deposit
            return _get_or_create_deposit(address, transaction)
    return None
