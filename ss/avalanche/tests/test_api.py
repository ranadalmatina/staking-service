import json
import time
from unittest import mock

from web3 import Web3
from web3.types import Wei

from django.test import TestCase

from ..api.validator import Delegator, Validator


class APITestCase(TestCase):

    def test_deserialise_validators(self):
        data = json.loads("""
      {
        "txID": "2NNkpYTGfTFLSGXJcHtVv6drwVU2cczhmjK2uhvwDyxwsjzZMm",
        "startTime": "1600368632",
        "endTime": "1602960455",
        "stakeAmount": "2000000000000",
        "nodeID": "NodeID-5mb46qkSBj81k9g9e4VFjGGSbaaSLFRzD",
        "rewardOwner": {
          "locktime": "0",
          "threshold": "1",
          "addresses": ["P-avax18jma8ppw3nhx5r4ap8clazz0dps7rv5u00z96u"]
        },
        "potentialReward": "117431493426",
        "delegationFee": "10.0000",
        "uptime": "0.0000",
        "connected": false,
        "delegators": [
          {
            "txID": "Bbai8nzGVcyn2VmeYcbS74zfjJLjDacGNVuzuvAQkHn1uWfoV",
            "startTime": "1600368523",
            "endTime": "1602960342",
            "stakeAmount": "25000000000",
            "nodeID": "NodeID-5mb46qkSBj81k9g9e4VFjGGSbaaSLFRzD",
            "rewardOwner": {
              "locktime": "0",
              "threshold": "1",
              "addresses": ["P-avax18jma8ppw3nhx5r4ap8clazz0dps7rv5u00z96u"]
            },
            "potentialReward": "11743144774"
          }
        ]
      }
        """)
        validator = Validator.from_json(data)
        self.assertEqual(validator.start_time, 1600368632)
        self.assertEqual(validator.end_time, 1602960455)
        self.assertEqual(validator.stake, Wei(2000000000000))
        self.assertEqual(validator.node_id, "NodeID-5mb46qkSBj81k9g9e4VFjGGSbaaSLFRzD")

        self.assertTrue(len(validator.delegators), 1)
        delegator = validator.delegators[0]
        self.assertEqual(delegator.amount, Wei(25000000000))

    def test_validator_free_space(self):
        empty = Validator("foo", 0, Web3.toWei(100, "ether"), 0, 0, [])
        self.assertEqual(empty.free_space, Web3.toWei(400, "ether"))

        delegators = [Delegator(Web3.toWei(1, "ether")) for _ in range(10)]
        val = Validator("foo", 0, Web3.toWei(100, "ether"), 0, 0, delegators)
        self.assertEqual(val.free_space, Web3.toWei(390, "ether"))

    @mock.patch('time.time', mock.MagicMock(return_value=1500000000))
    def test_validator_remaining_time(self):
        one_year = 60 * 60 * 24 * 365
        validator = Validator("foo", 0, Web3.toWei(0, "ether"), 1, time.time() + one_year, [])
        self.assertEqual(validator.remaining_time, one_year)
