import json
import os
from enum import Enum

from web3 import Web3

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from avalanche.web3 import AvaWeb3


class Contract(str, Enum):
    STAKING = 'Staking'
    ORACLE = 'Oracle'


class Contracts:

    def __init__(self):
        self.client = AvaWeb3()

        self.staking = self.client.web3.eth.contract(
            address=self.staking_address,
            abi=self.load_abi_file(contract_name=Contract.STAKING),
        )

        self.oracle = self.client.web3.eth.contract(
            address=self.oracle_address,
            abi=self.load_abi_file(contract_name=Contract.ORACLE),
        )

    @property
    def staking_address(self):
        if settings.CONTRACT_STAKING is None:
            raise ImproperlyConfigured('The CONTRACT_STAKING env var has not been set')
        return Web3.toChecksumAddress(settings.CONTRACT_STAKING)

    @property
    def oracle_address(self):
        if settings.CONTRACT_ORACLE is None:
            raise ImproperlyConfigured('The CONTRACT_ORACLE env var has not been set')
        return Web3.toChecksumAddress(settings.CONTRACT_ORACLE)

    def load_abi_file(self, contract_name: Contract):
        path = os.path.join(os.path.dirname(__file__), f'abis/{contract_name}.json')
        with open(path) as f:
            abi = f.read()
        return json.loads(abi)
