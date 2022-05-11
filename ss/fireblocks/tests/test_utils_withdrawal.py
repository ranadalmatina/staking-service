from decimal import Decimal
from unittest import mock

from fireblocks_sdk import FireblocksApiException

from django.test import TestCase

from ..exceptions import BroadcastFailed, IllegalWithdrawalState
from ..factories import (VaultAccountFactory, ExternalWalletAssetFactory, ExternalWalletFactory,
                         VaultAssetFactory, VaultWithdrawalFactory)
from ..factories.transaction import WithdrawalTransactionFactory
from ..models import VaultWithdrawal
from ..utils.withdrawal import broadcast_withdrawal, get_or_create_withdrawal


class WithdrawalUtilsTestCase(TestCase):

    def setUp(self):
        self.wallet = ExternalWalletFactory()
        self.wallet_asset = ExternalWalletAssetFactory(wallet=self.wallet, asset__asset_id='BTC')

    def test_get_or_create_simple_find(self):
        tx = WithdrawalTransactionFactory()
        # Withdrawal contains transaction ID and so will be matched even if other parameters don't match
        existing_withdrawal = VaultWithdrawalFactory(transaction_id=tx.tx_id)

        # Transaction is not matched
        self.assertIsNone(tx.withdrawal)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)

        withdrawal = get_or_create_withdrawal(transaction=tx)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)
        self.assertEqual(existing_withdrawal.id, withdrawal.id)
        self.assertEqual(tx.withdrawal, withdrawal)  # Matched

    def test_get_or_create_withdrawal_get(self):
        # Withdrawal and Transaction match each other so will be linked together
        existing_withdrawal = VaultWithdrawalFactory(wallet_asset=self.wallet_asset,
                                                     amount=Decimal('0.001'), status=VaultWithdrawal.STATUS.SENT)
        tx = WithdrawalTransactionFactory(asset_id='BTC', external_wallet=self.wallet, amount='0.001')

        # Transaction is not matched
        self.assertIsNone(tx.withdrawal)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)

        withdrawal = get_or_create_withdrawal(transaction=tx)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)
        self.assertEqual(existing_withdrawal.id, withdrawal.id)
        self.assertEqual(tx.withdrawal, withdrawal)  # Matched

    def test_get_or_create_withdrawal_get_failure(self):
        # The amount of the Transaction and the existing VaultWithdrawal don't match
        existing_withdrawal = VaultWithdrawalFactory(wallet_asset=self.wallet_asset,
                                                     amount=Decimal('0.002'), status=VaultWithdrawal.STATUS.SENT)
        tx = WithdrawalTransactionFactory(asset_id='BTC', external_wallet=self.wallet, amount='0.001')

        # Transaction is not matched
        self.assertIsNone(tx.withdrawal)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)

        withdrawal = get_or_create_withdrawal(transaction=tx, create=True)
        # Because we cant find a match a new VaultWithdrawal object will be created
        self.assertEqual(VaultWithdrawal.objects.count(), 2)
        self.assertNotEqual(existing_withdrawal.id, withdrawal.id)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.SENT)
        self.assertEqual(tx.withdrawal, withdrawal)  # Matched

    def test_get_or_create_withdrawal_create_true(self):
        tx = WithdrawalTransactionFactory(asset_id='BTC', external_wallet=self.wallet)

        # Transaction is not matched
        self.assertIsNone(tx.withdrawal)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)

        withdrawal = get_or_create_withdrawal(transaction=tx, create=True)
        self.assertEqual(VaultWithdrawal.objects.count(), 1)
        self.assertEqual(withdrawal.amount, tx.amount)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.SENT)
        self.assertEqual(tx.withdrawal, withdrawal)  # Matched

    def test_get_or_create_withdrawal_create_false(self):
        tx = WithdrawalTransactionFactory(asset_id='BTC', external_wallet=self.wallet)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        withdrawal = get_or_create_withdrawal(transaction=tx, create=False)
        self.assertEqual(VaultWithdrawal.objects.count(), 0)
        self.assertIsNone(withdrawal)


class BroadcastWithdrawalTestCase(TestCase):

    def setUp(self):
        VaultAccountFactory(vault_id=0)
        btc_test = VaultAssetFactory(asset_id='BTC_TEST')
        self.wallet_asset = ExternalWalletAssetFactory(asset=btc_test)

    def test_broadcast_new_withdrawal(self):
        withdrawal = VaultWithdrawalFactory()
        with self.assertRaises(IllegalWithdrawalState) as ar:
            broadcast_withdrawal(withdrawal=withdrawal)
        self.assertEqual(str(ar.exception), 'Unable to process VaultWithdrawal with status: new')

    def test_broadcast_approved_withdrawal(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.APPROVED)
        with self.assertRaises(IllegalWithdrawalState) as ar:
            broadcast_withdrawal(withdrawal=withdrawal)
        self.assertEqual(str(ar.exception), 'Unable to process VaultWithdrawal with status: approved')

    def test_broadcast_sent_withdrawal(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.SENT)
        with self.assertRaises(IllegalWithdrawalState) as ar:
            broadcast_withdrawal(withdrawal=withdrawal)
        self.assertEqual(str(ar.exception), 'Unable to process VaultWithdrawal with status: sent')

    @mock.patch('fireblocks.utils.withdrawal.get_fireblocks_client')
    def test_broadcast_queued_withdrawal(self, mock_get_fb_client):
        # We have created a transaction on Fireblocks and get a Transaction ID back in response
        external_wallet_withdrawal_response = {'id': 'bd20fcd3-3697-4dbe-be8e-4b7b13f7d04a', 'status': 'SUBMITTED'}
        mock_get_fb_client.return_value.external_wallet_withdrawal.return_value = external_wallet_withdrawal_response

        withdrawal = VaultWithdrawalFactory(wallet_asset=self.wallet_asset,
                                            status=VaultWithdrawal.STATUS.QUEUED)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.QUEUED)

        response = broadcast_withdrawal(withdrawal=withdrawal)
        self.assertEqual(response, external_wallet_withdrawal_response)
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.SENT)
        self.assertEqual(withdrawal.transaction_id, 'bd20fcd3-3697-4dbe-be8e-4b7b13f7d04a')

    @mock.patch('fireblocks.utils.withdrawal.get_fireblocks_client')
    def test_broadcast_withdrawal_fireblocks_exception(self, mock_get_fb_client):
        mock_get_fb_client.return_value.external_wallet_withdrawal.side_effect = FireblocksApiException(
            {'message': 'Destination address was not found', 'code': 1411})

        withdrawal = VaultWithdrawalFactory(wallet_asset=self.wallet_asset,
                                            status=VaultWithdrawal.STATUS.QUEUED)
        with self.assertRaises(FireblocksApiException):
            broadcast_withdrawal(withdrawal=withdrawal)

    @mock.patch('fireblocks.utils.withdrawal.get_fireblocks_client')
    def test_broadcast_withdrawal_error_message(self, mock_get_fb_client):
        external_wallet_withdrawal_response = {'message': 'Destination address was not found', 'code': 1411}
        mock_get_fb_client.return_value.external_wallet_withdrawal.return_value = external_wallet_withdrawal_response

        withdrawal = VaultWithdrawalFactory(wallet_asset=self.wallet_asset,
                                            status=VaultWithdrawal.STATUS.QUEUED)
        with self.assertRaises(BroadcastFailed) as ar:
            broadcast_withdrawal(withdrawal=withdrawal)

        self.assertIn('Withdrawal transaction response', str(ar.exception))
        self.assertIn("{'message': 'Destination address was not found', 'code': 1411}", str(ar.exception))
