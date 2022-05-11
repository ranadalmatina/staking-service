import logging

from ..client import get_fireblocks_client
from ..exceptions import FireblocksWalletCreationException
from ..models import FireblocksWallet, VaultAccount, VaultAsset

logger = logging.getLogger(__name__)


def _create_deposit_wallet(vault_account: VaultAccount, vault_asset: VaultAsset) -> FireblocksWallet:
    """
    Call Fireblocks and create a new asset within an existing vault account.
    We represent this as a FireblocksWallet object in the database.
    """
    fb = get_fireblocks_client()
    response = fb.create_vault_asset(vault_account_id=vault_account.vault_id, asset_id=vault_asset.asset_id)
    logger.info(response)

    if response['id'] == vault_account.vault_id:
        # Wallet exists on Fireblocks so create the matching object in the db and return it
        return FireblocksWallet.objects.create(vault_account=vault_account, asset=vault_asset)
    raise FireblocksWalletCreationException('Invalid ID during wallet creation')
