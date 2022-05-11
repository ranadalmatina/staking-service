from django_fsm import TransitionNotAllowed

from django.test import TestCase

from ..factories import VaultWithdrawalFactory
from ..models import VaultWithdrawal


class VaultWithdrawalAllowedStateTransitionTestCase(TestCase):

    def test_new_to_approved(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.NEW)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.NEW)
        withdrawal.approve()
        withdrawal.save()
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.APPROVED)

    def test_approved_to_queued(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.APPROVED)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.APPROVED)
        withdrawal.queue()
        withdrawal.save()
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.QUEUED)

    def test_queued_to_sent(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.QUEUED)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.QUEUED)
        withdrawal.send()
        withdrawal.save()
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.SENT)

    def test_sent_to_confirmed(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.SENT)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.SENT)
        withdrawal.confirm()
        withdrawal.save()
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.CONFIRMED)


class VaultWithdrawalIllegalStateTransitionTestCase(TestCase):

    def test_new_to_queued(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.NEW)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.NEW)
        with self.assertRaises(TransitionNotAllowed):
            withdrawal.queue()

    def test_new_to_sent(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.NEW)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.NEW)
        with self.assertRaises(TransitionNotAllowed):
            withdrawal.send()

    def test_new_to_confirmed(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.NEW)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.NEW)
        with self.assertRaises(TransitionNotAllowed):
            withdrawal.confirm()

    def test_queued_to_confirmed(self):
        withdrawal = VaultWithdrawalFactory(status=VaultWithdrawal.STATUS.QUEUED)
        self.assertEqual(withdrawal.status, VaultWithdrawal.STATUS.QUEUED)
        with self.assertRaises(TransitionNotAllowed):
            withdrawal.confirm()
