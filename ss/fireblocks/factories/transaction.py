from datetime import datetime
from uuid import uuid4

import arrow
import factory
from factory.django import DjangoModelFactory

from django.utils import timezone

from ..models import Transaction


def convert_to_timestamp(to_convert: datetime) -> int:
    """
    Converts a datetime to a Fireblocks format timestamp.
    """
    return int(datetime.timestamp(to_convert) * 1000)


class TransactionFactory(DjangoModelFactory):

    class Meta:
        model = Transaction
        exclude = ('source', 'destination', 'destination_address', 'tx_hash')

    class Params:
        status = 'COMPLETED'
        amount = '1'
        last_updated = 1583858111079

    asset_id = 'ETH_TEST'
    deposit = None
    withdrawal = None
    destination = {}

    @factory.lazy_attribute
    def created_at(self):
        return timezone.now()

    @factory.lazy_attribute
    def tx_id(self):
        return str(uuid4())

    @factory.lazy_attribute
    def source(self):
        return {'id': '', 'name': 'External', 'type': 'UNKNOWN', 'subType': ''}

    @factory.lazy_attribute
    def destination_address(self):
        if 'ETH' in self.asset_id:
            return '0xc6256f4388d177f446A3AbEd9aB59021Dcc01565'
        return 'mjwrisAsZ5vZAeYGB4NXTAzCVJKGAS4XxL'

    @factory.lazy_attribute
    def tx_hash(self):
        if 'ETH' in self.asset_id:
            return '0xc6545156c472d12bc3bba84582e2c415d5b52e959ec27800d2996a1d1d7f2fed'
        return '179aaa4a9b0d71cbbff2b8caacf445f42f28af43fd2441c001e67c8375efd6c5'

    @factory.lazy_attribute
    def data(self):
        return {
            'id': self.tx_id,
            'fee': 4.2e-05,
            'note': '',
            'amount': self.amount,
            'source': self.source,
            'status': self.status,
            'txHash': self.tx_hash,
            'assetId': self.asset_id,
            'signedBy': [],
            'createdAt': convert_to_timestamp(self.created_at),
            'createdBy': '',
            'netAmount': 1,
            'operation': 'TRANSFER',
            'subStatus': 'CONFIRMED',
            'networkFee': 4.2e-05,
            'rejectedBy': '',
            'addressType': '',
            'destination': self.destination,
            'feeCurrency': self.asset_id,
            'lastUpdated': self.last_updated,
            'exchangeTxId': '',
            'destinationTag': '',
            'requestedAmount': 1,
            'destinationAddress': self.destination_address,
            'destinationAddressDescription': '3253926033128177663',
        }


class DepositTransactionFactory(TransactionFactory):
    class Params:
        vault_account = None

    @factory.lazy_attribute
    def destination(self):
        name = 'Default'
        id_ = '0'
        if self.vault_account is not None:
            name = str(self.vault_account.name)
            id_ = str(self.vault_account.vault_id)
        return {'id': id_, 'name': name, 'type': 'VAULT_ACCOUNT', 'subType': ''}


class WithdrawalTransactionFactory(TransactionFactory):
    class Params:
        external_wallet = None

    @factory.lazy_attribute
    def destination(self):
        id_ = '4b1a10c6-df9b-0840-a293-690169f70767'
        name = 'trader 666 wallet 999'
        if self.external_wallet is not None:
            id_ = str(self.external_wallet.id)
            name = str(self.external_wallet.name)
        return {'id': id_, 'name': name, 'type': 'EXTERNAL_WALLET', 'subType': 'External'}


class TransactionDataFactory(factory.DictFactory):

    class Meta:
        abstract = True
        exclude = ('source', 'destination', 'destination_address', 'tx_hash')

    class Params:
        vault_account = None
        status = 'COMPLETED'
        amount = 5.001
        last_updated = 1589554716087

    asset_id = 'BTC_TEST'

    @factory.lazy_attribute
    def created_at(self):
        return arrow.utcnow().isoformat()

    @factory.lazy_attribute
    def data(self):
        return {
            'id': self.tx_id,
            'fee': 1.68e-06,
            'note': '',
            'amount': self.amount,
            'source': self.source,
            'status': self.status,
            'txHash': self.tx_hash,
            'assetId': self.asset_id,
            'signedBy': [],
            'createdAt': 1589554675000,
            'createdBy': '',
            'netAmount': 0.001,
            'operation': 'TRANSFER',
            'subStatus': 'CONFIRMED',
            'networkFee': 1.68e-06,
            'rejectedBy': '',
            'addressType': '',
            'destination': self.destination,
            'feeCurrency': self.asset_id,
            'lastUpdated': self.last_updated,
            'exchangeTxId': '',
            'destinationTag': '',
            'requestedAmount': 0.001,
            'destinationAddress': self.destination_address,
            'destinationAddressDescription': '11 deposit',
        }


class DepositTransactionDataFactory(TransactionDataFactory, DepositTransactionFactory):
    pass


class WithdrawalTransactionDataFactory(TransactionDataFactory, WithdrawalTransactionFactory):
    pass
