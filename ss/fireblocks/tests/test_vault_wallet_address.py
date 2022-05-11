from django.db import IntegrityError
from django.test import TestCase

from common.testing import generate_random_address
from fireblocks.factories import FireblocksWalletFactory, VaultAssetFactory, VaultWalletAddressFactory


class VaultWalletAddressTestCase(TestCase):

    def test_unique_address(self):
        btc_test = VaultAssetFactory(asset_id='BTC_TEST')
        wallet = FireblocksWalletFactory(asset=btc_test)

        address = generate_random_address(currency_code='AVAX')
        VaultWalletAddressFactory(wallet=wallet, address=address)
        # Should be unable to create a duplicate address
        with self.assertRaises(IntegrityError):
            VaultWalletAddressFactory(wallet=wallet, address=address)
