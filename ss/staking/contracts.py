import os
import json


from enum import Enum
from django.conf import settings
from avalanche.web3 import AvaWeb3


class Contract(str, Enum):
    STAKING = 'Staking'
    ORACLE = 'Oracle'


class Contracts:

    def __init__(self):
        self.client = AvaWeb3(RPC_URL=settings.AVAX_RPC_URL)

        self.staking = self.client.web3.eth.contract(
            address=settings.CONTRACT_STAKING,
            abi=self.load_abi_file(contract_name=Contract.STAKING),
        )

        self.oracle = self.client.web3.eth.contract(
            address=settings.CONTRACT_ORACLE,
            abi=self.load_abi_file(contract_name=Contract.ORACLE),
        )

    def load_abi_file(self, contract_name: Contract):
        path = os.path.join(os.path.dirname(__file__),
                            f'abis/{contract_name}.json')
        with open(path) as f:
            abi = f.read()
        return json.loads(abi)
