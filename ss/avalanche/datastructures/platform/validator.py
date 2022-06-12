import time
from decimal import Decimal

from web3 import Web3
from web3.types import Wei


class Delegator:

    def __init__(self, amount: Wei):
        self.amount = amount


class Validator:

    def __init__(self, node_id, uptime: float, stake: Wei, start_time: int, end_time: int, delegators: list[Delegator]):
        self.node_id = node_id
        self.uptime = uptime
        self.stake = stake
        self.start_time = start_time
        self.end_time = end_time
        self.delegators = delegators

    @staticmethod
    def from_json(json_data: dict):
        raw_delegators = json_data['delegators'] if json_data['delegators'] else []
        delegators = [Delegator(Web3.toWei(delegator['stakeAmount'], 'wei')) for delegator in raw_delegators]
        return Validator(
            json_data['nodeID'],
            float(json_data['uptime']),
            Web3.toWei(json_data['stakeAmount'], 'wei'),
            int(json_data['startTime']),
            int(json_data['endTime']),
            delegators,
        )

    @property
    def free_space(self) -> Decimal:
        delegated = sum(delegator.amount for delegator in self.delegators)
        return Decimal(self.stake * 4 - delegated)

    @property
    def remaining_time(self) -> int:
        return self.end_time - int(round(time.time()))
