import logging

from celery import shared_task

from .client import get_fireblocks_client
from .models import ExternalWalletAsset, WithdrawalJob
from .utils.fireblocks_import import import_fireblocks
from .utils.withdrawal_job import create_vault_withdrawal

logger = logging.getLogger(__name__)


@shared_task
def update_pending_wallets():
    """
    Update the status of external wallets.
    """
    for ewa in ExternalWalletAsset.objects.filter(status=ExternalWalletAsset.STATUS.WAITING_FOR_APPROVAL):
        update_pending_wallet(ewa.id)


def update_pending_wallet(external_wallet_asset_id):
    ewa = ExternalWalletAsset.objects.get(id=external_wallet_asset_id)
    logger.info(f'Updating ExternalWalletAsset status for {ewa}')

    wallet = ewa.wallet
    fb = get_fireblocks_client()
    wallet_data = fb.get_external_wallet(wallet_id=wallet.id)

    wallet_assets = wallet_data['assets']
    for asset in wallet_assets:
        asset_id = asset['id']
        address = asset['address']
        if address == ewa.address and asset_id == ewa.asset.asset_id:
            ewa.update_status(new_status=asset['status'], save=True)


@shared_task
def process_withdrawal_jobs():
    """
    Loop over all NEW and PENDING WithdrawlJob objects and run the appropriate actions.
    """
    for job in WithdrawalJob.objects.filter(status__in=(WithdrawalJob.STATUS.NEW, WithdrawalJob.STATUS.PENDING)):
        logger.info(f'Processing job {job} with status: {job.status}')
        create_vault_withdrawal(job)


@shared_task
def fireblocks_import():
    """
    Import all objects from Fireblocks including linking transactions to Deposits/Withdrawals.
    """
    import_fireblocks(link_transactions=True)
