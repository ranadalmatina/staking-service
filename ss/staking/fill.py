import logging
import traceback

from django.conf import settings
from web3 import Web3
from web3.types import Wei
from .models import FillJob
from staking.graphql import GraphAPI
from staking.contracts import Contracts
from fireblocks.models import Transaction
from fireblocks.client import get_fireblocks_client

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
        pass

    def run_fill(self, amount_override: Wei = None):

        # Check if ongoing fill is happening.
        jobs = FillJob.objects.filter(status__in=pending_states)
        if len(jobs) > 0:
            if jobs[0].status == FillJob.STATUS.NEW:
                logger.info(f'Found non-executed job, submitting transaciton.')
                self.submit_transaction(jobs[0])
                return

            logger.info(f'Found {len(jobs)} pending jobs, skipping.')
            return

        # Compute deficit
        graphapi = GraphAPI(settings.GRAPHQL_URL)
        deficit = graphapi.contract_avax_deficit() if not amount_override else amount_override
        logger.info(f'Contract deficit: {deficit}')

        # Check we have enough balance to make the tx.
        # TODO: Handle fees
        balance = self.fb_client.available_balance_wei(VAULT_ACCOUNT, ASSET_ID)
        if balance < deficit:
            logger.info(f'Custody balance {balance} is below deficit of {deficit}')
            return

        # Create a new job if there's a deficit.
        if deficit == 0:
            logger.info(f'No deficit, not creating a new job')
            return

        logger.info(f'Found deficit of {deficit} AVAX')
        job = FillJob.objects.create(
            status=FillJob.STATUS.NEW,
            amount_wei=deficit,
        )
        job.save()

        # Send transaction to fireblocks and put job into Pending state.
        self.submit_transaction(job)

        # TODO:
        # - Check if transaction was successful
        # - If not, mark job as failed
        # - If yes, mark job as completed

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
            logger.error(e)
            traceback.print_tb(e.__traceback__)
            raise e
