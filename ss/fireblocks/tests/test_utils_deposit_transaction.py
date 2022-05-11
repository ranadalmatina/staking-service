from django.test import TestCase

from ..factories import (VaultAccountFactory, FireblocksWalletFactory, VaultAssetFactory, VaultDepositFactory,
                         VaultWalletAddressFactory)
from ..factories.transaction import DepositTransactionFactory
from ..models import VaultDeposit
from ..utils.deposit import get_or_create_deposit


# TODO we need positive and NEGATIVE tests for this call
class DepositTransactionUtilsTestCase(TestCase):

    def test_get_or_create_deposit_no_object_exists(self):
        asset = VaultAssetFactory(asset_id='BTC')
        vault_account = VaultAccountFactory()
        wallet = FireblocksWalletFactory(vault_account=vault_account, asset=asset)
        address = VaultWalletAddressFactory(wallet=wallet)

        # This vault account link is what allows us to link to an existing deposit
        tx = DepositTransactionFactory(asset_id='BTC', vault_account=vault_account,
                                       destination_address=address.address)
        self.assertEqual(VaultDeposit.objects.count(), 0)
        new_deposit = get_or_create_deposit(transaction=tx)
        self.assertEqual(VaultDeposit.objects.count(), 1)
        self.assertEqual(new_deposit.address, address)

    def test_get_or_create_deposit_existing_deposit(self):
        asset = VaultAssetFactory(asset_id='BTC')
        vault_account = VaultAccountFactory()
        wallet = FireblocksWalletFactory(vault_account=vault_account, asset=asset)
        address = VaultWalletAddressFactory(wallet=wallet)

        existing_deposit = VaultDepositFactory(address=address)
        # Deposit is new and not linked to a transaction
        self.assertEqual(existing_deposit.status, VaultDeposit.STATUS.NEW)

        # This vault account link is what allows us to link to an existing deposit
        tx = DepositTransactionFactory(asset_id='BTC', vault_account=vault_account,
                                       destination_address=address.address)
        self.assertEqual(VaultDeposit.objects.count(), 1)
        new_deposit = get_or_create_deposit(transaction=tx)
        self.assertEqual(VaultDeposit.objects.count(), 1)
        self.assertEqual(new_deposit.address, address)
        self.assertEqual(existing_deposit.id, new_deposit.id)
