import logging

from fireblocks_sdk import FireblocksApiException

from ..client import get_fireblocks_client
from ..models import FireblocksWallet, VaultWalletAddress

logger = logging.getLogger(__name__)


def get_vault_wallet_address(wallet: FireblocksWallet) -> VaultWalletAddress:
    """
    Get the VaultWalletAddress object belonging to an intermediate vault account for a specific user.
    Note: This function should not be used to get a deposit address for a non ERC-20 vault asset.
    """
    try:
        return VaultWalletAddress.objects.get(wallet=wallet)
    except VaultWalletAddress.DoesNotExist:
        return _fetch_vault_wallet_addresses(wallet=wallet)


def _fetch_vault_wallet_addresses(wallet: FireblocksWallet) -> VaultWalletAddress:
    """
    Fetch and save all deposit addresses from Fireblocks for the given FireblocksWallet.
    """
    new_address = None

    # Call fireblocks and get deposit addresses for the given wallet
    fb = get_fireblocks_client()
    addresses = fb.get_deposit_addresses(vault_account_id=wallet.vault_account.vault_id,
                                         asset_id=wallet.asset.asset_id)
    for address_data in addresses:
        defaults = {
            'description': address_data['description'],
            'tag': address_data['tag'],
            'type': address_data['type'],
        }
        address, created = VaultWalletAddress.objects.get_or_create(
            wallet=wallet, address=address_data['address'], defaults=defaults)
        if created:
            new_address = address

    # TODO raise better exception
    assert new_address is not None
    return new_address


def set_address_description(address: VaultWalletAddress, description: str):
    """
    Update the addresses description for non-ETH-based assets on Fireblocks.
    Fireblocks does not support updating address description for ERC-20 assets.
    Upon success, also update the description in the database for this address.
    """
    asset = address.wallet.asset
    if not asset.is_erc_20:
        vault_account = address.wallet.vault_account
        fb = get_fireblocks_client()

        try:
            response = fb.set_address_description(vault_account_id=vault_account.vault_id, asset_id=asset.asset_id,
                                                  address=address.address, description=description)
        except FireblocksApiException as e:
            logger.error(f'Failed to set new description for {address} - {e}')
        else:
            if response['success'] is True:
                address.description = description
                address.save()
            else:
                raise Exception(f'Invalid response returned: {response}')
