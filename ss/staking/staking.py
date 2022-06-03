import logging
import random
from django.conf import settings
from web3 import Web3
from avalanche.api import AvalancheClient

logger = logging.Logger(__file__)


class Staking:

    def run_staking(self):
        # TODO: Check if any existing staking txs are still pending and don't run this if so.

        # TODO: Check p-chain wallet balance. If over threshold, start staking process.
        balance = Web3.toWei(0.001, 'ether')

        # TODO: Maintain allowlist of validators to stake with

        # Load validator data
        self.client = AvalancheClient(RPC_URL=settings.AVAX_RPC_URL)
        validators = self.client.platform_get_current_validators()
        print([v.free_space for v in validators])

        # For now, just shove everything on one node.
        # TODO: We need to break this up across multiple nodes for large stakes
        with_min_space = [v for v in validators if v.free_space > balance]

        if len(with_min_space) == 0:
            logger.warning('No validators with enough space to stake')
            return

        validator = random.choice(with_min_space)

        # TODO: Create a staking transaction
        logger.info(f'Staking {balance} AVAX on {validator.node_id}')
        return
