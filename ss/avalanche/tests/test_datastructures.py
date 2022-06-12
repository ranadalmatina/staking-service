import json
import time
from unittest import mock

from hexbytes import HexBytes
from web3 import Web3
from web3.types import Wei

from django.test import TestCase

from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.evm import EVMExportTx, EVMImportTx
from avalanche.datastructures.platform import Delegator, PlatformExportTx, PlatformImportTx, Validator


class DataStructureTestCase(TestCase):

    def test_unsigned_cchain_export_from_bytes(self):
        data = HexBytes("0x000000000001000000057fc93d85c6d62c5b2ac0b519c87010ea5294012d1e407030d6acd0021cac10d500000"
                        "000000000000000000000000000000000000000000000000000000000000000000137925525b620412183d4d8f7"
                        "1e6f64b5e64420c4000000003baf67193d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f61b"
                        "be2aa0000000000000004000000013d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f61bbe2"
                        "aa00000007000000003baa0c4000000000000000000000000100000001e5649e7ec3f3be0117d9828db8be18f0e"
                        "b3dea9b")
        tx = UnsignedTransaction.from_bytes(raw=data)
        self.assertEqual(tx.codec_id.hex(), "0000")
        self.assertIsInstance(tx.atomic_tx, EVMExportTx)
        self.assertEqual(tx.hash().hex(), "edd9b102c0113997e9f00fdca4e0b1446ac98aa1ef81f06b6266b68f2c3d778e")

    def test_unsigned_pchain_import_from_bytes(self):
        data = HexBytes("0x00000000001100000005000000000000000000000000000000000000000000000000000000000000000000000"
                        "0013d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f61bbe2aa00000007000000003b9aca00"
                        "00000000000000000000000100000001e5649e7ec3f3be0117d9828db8be18f0eb3dea9b000000000000001e464"
                        "220502d436861696e20696d706f72742066726f6d20432d436861696e7fc93d85c6d62c5b2ac0b519c87010ea52"
                        "94012d1e407030d6acd0021cac10d5000000011a3de5b01ce23aca1cb2b6cfe352a2ead685dfad1d86844bb935d"
                        "c5a74b0cd2c000000003d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f61bbe2aa00000005"
                        "000000003baa0c400000000100000000")
        tx = UnsignedTransaction.from_bytes(raw=data)
        self.assertEqual(tx.codec_id.hex(), "0000")
        self.assertIsInstance(tx.atomic_tx, PlatformImportTx)
        self.assertEqual(tx.hash().hex(), "a9d054465f2acd1c3a6deaaa27ba66927110d483205036d606232ac2eac85280")

    def test_unsigned_pchain_export_from_bytes(self):
        data = HexBytes("0x00000000001200000005000000000000000000000000000000000000000000000000000000000000000000000"
                        "00000000002b17d5b96f75198af0a0347588b3305978667baa3629894085e42045074c76782000000003d9bdac0"
                        "ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f61bbe2aa00000005000000003b9aca0000000001000"
                        "00000823904f704522e7ab5e4c161d0e02e089b0383600ba28836aba44e4cacca08c2000000003d9bdac0ed1d76"
                        "1330cf680efdeb1a42159eb387d6d2950c96f7d28f61bbe2aa00000005000000003b9aca0000000001000000000"
                        "000001c464220502d436861696e206578706f727420746f20432d436861696e7fc93d85c6d62c5b2ac0b519c870"
                        "10ea5294012d1e407030d6acd0021cac10d5000000013d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950"
                        "c96f7d28f61bbe2aa00000007000000003b8b87c000000000000000000000000100000001e5649e7ec3f3be0117"
                        "d9828db8be18f0eb3dea9b")
        tx = UnsignedTransaction.from_bytes(raw=data)
        self.assertEqual(tx.codec_id.hex(), "0000")
        self.assertIsInstance(tx.atomic_tx, PlatformExportTx)
        self.assertEqual(tx.hash().hex(), "03868278ef00c9bd44907f7ea6c66c5741b850fb6a4adfba480c5ba4678a2859")

    def test_unsigned_cchain_import_from_bytes(self):
        data = HexBytes("0x000000000000000000057fc93d85c6d62c5b2ac0b519c87010ea5294012d1e407030d6acd0021cac10d50000"
                        "00000000000000000000000000000000000000000000000000000000000000000001339ec139e45e76295ba81c6"
                        "054ca4b9cc16ec6b0f02158bea5caf982ad4fad52000000003d9bdac0ed1d761330cf680efdeb1a42159eb387d6"
                        "d2950c96f7d28f61bbe2aa00000005000000003b8b87c000000001000000000000000137925525b620412183d4d"
                        "8f71e6f64b5e64420c4000000003b862ce73d9bdac0ed1d761330cf680efdeb1a42159eb387d6d2950c96f7d28f"
                        "61bbe2aa")
        tx = UnsignedTransaction.from_bytes(raw=data)
        self.assertEqual(tx.codec_id.hex(), "0000")
        self.assertIsInstance(tx.atomic_tx, EVMImportTx)
        self.assertEqual(tx.hash().hex(), "9cbf5e59ab703fb847089a044a36bfa48425c8e47492f5f98e5d1b179b2f220e")

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
