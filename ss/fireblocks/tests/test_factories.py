from decimal import Decimal

from django.db.models import ObjectDoesNotExist
from django.test import TestCase

from ..factories import (VaultAccountFactory, ConfirmedWithdrawalFactory, ExternalWalletAssetFactory,
                         ExternalWalletFactory, FireblocksWalletFactory, SuccessfulDepositFactory,
                         SuccessfulWithdrawalJobFactory, VaultAssetFactory, VaultDepositFactory,
                         VaultWalletAddressFactory, VaultWithdrawalFactory, WithdrawalJobFactory)
from ..models import (ExternalWallet, ExternalWalletAsset, FireblocksWallet, Transaction, VaultAccount, VaultAsset,
                      VaultDeposit, VaultWalletAddress, VaultWithdrawal, WithdrawalJob)


class ModelFactoryTestCase(TestCase):
    """
    Test that are factories work as expected. They are crucial parts of the testing framework
    """

    def test_vault_account_factory(self):
        vault_account = VaultAccountFactory()
        self.assertIsInstance(vault_account, VaultAccount)

    def test_vault_asset_factory(self):
        vault_asset = VaultAssetFactory()
        self.assertIsInstance(vault_asset, VaultAsset)

    def test_fireblocks_wallet_factory(self):
        fireblocks_wallet = FireblocksWalletFactory()
        self.assertIsInstance(fireblocks_wallet, FireblocksWallet)
        self.assertIn(fireblocks_wallet.asset.asset_id, ['BTC', 'ETH', 'BTC_TEST', 'ETH_TEST', 'DASH'])

    def test_xtn_wallet_factory(self):
        fireblocks_wallet = FireblocksWalletFactory(asset__asset_id='BTC_TEST')
        self.assertIsInstance(fireblocks_wallet, FireblocksWallet)

        btc_test = VaultAsset.objects.get(asset_id='BTC_TEST')
        self.assertEqual(fireblocks_wallet.asset, btc_test)
        self.assertIn(fireblocks_wallet.asset.asset_id, 'BTC_TEST')

    def test_external_wallet_factory(self):
        wallet = ExternalWalletFactory()
        self.assertIsInstance(wallet, ExternalWallet)
        self.assertIsNotNone(wallet.customer_ref_id)
        self.assertEqual(wallet.customer_ref_id, '')

    def test_external_wallet_asset_factory(self):
        ewa = ExternalWalletAssetFactory()
        self.assertIsInstance(ewa, ExternalWalletAsset)
        self.assertIsInstance(ewa.wallet, ExternalWallet)
        self.assertIsInstance(ewa.asset, VaultAsset)
        self.assertIsNotNone(ewa.address)
        self.assertNotEqual(ewa.address, '')

    def test_vault_wallet_address_factory(self):
        address = VaultWalletAddressFactory()
        self.assertIsInstance(address, VaultWalletAddress)
        self.assertIsInstance(address.wallet, FireblocksWallet)
        self.assertIsNotNone(address.address)
        self.assertIsInstance(address.address, str)
        self.assertGreater(len(address.address), 10)
        self.assertEqual(address.description, '')

    def test_vault_wallet_address_factory_linked_trader(self):
        address = VaultWalletAddressFactory()
        self.assertIsInstance(address, VaultWalletAddress)
        self.assertIsInstance(address.wallet, FireblocksWallet)
        self.assertIsNotNone(address.address)
        self.assertIsInstance(address.address, str)
        self.assertGreater(len(address.address), 10)

    def test_vault_deposit_factory(self):
        vault_deposit = VaultDepositFactory()
        self.assertIsInstance(vault_deposit, VaultDeposit)
        self.assertEqual(vault_deposit.status, VaultDeposit.STATUS.NEW)
        with self.assertRaises(ObjectDoesNotExist):
            vault_deposit.transaction

    def test_completed_vault_deposit(self):
        address = VaultWalletAddressFactory()
        vault_deposit = SuccessfulDepositFactory(address=address)
        self.assertIsInstance(vault_deposit, VaultDeposit)
        self.assertEqual(vault_deposit.status, VaultDeposit.STATUS.CONFIRMED)
        self.assertIsNotNone(vault_deposit.transaction)
        self.assertIsInstance(vault_deposit.transaction, Transaction)

    def test_vault_withdrawal_factory(self):
        vault_withdrawal = VaultWithdrawalFactory()
        btc_test = VaultAsset.objects.get(asset_id='BTC_TEST')

        self.assertIsInstance(vault_withdrawal, VaultWithdrawal)
        self.assertEqual(vault_withdrawal.status, VaultWithdrawal.STATUS.NEW)
        with self.assertRaises(ObjectDoesNotExist):
            vault_withdrawal.transaction
        self.assertIsNotNone(vault_withdrawal.wallet_asset.address)
        self.assertIsInstance(vault_withdrawal.wallet_asset.address, str)
        # The currency code and asset code should align
        self.assertEqual(vault_withdrawal.wallet_asset.asset, btc_test)

    def test_confirmed_vault_withdrawal_factory(self):
        vault_withdrawal = ConfirmedWithdrawalFactory()
        self.assertIsInstance(vault_withdrawal, VaultWithdrawal)
        self.assertEqual(vault_withdrawal.status, VaultWithdrawal.STATUS.CONFIRMED)
        self.assertIsNotNone(vault_withdrawal.transaction)
        self.assertIsInstance(vault_withdrawal.transaction, Transaction)

    def test_withdrawal_job_factory(self):
        job = WithdrawalJobFactory()
        self.assertIsInstance(job, WithdrawalJob)
        self.assertIsNotNone(job.address)
        self.assertGreater(len(job.address), 5)
        self.assertGreater(job.amount, Decimal('0'))
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        self.assertIsNone(job.withdrawal)

    def test_successfull_withdrawal_job_factory(self):
        job = SuccessfulWithdrawalJobFactory()
        self.assertIsInstance(job, WithdrawalJob)
        self.assertIsNotNone(job.address)
        self.assertGreater(len(job.address), 5)
        self.assertGreater(job.amount, Decimal('0'))
        self.assertEqual(job.status, WithdrawalJob.STATUS.SUCCESS)
        self.assertIsInstance(job.withdrawal, VaultWithdrawal)
