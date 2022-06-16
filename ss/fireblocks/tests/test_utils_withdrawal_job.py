from unittest import mock, skip

from django.test import TestCase

from ..factories import ExternalWalletAssetFactory, ExternalWalletFactory, VaultAssetFactory
from ..factories.withdrawal import WithdrawalJobFactory
from ..models import ExternalWallet, ExternalWalletAsset, VaultWithdrawal, WithdrawalJob
from ..utils.withdrawal_job import _pending_withdrawal_job, create_vault_withdrawal


@skip
@mock.patch('fireblocks.utils.external_wallet._create_external_wallet_asset')
@mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
class CreatVaultWithdrawalTestCase(TestCase):

    def setUp(self):
        self.wallet = ExternalWalletFactory()
        self.asset = VaultAssetFactory(asset_id='BTC_TEST')

    def test_new_to_pending(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        job = WithdrawalJobFactory(address=address, status=WithdrawalJob.STATUS.NEW)
        # External wallet asset is not yet approved, so job will stop in pending state
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address,
                                   status=ExternalWalletAsset.STATUS.WAITING_FOR_APPROVAL)

        # ExternalWalletAsset already exists but VaultWithdrawal does not
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        create_vault_withdrawal(job=job)

        job.refresh_from_db()
        # Nothing changes with objects but job moves to PENDING state
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)
        self.assertIsNone(job.withdrawal)
        # Neither mock is called
        self.assertFalse(mock_create_external_wallet.called)
        self.assertFalse(mock_create_external_wallet_asset.called)

    def test_new_to_failed(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        # Job goes from NEW to PENDING and then to FAILED when it finds the EWA is REJECTED
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        job = WithdrawalJobFactory(address=address, status=WithdrawalJob.STATUS.NEW)
        # External wallet asset is rejected, so job will stop will fail with message about EWA status
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address,
                                   status=ExternalWalletAsset.STATUS.REJECTED)

        # ExternalWalletAsset already exists but VaultWithdrawal does not
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        create_vault_withdrawal(job=job)

        job.refresh_from_db()
        # Nothing changes with objects but job moves to FAILED state
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(job.status, WithdrawalJob.STATUS.FAILED)
        self.assertIsNone(job.withdrawal)
        # Neither mock is called
        self.assertFalse(mock_create_external_wallet.called)
        self.assertFalse(mock_create_external_wallet_asset.called)

    def test_new_to_success_one_wallet(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        job = WithdrawalJobFactory(address=address, status=WithdrawalJob.STATUS.NEW)
        # External wallet asset is approved, job will complete
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address,
                                   status=ExternalWalletAsset.STATUS.APPROVED)

        # ExternalWalletAsset already exists but VaultWithdrawal does not
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        create_vault_withdrawal(job=job)

        job.refresh_from_db()
        # VaultWithdrawal object gets created
        self.assertEqual(VaultWithdrawal.objects.count(), 1)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(job.status, WithdrawalJob.STATUS.SUCCESS)
        self.assertIsNotNone(job.withdrawal)
        # Neither mock is called
        self.assertFalse(mock_create_external_wallet.called)
        self.assertFalse(mock_create_external_wallet_asset.called)

    def test_new_to_success_two_wallets(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        mock_create_external_wallet.side_effect = lambda name: ExternalWalletFactory(name=name)

        def create_external_wallet_assset(wallet, asset, address):
            return ExternalWalletAssetFactory(wallet=wallet, asset=asset, address=address)
        mock_create_external_wallet_asset.side_effect = create_external_wallet_assset

        address_1 = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        address_2 = 'mobXJEuLW5eEbD7hmrggkL1qYDk6MXuxnK'

        # Job is trying to create a new EWA with a different address from one that already exists
        job = WithdrawalJobFactory(address=address_1, status=WithdrawalJob.STATUS.NEW)
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address_2,
                                   status=ExternalWalletAsset.STATUS.APPROVED)

        # There exists a single ExternalWallet with one ExternalWalletAsset. No VaultWithdrawals exist.
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWallet.objects.count(), 1)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        create_vault_withdrawal(job=job)

        job.refresh_from_db()
        # The job creates another ExternalWallet with its own ExternalWalletAsset as well as a VaultWithdrawal object
        self.assertEqual(VaultWithdrawal.objects.count(), 1)
        self.assertEqual(ExternalWallet.objects.count(), 2)
        self.assertEqual(ExternalWalletAsset.objects.count(), 2)

        self.assertEqual(job.status, WithdrawalJob.STATUS.SUCCESS)
        self.assertIsNotNone(job.withdrawal)
        self.assertEqual(job.error, '')
        # Both these mocks are called because we create a new ExternalWallet and a new ExternalWalletAsset
        self.assertTrue(mock_create_external_wallet.called)
        self.assertTrue(mock_create_external_wallet_asset.called)


@skip
@mock.patch('fireblocks.utils.external_wallet._create_external_wallet_asset')
@mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
class WithdrawalJobUtilsUnitTestCase(TestCase):

    def setUp(self):
        self.wallet = ExternalWalletFactory()
        self.asset = VaultAssetFactory(asset_id='BTC_TEST')

    def test_pending_withdrawal_job_ewa_rejected(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        job = WithdrawalJobFactory(address=address, status=WithdrawalJob.STATUS.PENDING)
        # External wallet asset is rejected, so job will stop will fail with message about EWA status
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address,
                                   status=ExternalWalletAsset.STATUS.REJECTED)

        # ExternalWalletAsset already exists but VaultWithdrawal does not
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        _pending_withdrawal_job(job=job)

        job.refresh_from_db()
        # Nothing changes with objects but job moves to FAILED state
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(job.status, WithdrawalJob.STATUS.FAILED)
        self.assertIsNone(job.withdrawal)
        # Neither mock is called
        self.assertFalse(mock_create_external_wallet.called)
        self.assertFalse(mock_create_external_wallet_asset.called)

    def test_pending_withdrawal_job_ewa_failed(self, mock_create_external_wallet, mock_create_external_wallet_asset):
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'
        job = WithdrawalJobFactory(address=address, status=WithdrawalJob.STATUS.PENDING)
        # External wallet asset is rejected, so job will stop will fail with message about EWA status
        ExternalWalletAssetFactory(wallet=self.wallet, asset=self.asset, address=address,
                                   status=ExternalWalletAsset.STATUS.FAILED)

        # ExternalWalletAsset already exists but VaultWithdrawal does not
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        _pending_withdrawal_job(job=job)

        job.refresh_from_db()
        # Nothing changes with objects but job moves to FAILED state
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(job.status, WithdrawalJob.STATUS.FAILED)
        self.assertIsNone(job.withdrawal)
        # Neither mock is called
        self.assertFalse(mock_create_external_wallet.called)
        self.assertFalse(mock_create_external_wallet_asset.called)
