import uuid
from decimal import Decimal
from unittest import mock

from fireblocks_sdk import TRANSACTION_STATUS_COMPLETED, TRANSACTION_STATUS_FAILED
from fireblocks_sdk.api_types import FireblocksApiException
from web3 import Web3
from web3.types import Wei

from django.test import TestCase

from fireblocks.client import FireblocksClient
from staking.graphql import GraphAPI

from .factories import FillJobFactory
from .fill import ASSET_ID, FB_CONTRACT_ID, VAULT_ACCOUNT, Fill
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


class TestFillTask(TestCase):

    def test_run_fill_multiple_pending_jobs(self):
        FillJobFactory(status=FillJob.STATUS.NEW)
        FillJobFactory(status=FillJob.STATUS.PENDING)
        runner = Fill()
        with self.assertRaises(AssertionError):
            runner.run_fill()

    @mock.patch.object(Fill, 'check_transaction_state')
    def test_run_fill_pending_job_check_status(self, check_mock):
        job = FillJobFactory(status=FillJob.STATUS.PENDING)
        runner = Fill()
        runner.run_fill()

        # Check that check_transaction_state was called with the job.
        check_mock.assert_called_with(job)

    @mock.patch.object(Fill, 'submit_transaction')
    def test_run_fill_new_job_submit(self, submit_mock):
        job = FillJobFactory(status=FillJob.STATUS.NEW)
        runner = Fill()
        runner.run_fill()

        # Check that submit_transaction was called with the job.
        submit_mock.assert_called_with(job)

    @mock.patch.object(GraphAPI, 'contract_avax_deficit')
    def test_fill_no_deficit(self, deficit_mock):
        deficit_mock.return_value = Wei(0)
        runner = Fill()
        runner.run_fill()
        self.assertEqual(FillJob.objects.count(), 0)

    @mock.patch.object(FireblocksClient, 'available_balance_wei')
    @mock.patch.object(GraphAPI, 'contract_avax_deficit')
    def test_fill_deficit_but_no_balance(self, deficit_mock, balance_mock):
        deficit_mock.return_value = Wei(100)
        balance_mock.return_value = Wei(0)

        runner = Fill()
        runner.run_fill()
        self.assertEqual(FillJob.objects.count(), 0)

    @mock.patch.object(FireblocksClient, 'get_transaction_by_id')
    @mock.patch.object(FireblocksClient, 'external_contract_call')
    @mock.patch.object(FireblocksClient, 'available_balance_wei')
    @mock.patch.object(GraphAPI, 'contract_avax_deficit')
    def test_fill_job_created(self, deficit_mock, balance_mock, call_mock, get_mock):
        deficit_mock.return_value = Wei(100)
        balance_mock.return_value = Wei(100000000)

        tx_id = uuid.uuid4()
        call_mock.return_value = {
            'id': tx_id,
        }

        # Assume likely case where api returns nothing for the call after creating.
        get_mock.side_effect = FireblocksApiException(error_code=404)

        runner = Fill()
        runner.run_fill()

        self.assertEqual(FillJob.objects.count(), 1)
        job = FillJob.objects.first()
        self.assertEqual(job.status, FillJob.STATUS.PENDING)

        call_mock.assert_called_once()
        deficit_mock.assert_called_once()
        balance_mock.assert_called_once()
        get_mock.assert_called_once()

    @mock.patch.object(FireblocksClient, 'external_contract_call')
    def test_submit_transaction_not_new(self, call_mock):
        job = FillJobFactory(status=FillJob.STATUS.PENDING)
        runner = Fill()
        runner.submit_transaction(job)
        call_mock.assert_not_called()

    @mock.patch.object(FireblocksClient, 'external_contract_call')
    def test_submit_transaction_new(self, call_mock):
        job = FillJobFactory(status=FillJob.STATUS.NEW)
        tx_id = uuid.uuid4()
        call_mock.return_value = {
            'id': tx_id,
        }

        runner = Fill()
        runner.submit_transaction(job)

        call_mock.assert_called_with(
            vault_account_id=VAULT_ACCOUNT,
            asset_id=ASSET_ID,
            external_contract_id=FB_CONTRACT_ID,
            amount="1.23456",
            data="0xccf00d2d",
            note="Fill contract deficit",
        )

        self.assertEqual(job.fireblocks_transaction_id, tx_id)

    @mock.patch.object(FireblocksClient, 'get_transaction_by_id')
    def test_check_transaction_state_not_pending(self, get_mock):
        job = FillJobFactory(status=FillJob.STATUS.NEW)
        runner = Fill()
        runner.check_transaction_state(job)

        get_mock.assert_not_called()

    @mock.patch.object(FireblocksClient, 'get_transaction_by_id')
    def test_check_transaction_state_complete(self, get_mock):
        job = FillJobFactory(status=FillJob.STATUS.PENDING)
        tx_id = uuid.uuid4()
        job.fireblocks_transaction_id = tx_id

        get_mock.return_value = {
            'status': TRANSACTION_STATUS_COMPLETED,
        }

        runner = Fill()
        runner.check_transaction_state(job)

        get_mock.asset_called_with(tx_id)
        self.assertEqual(job.status, FillJob.STATUS.COMPLETED)

    @mock.patch.object(FireblocksClient, 'get_transaction_by_id')
    def test_check_transaction_state_fail(self, get_mock):
        job = FillJobFactory(status=FillJob.STATUS.PENDING)
        tx_id = uuid.uuid4()
        job.fireblocks_transaction_id = tx_id

        get_mock.return_value = {
            'status': TRANSACTION_STATUS_FAILED,
        }

        runner = Fill()
        runner.check_transaction_state(job)

        get_mock.asset_called_with(tx_id)
        self.assertEqual(job.status, FillJob.STATUS.FAILED)
