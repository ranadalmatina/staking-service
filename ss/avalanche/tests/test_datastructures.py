from hexbytes import HexBytes
from django.test import TestCase
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.evm import EVMExportTx
from avalanche.datastructures.platform import PlatformImportTx


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
