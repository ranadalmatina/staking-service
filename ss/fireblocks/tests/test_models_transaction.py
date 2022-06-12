from django.db import IntegrityError
from django.test import TestCase

from fireblocks.factories import (FireblocksWalletFactory, VaultAccountFactory, VaultAssetFactory,
                                  VaultWalletAddressFactory)

from ..factories.transaction import DepositTransactionFactory


class TransactionTestCase(TestCase):

    def test_unique_tx_id(self):
        DepositTransactionFactory(asset_id='BTC_TEST', tx_id='016c6dbf-4c96-4381-90c9-19a940bce4a0')
        # Should be unable to create a transaction with duplicate ID
        with self.assertRaises(IntegrityError):
            DepositTransactionFactory(asset_id='ETH_TEST', tx_id='016c6dbf-4c96-4381-90c9-19a940bce4a0')

    def test_destination_vault_account(self):
        account = VaultAccountFactory(vault_id=435)
        destination = {'id': account.vault_id, 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''}
        tx = DepositTransactionFactory(asset_id='DASH', destination=destination)
        self.assertEqual(tx.destination_vault_account, account.vault_id)

    def test_get_vault_account(self):
        account = VaultAccountFactory(vault_id=999)
        destination = {'id': account.vault_id, 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''}
        tx = DepositTransactionFactory(asset_id='BTC_TEST', destination=destination)
        account.refresh_from_db()
        self.assertEqual(tx.get_vault_account(), account)

    def test_get_vault_asset(self):
        btc = VaultAssetFactory(asset_id='BTC')
        tx = DepositTransactionFactory(asset_id=btc.asset_id)
        self.assertEqual(tx.get_vault_asset(), btc)

    def test_get_fireblocks_wallet(self):
        vault_account = VaultAccountFactory(vault_id=26)
        btc_test = VaultAssetFactory(asset_id='BTC_TEST')
        wallet = FireblocksWalletFactory(asset=btc_test, vault_account=vault_account)

        destination = {'id': vault_account.vault_id, 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''}
        tx = DepositTransactionFactory(asset_id=btc_test.asset_id, destination=destination)
        self.assertEqual(tx.get_fireblocks_wallet(), wallet)

    def test_get_vault_wallet_address(self):
        vault_account = VaultAccountFactory(vault_id=-5)
        eth = VaultAssetFactory(asset_id='ETH')
        wallet = FireblocksWalletFactory(asset=eth, vault_account=vault_account)
        address = VaultWalletAddressFactory(wallet=wallet)

        destination = {'id': vault_account.vault_id, 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''}
        tx = DepositTransactionFactory(asset_id=eth.asset_id, destination=destination,
                                       destination_address=address.address)
        self.assertEqual(tx.get_vault_wallet_address(), address)
