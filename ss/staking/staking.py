import logging
import random

from web3 import Web3

from django.conf import settings

from avalanche.api import AvalancheClient

logger = logging.Logger(__file__)


class Staking:

    def run_staking(self):
        # TODO: Check if any existing staking txs are still pending and don't run this if so.

        # TODO: Check p-chain wallet balance. If over threshold, start staking process.
        balance = Web3.toWei(0.001, 'ether')

        # TODO: Maintain allowlist of validators to stake with
        min_uptime = 0.9
        min_staking_period = 14 * 24 * 60 * 60  # seconds

        # Load validator data
        self.client = AvalancheClient(RPC_URL=settings.AVAX_RPC_URL)
        validators = self.client.platform_get_current_validators()
        print([v.free_space for v in validators])

        # For now, just shove everything on one node.
        # TODO: We need to break this up across multiple nodes for large stakes
        filtered = []
        for v in validators:
            if v.free_space < balance:
                continue
            if v.remaining_time < min_staking_period:
                continue
            if v.uptime < min_uptime:
                continue
            filtered.append(v)

        if len(filtered) == 0:
            logger.warning('No validators found that meet our minimum requirements')
            return

        validator = random.choice(filtered)

        # TODO: Create a staking transaction
        logger.info(f'Staking {balance} AVAX on {validator.node_id}')
        return
