from hexbytes import HexBytes
from django.test import TestCase
from avalanche.bech32 import bech32_address_from_public_key, address_from_public_key
from common.bip.bip44_coins import Bip44Coins
from common.bip.bip32 import eth_address_from_public_key

class AddressDerivationTestCase(TestCase):

    def test_default_address_derivation_cchain(self):
        pub_key = HexBytes('03e41e35a559e169f80f5241c518580e15cfc7f497d4ab3e580ff4e6c03b2f5219')
        addr = address_from_public_key(pub_key, Bip44Coins.FB_C_CHAIN)
        self.assertEqual(addr, '0xb50a61Ca779487fC19aCcA5c7e5d61B547AB710a')

    def test_eth_address_derivation(self):
        pub_key = HexBytes('03e41e35a559e169f80f5241c518580e15cfc7f497d4ab3e580ff4e6c03b2f5219')
        addr = eth_address_from_public_key(pub_key)
        self.assertEqual(addr, '0xb50a61Ca779487fC19aCcA5c7e5d61B547AB710a')

    def test_bech32_address_derivation(self):
        pub_key = HexBytes('03e41e35a559e169f80f5241c518580e15cfc7f497d4ab3e580ff4e6c03b2f5219')
        addr = bech32_address_from_public_key(pub_key, Bip44Coins.FB_C_CHAIN)
        self.assertEqual(addr, 'C-fuji1p57arzes0y609q57fu4gtwd8ervwfy0nzdrlu2')
