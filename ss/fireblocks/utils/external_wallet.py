import logging

from ..client import get_fireblocks_client
from ..exceptions import ExternalWalletAssetAlreadyExists
from ..models import ExternalWallet, ExternalWalletAsset, VaultAsset

logger = logging.getLogger(__name__)




def _create_external_wallet(name: str) -> ExternalWallet:
    """
    Call Fireblocks and create new external wallet
    """
    fb = get_fireblocks_client()

    response = fb.create_external_wallet(name=name)
    logger.info(response)
    return ExternalWallet.objects.create(id=response['id'], name=response['name'])


def _get_empty_external_wallet(name: str, vault_asset: VaultAsset) -> ExternalWallet:
    """
    Fetch an ExternalWallet for the given trader which does not contain the asset.
    Create a new external wallet for this Trader if one doesn't exist.
    """
    wallet = ExternalWallet.objects.filter(name=name).exclude(assets__asset=vault_asset).first()

    if wallet is None:
        return _create_external_wallet(name)
    return wallet


def _create_external_wallet_asset(wallet: ExternalWallet,
                                  vault_asset: VaultAsset, address: str) -> ExternalWalletAsset:
    """
    Call Fireblocks and create new external wallet asset.
    """
    fb = get_fireblocks_client()
    response = fb.create_external_wallet_asset(wallet_id=wallet.id, asset_id=vault_asset.asset_id, address=address)

    # The ID we get back in this response is a VaultAsset ID
    assert response['id'] == vault_asset.asset_id

    logger.info(response)
    tag = response.get('tag', '')  # Usually empty

    return ExternalWalletAsset.objects.create(
        # Here we automatically generate a UUID for the ExternalWalletAsset
        wallet=wallet,
        asset=vault_asset,
        address=address,
        status=response['status'],
        tag=tag,
    )


def get_external_wallet_asset(vault_asset: VaultAsset, address: str) -> ExternalWalletAsset:
    """
    Given a withdrawal address and vault asset, get the matching external wallet asset.
    Create a new external wallet asset for this account/asset/address if one
    doesn't exist.
    """
    try:
        return ExternalWalletAsset.objects.get(asset=vault_asset, address=address)
    except ExternalWalletAsset.DoesNotExist:
        # TODO fix default name here
        wallet = _get_empty_external_wallet(name="Contract", vault_asset=vault_asset)

        try:
            # Make sure that no other address has been registered for this asset with this wallet
            ExternalWalletAsset.objects.get(wallet=wallet, asset=vault_asset)
        except ExternalWalletAsset.DoesNotExist:
            # There is no other address so lets try and create one
            return _create_external_wallet_asset(wallet, vault_asset, address)
        else:
            # We already have an address for this asset but we are trying to create another
            # This is impossible, so raise an exception
            raise ExternalWalletAssetAlreadyExists(
                f'ExternalWalletAsset already exists for wallet: {wallet} and asset: {vault_asset}')
