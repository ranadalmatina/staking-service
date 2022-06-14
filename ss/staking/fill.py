import logging

from fireblocks_sdk import TRANSACTION_STATUS_COMPLETED, TRANSACTION_STATUS_FAILED
from fireblocks_sdk.api_types import FireblocksApiException
from web3 import Web3
from web3.types import Wei

from django.conf import settings

from fireblocks.client import get_fireblocks_client
from staking.contracts import Contracts
from staking.graphql import GraphAPI

from .models import FillJob

pending_states = [FillJob.STATUS.NEW, FillJob.STATUS.PENDING]

logger = logging.getLogger(__name__)

# TODO: Parameterize this
VAULT_ACCOUNT = '1'
ASSET_ID = 'AVAXTEST'
FB_CONTRACT_ID = '290abb68-80bd-59d6-ef42-89f30eeba2e0'


class Fill:

    def __init__(self) -> None:
        self.fb_client = get_fireblocks_client()
        self.contracts = Contracts()

    def run_fill(self, amount_override: Wei = None):
        # There should never be more than one pending fill job
        assert FillJob.objects.filter(status__in=pending_states).count() <= 1

        # Check if ongoing fill is happening.
        job = FillJob.objects.filter(status__in=pending_states).first()
        if job is not None:
            if job.status == FillJob.STATUS.NEW:
                logger.info(f'Found non-executed job, submitting transaciton.')
                self.submit_transaction(job)
                return

            if job.status == FillJob.STATUS.PENDING:
                logger.info(f'Found pending job, checking transaction state.')
                self.check_transaction_state(job)
                return

            return

        # Compute deficit
        graphapi = GraphAPI(settings.GRAPHQL_URL)
        deficit = graphapi.contract_avax_deficit() if not amount_override else amount_override
        logger.info(f'Contract deficit: {deficit}')

        # Create a new job if there's a deficit.
        if deficit == 0:
            logger.info(f'No deficit, not creating a new job')
            return

        # Check we have enough balance to make the tx.
        # TODO: Handle fees
        balance = self.fb_client.available_balance_wei(VAULT_ACCOUNT, ASSET_ID)
        if balance < deficit:
            logger.info(f'Custody balance {balance} is below deficit of {deficit}')
            return

        logger.info(f'Found deficit of {deficit} AVAX')
        job = FillJob.objects.create(status=FillJob.STATUS.NEW, amount_wei=deficit)
        job.save()

        # Send transaction to fireblocks and put job into Pending state.
        self.submit_transaction(job)

        # Unlikely that FB has completed the transaction at this point, but check while we're here.
        self.check_transaction_state(job)

    def submit_transaction(self, job):
        if job.status != FillJob.STATUS.NEW:
            logger.info(f'Job {job.id} is not in NEW state, skipping.')
            return

        try:
            logger.info(f'Submitting job {job.id}')
            raw_data = self.contracts.staking.encodeABI(fn_name="receiveFreedAVAX", args=[])

            tx = self.fb_client.external_contract_call(
                vault_account_id=VAULT_ACCOUNT,
                asset_id=ASSET_ID,
                external_contract_id=FB_CONTRACT_ID,
                amount=str(Web3.fromWei(job.amount_wei, 'ether')),
                data=raw_data,
                note="Fill contract deficit",
            )
            job.fireblocks_transaction_id = tx['id']
            job.submit()
            job.save()
        except Exception as e:
            logger.exception("Failed to submit fill transaction to fireblocks")
            raise e

    def check_transaction_state(self, job):
        if job.status != FillJob.STATUS.PENDING:
            logger.info(f'Job {job.id} is not in PENDING state, skipping.')
            return

        try:
            tx = self.fb_client.get_transaction_by_id(job.fireblocks_transaction_id)
            if tx['status'] == TRANSACTION_STATUS_COMPLETED:
                logger.info(f"Found completed transaction for job {job.id}")
                job.complete()
                job.save()
                return

            if tx['status'] == TRANSACTION_STATUS_FAILED:
                logger.warning(f"Found failed transaction for job {job.id}")
                job.fail()
                job.save()
                return

            logger.info(f"Transaction state is {tx['status']}, skipping.")

        except FireblocksApiException as e:
            logger.exception("Failed to load transaction by id")
            return
