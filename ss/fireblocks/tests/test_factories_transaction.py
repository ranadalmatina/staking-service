from datetime import datetime

from common.testing import TestCase

from ..factories import ExternalWalletFactory, VaultAccountFactory
from ..factories.transaction import (DepositTransactionDataFactory, DepositTransactionFactory,
                                     WithdrawalTransactionDataFactory, WithdrawalTransactionFactory)
from ..models import Transaction


class TransactionTestCase(TestCase):
    """
    Deduplicate repeated tests
    """

    def assert_transaction_data_valid(self, data):
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['data'], dict)

        self.assert_is_valid_UUID(data['tx_id'])
        self.assertEqual(data['data']['id'], data['tx_id'])
        self.assertEqual(data['data']['assetId'], data['asset_id'])

        self.assert_is_iso_8601(data['created_at'])
        self.assert_is_timestamp(data['data']['createdAt'])

    def assert_transaction_valid(self, transaction):
        self.assertIsInstance(transaction, Transaction)
        self.assert_is_valid_UUID(transaction.tx_id)
        self.assert_is_valid_UUID(transaction.data['id'])
        self.assertEqual(transaction.tx_id, transaction.data['id'])

        self.assertEqual(transaction.asset_id, transaction.data['assetId'])

        self.assertIsInstance(transaction.created_at, datetime)
        self.assert_is_timestamp(transaction.data['createdAt'])


class TransactionDataFactoryTestCase(TransactionTestCase):

    def test_withdrawal_transaction_data_factory(self):
        data = WithdrawalTransactionDataFactory(asset_id='ETH')
        self.assert_transaction_data_valid(data)

        self.assertEqual(data['asset_id'], 'ETH')
        self.assertEqual(data['data']['destination'], {
            'id': '4b1a10c6-df9b-0840-a293-690169f70767',
            'name': 'trader 666 wallet 999', 'subType': 'External', 'type': 'EXTERNAL_WALLET'})

    def test_withdrawal_transaction_data_factory_external_wallet(self):
        external_wallet = ExternalWalletFactory(id=333, name='Amazing Wallet')
        data = WithdrawalTransactionDataFactory(external_wallet=external_wallet)
        self.assert_transaction_data_valid(data)

        self.assertEqual(data['asset_id'], 'BTC_TEST')
        self.assertEqual(data['data']['destination'], {
            'id': '333', 'name': 'Amazing Wallet', 'subType': 'External', 'type': 'EXTERNAL_WALLET'})

    def test_deposit_transaction_data_factory(self):
        data = DepositTransactionDataFactory(asset_id='ETH')
        self.assert_transaction_data_valid(data)

        self.assertEqual(data['asset_id'], 'ETH')
        self.assertEqual(data['data']['destination'], {
            'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_deposit_transaction_data_factory_vault_account(self):
        account = VaultAccountFactory(vault_id=666, name='Devil Vault Account')
        data = DepositTransactionDataFactory(vault_account=account)
        self.assert_transaction_data_valid(data)
        self.assertEqual(data['asset_id'], 'BTC_TEST')
        self.assertEqual(data['data']['destination'], {
            'id': '666', 'name': 'Devil Vault Account', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_data_factory(self):
        data = DepositTransactionDataFactory(asset_id='ETH', tx_id='d6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assert_transaction_data_valid(data)

        self.assertEqual(data['tx_id'], 'd6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertEqual(data['asset_id'], 'ETH')
        self.assertEqual(
            data['data']['destination'], {'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_data_factory_vault_account(self):
        vault_account = VaultAccountFactory(vault_id=333, name='Amazing Vault')
        data = DepositTransactionDataFactory(vault_account=vault_account, tx_id='42d959ed-38d2-4294-95d3-6b35093395ec')
        self.assert_transaction_data_valid(data)

        self.assertEqual(data['tx_id'], '42d959ed-38d2-4294-95d3-6b35093395ec')
        self.assertEqual(data['asset_id'], 'BTC_TEST')
        self.assertEqual(data['data']['destination'],
                         {'id': '333', 'name': 'Amazing Vault', 'type': 'VAULT_ACCOUNT', 'subType': ''})


class WithdrawalTransactionFactoryTestCase(TransactionTestCase):

    def test_transaction_factory_btc(self):
        transaction = WithdrawalTransactionFactory(asset_id='BTC')
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'BTC')
        self.assertEqual(transaction.destination_address, 'mjwrisAsZ5vZAeYGB4NXTAzCVJKGAS4XxL')
        self.assertEqual(transaction.destination, {
            'id': '4b1a10c6-df9b-0840-a293-690169f70767',
            'name': 'trader 666 wallet 999', 'subType': 'External', 'type': 'EXTERNAL_WALLET'})

    def test_transaction_factory_eth(self):
        transaction = WithdrawalTransactionFactory(asset_id='ETH_TEST')
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.destination_address, '0xc6256f4388d177f446A3AbEd9aB59021Dcc01565')
        self.assertEqual(transaction.destination, {
            'id': '4b1a10c6-df9b-0840-a293-690169f70767',
            'name': 'trader 666 wallet 999', 'subType': 'External', 'type': 'EXTERNAL_WALLET'})

    def test_transaction_factory_external_wallet(self):
        external_wallet = ExternalWalletFactory(id=666, name='Devil Wallet')
        transaction = WithdrawalTransactionFactory(external_wallet=external_wallet)
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.destination, {
            'id': '666',
            'name': 'Devil Wallet', 'subType': 'External', 'type': 'EXTERNAL_WALLET'})


class DepositTransactionFactoryTestCase(TransactionTestCase):

    def test_transaction_factory_btc(self):
        transaction = DepositTransactionFactory(asset_id='BTC')
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'BTC')
        self.assertEqual(transaction.destination_address, 'mjwrisAsZ5vZAeYGB4NXTAzCVJKGAS4XxL')
        self.assertEqual(transaction.destination, {
            'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_factory_eth(self):
        transaction = DepositTransactionFactory(asset_id='ETH_TEST')
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.destination_address, '0xc6256f4388d177f446A3AbEd9aB59021Dcc01565')
        self.assertEqual(transaction.destination, {
            'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_factory_vault_account(self):
        account = VaultAccountFactory(vault_id=666, name='Devil Vault Account')
        transaction = DepositTransactionFactory(vault_account=account)
        self.assert_transaction_valid(transaction)

        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.destination, {
            'id': '666', 'name': 'Devil Vault Account', 'type': 'VAULT_ACCOUNT', 'subType': ''})


class TransactionFactoryTestCase(TestCase):

    def test_transaction_factory_btc(self):
        transaction = DepositTransactionFactory(asset_id='BTC', tx_id='42d959ed-38d2-4294-95d3-6b35093395ec')
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.tx_id, '42d959ed-38d2-4294-95d3-6b35093395ec')
        self.assertEqual(transaction.data['id'], '42d959ed-38d2-4294-95d3-6b35093395ec')
        self.assertEqual(transaction.asset_id, 'BTC')
        self.assertEqual(transaction.data['assetId'], 'BTC')
        self.assertEqual(transaction.destination_address, 'mjwrisAsZ5vZAeYGB4NXTAzCVJKGAS4XxL')
        self.assertEqual(
            transaction.destination, {'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_factory_eth(self):
        transaction = DepositTransactionFactory(asset_id='ETH_TEST', tx_id='d6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.tx_id, 'd6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertEqual(transaction.data['id'], 'd6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.data['assetId'], 'ETH_TEST')
        self.assertEqual(transaction.destination_address, '0xc6256f4388d177f446A3AbEd9aB59021Dcc01565')
        self.assertEqual(
            transaction.destination, {'id': '0', 'name': 'Default', 'type': 'VAULT_ACCOUNT', 'subType': ''})

    def test_transaction_factory_vault_account(self):
        vault_account = VaultAccountFactory(vault_id=666, name='Devil Vault')
        transaction = DepositTransactionFactory(vault_account=vault_account,
                                                tx_id='d6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.tx_id, 'd6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertEqual(transaction.data['id'], 'd6a7f7c7-13d3-4c31-b2e4-9c5b698d9243')
        self.assertEqual(transaction.asset_id, 'ETH_TEST')
        self.assertEqual(transaction.data['assetId'], 'ETH_TEST')
        self.assertEqual(
            transaction.destination, {'id': '666', 'name': 'Devil Vault', 'type': 'VAULT_ACCOUNT', 'subType': ''})
