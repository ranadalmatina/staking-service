from decimal import Decimal

from django_fsm import TransitionNotAllowed

from django.test import TestCase

from ..factories import VaultDepositFactory
from ..models import VaultDeposit


class ModelTestCase(TestCase):

    def test_vault_deposit(self):
        deposit = VaultDepositFactory()
        self.assertEqual(deposit.amount, Decimal('0'))
        self.assertEqual(deposit.fee, Decimal('0'))
        self.assertEqual(deposit.asset.asset_id, 'BTC_TEST')


class VaultDepositAllowedStateTransitionTestCase(TestCase):

    def test_new_to_received(self):
        deposit = VaultDepositFactory(status=VaultDeposit.STATUS.NEW)
        self.assertEqual(deposit.status, VaultDeposit.STATUS.NEW)
        deposit.receive()
        deposit.save()
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.RECEIVED)

    def test_new_to_confirmed(self):
        # Transaction may only arrive later after deposit is confirmed
        # thus we don't go to received state first
        deposit = VaultDepositFactory(status=VaultDeposit.STATUS.NEW)
        self.assertEqual(deposit.status, VaultDeposit.STATUS.NEW)
        deposit.confirm()
        deposit.save()
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.CONFIRMED)

    def test_received_to_confirmed(self):
        deposit = VaultDepositFactory(status=VaultDeposit.STATUS.RECEIVED)
        self.assertEqual(deposit.status, VaultDeposit.STATUS.RECEIVED)
        deposit.confirm()
        deposit.save()
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, VaultDeposit.STATUS.CONFIRMED)


class VaultDepositIllegalStateTransitionTestCase(TestCase):

    def test_confirmed_to_received(self):
        # This would be a backwards transition and should not be allowed
        deposit = VaultDepositFactory(status=VaultDeposit.STATUS.CONFIRMED)
        self.assertEqual(deposit.status, VaultDeposit.STATUS.CONFIRMED)
        with self.assertRaises(TransitionNotAllowed):
            deposit.receive()
