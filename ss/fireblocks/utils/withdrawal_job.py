import json
import logging

from django.db import transaction

from ..exceptions import ExternalWalletAssetAlreadyExists
from ..models import ExternalWalletAsset, VaultWithdrawal, WithdrawalJob
from .external_wallet import get_external_wallet_asset

logger = logging.getLogger(__name__)


def _get_external_wallet_asset(job: WithdrawalJob):
    """
    Get or create an ExternalWalletAsset using data from a WithdrawalJob object.
    """
    try:
        # Get or create an ExternalWallet and ExternalWalletAsset with
        # the given currency code and address
        return get_external_wallet_asset(vault_asset=job.asset, address=job.address)
    except ExternalWalletAssetAlreadyExists as e:
        logger.error(str(e))
        msg = json.dumps(
            {'address': f'An address already exists for this vault_asset: {job.asset}'})
        with transaction.atomic():
            job.fail(msg)
            job.save()

    return None


def _new_withdrawal_job(job: WithdrawalJob):
    """
    Given a NEW WithdrawalJob, try to create the ExternalWalletAsset
    """
    if job.status == WithdrawalJob.STATUS.NEW:
        wallet_asset = _get_external_wallet_asset(job)
        if wallet_asset is not None:
            with transaction.atomic():
                # Upon successful creation, we mark the job as pending
                job.pending()
                job.save()


def _pending_withdrawal_job(job: WithdrawalJob):
    """
    Given a PENDING WithdrawalJob, try to create the VaultWithdrawal.
    """
    if job.status == WithdrawalJob.STATUS.PENDING:
        wallet_asset = _get_external_wallet_asset(job)
        assert wallet_asset is not None

        # Only create the VaultWithdrawal object when the ExternalWalletAsset is approved
        if wallet_asset.status == ExternalWalletAsset.STATUS.APPROVED:
            with transaction.atomic():
                withdrawal = VaultWithdrawal.objects.create(wallet_asset=wallet_asset, amount=job.amount)
                job.complete(withdrawal)
                job.save()

        # Fail the job if the ExternalWalletAsset is rejected or failed
        elif wallet_asset.status in (ExternalWalletAsset.STATUS.REJECTED, ExternalWalletAsset.STATUS.FAILED):
            msg = json.dumps({'ExternalWalletAsset': f'Fireblocks returned {wallet_asset.status} status'})
            with transaction.atomic():
                job.fail(msg)
                job.save()


def create_vault_withdrawal(job: WithdrawalJob):
    """
    Create an ExternalWalletAsset and then a VaultWithdrawal object
    using data from a WithdrawalJob object.
    """
    _new_withdrawal_job(job)
    _pending_withdrawal_job(job)
