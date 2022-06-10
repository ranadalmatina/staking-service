from django.test import TestCase

from web3 import Web3
from decimal import Decimal

from .factories import FillJobFactory
from .models import FillJob


class FillJobModelTestCase(TestCase):

    def test_fill_job(self):
        job = FillJobFactory()
        self.assertEqual(job.status, FillJob.STATUS.NEW)
        self.assertEqual(job.amount, Decimal('1.23456'))
        self.assertEqual(job.amount_wei, Decimal('1.23456') * Decimal('10')**18)

    def test_create_fill_job(self):
        amount_wei = Web3.toWei(Decimal('9.876'), 'ether')
        self.assertEqual(FillJob.objects.count(), 0)
        job = FillJob.objects.create(status=FillJob.STATUS.NEW, amount_wei=amount_wei)
        self.assertEqual(FillJob.objects.count(), 1)
        self.assertEqual(job.amount, Decimal('9.876'))
