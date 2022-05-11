from django_fsm import TransitionNotAllowed

from django.test import TestCase

from ..factories import VaultWithdrawalFactory, WithdrawalJobFactory
from ..models import WithdrawalJob


class WithdrawalJobAllowedStateTransitionTestCase(TestCase):

    def test_new_to_pending(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.NEW)
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        job.pending()
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)

    def test_pending_to_success(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.PENDING)
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)
        withdrawal = VaultWithdrawalFactory()
        job.complete(withdrawal=withdrawal)
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.status, WithdrawalJob.STATUS.SUCCESS)
        self.assertEqual(job.withdrawal.id, withdrawal.id)

    def test_new_to_failed(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.NEW)
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        job.fail(reason='Something went wrong')
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.status, WithdrawalJob.STATUS.FAILED)
        self.assertEqual(job.error, 'Something went wrong')

    def test_pending_to_failed(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.PENDING)
        self.assertEqual(job.status, WithdrawalJob.STATUS.PENDING)
        job.fail(reason='Something went wrong')
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.status, WithdrawalJob.STATUS.FAILED)
        self.assertEqual(job.error, 'Something went wrong')


class WithdrawalJobIllegalStateTransitionTestCase(TestCase):

    def test_new_to_success(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.NEW)
        self.assertEqual(job.status, WithdrawalJob.STATUS.NEW)
        withdrawal = VaultWithdrawalFactory()
        with self.assertRaises(TransitionNotAllowed):
            job.complete(withdrawal=withdrawal)

    def test_success_to_failed(self):
        job = WithdrawalJobFactory(status=WithdrawalJob.STATUS.SUCCESS)
        self.assertEqual(job.status, WithdrawalJob.STATUS.SUCCESS)
        with self.assertRaises(TransitionNotAllowed):
            job.fail(reason='Something went wrong')
