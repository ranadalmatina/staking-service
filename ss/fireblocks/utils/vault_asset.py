import logging

from django.conf import settings

from ..client import get_fireblocks_client
from ..models import FireblocksWallet, VaultAccount, VaultAsset

logger = logging.getLogger(__name__)


def get_or_create_vault_asset(asset_id: str, is_erc_20: bool) -> VaultAsset:
    """
    Try to create a new VaultAsset on Fireblocks and matching Currency object.
    """
    try:
        vault_asset = VaultAsset.objects.get(asset_id=asset_id)
    except VaultAsset.DoesNotExist:
        vault_asset = _create_vault_asset_on_fireblocks(asset_id=asset_id, is_erc_20=is_erc_20)

    # Ensure that we always have a matching Currency object.
    _create_currency_object(vault_asset=vault_asset)
    return vault_asset


def _create_vault_asset_on_fireblocks(asset_id: str, is_erc_20: bool) -> VaultAsset:
    """
    Call Fireblocks and create new VaultAsset in the default VaultAccount for BlockEx.
    """
    vault_account = VaultAccount.objects.get(vault_id=settings.FIREBLOCKS_DEFAULT_VAULT_ID)

    # Call Fireblocks and create a new vault asset in the default vault account
    fb = get_fireblocks_client()

    response = fb.create_vault_asset(vault_account_id=vault_account.vault_id, asset_id=asset_id)
    logger.info(response)
    assert 'id' in response and response['id'] == settings.FIREBLOCKS_DEFAULT_VAULT_ID

    # Create objects for the new VaultAsset and FireblocksWallet
    vault_asset = VaultAsset.objects.create(asset_id=asset_id, is_erc_20=is_erc_20)
    FireblocksWallet.objects.create(vault_account=vault_account, asset=vault_asset)
    return vault_asset


def _create_currency_object(vault_asset: VaultAsset):
    """
    Create empty currency object to avoid splitting V1 and V2
    """
    currency_code = vault_asset.get_currency_code()
    defaults = {
        'dec_places': 0,
        'is_enabled': True,
    }
