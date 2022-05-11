from django.test import TestCase

from ..factories import TransactionFactory, VaultDepositFactory
from ..models import VaultDeposit
from ..utils.deposit import update_deposit_status


class DepositUtilsTestCase(TestCase):

    def test_update_deposit_status_new_completed(self):
        deposit = VaultDepositFactory()
        transaction = TransactionFactory(deposit=deposit)  # Add linked Transaction
        self.assertEqual(deposit.status, VaultDeposit.STATUS.NEW)
        update_deposit_status(transaction)
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.CONFIRMED)

    def test_update_deposit_status_received_completed(self):
        # In real life this deposit would already have a linked deposit in order to become received
        deposit = VaultDepositFactory(status=VaultDeposit.STATUS.RECEIVED)
        transaction = TransactionFactory(deposit=deposit)
        self.assertEqual(deposit.status, VaultDeposit.STATUS.RECEIVED)
        update_deposit_status(transaction)
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.CONFIRMED)

    def test_update_deposit_status_new_received(self):
        deposit = VaultDepositFactory()
        transaction = TransactionFactory(status='CONFIRMING', deposit=deposit)  # Add linked Transaction
        self.assertEqual(deposit.status, VaultDeposit.STATUS.NEW)
        update_deposit_status(transaction)
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.RECEIVED)
