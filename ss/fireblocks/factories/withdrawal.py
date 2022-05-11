import random
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from common.testing import generate_random_address

from ..models import VaultWithdrawal, WithdrawalJob
from .core import ExternalWalletAssetFactory, VaultAssetFactory
from .transaction import WithdrawalTransactionFactory


class VaultWithdrawalFactory(DjangoModelFactory):
    """
    This creates a brand new VaultWithdrawal, for which there is not yet a
    matching transaction.
    """

    class Meta:
        model = VaultWithdrawal

    class Params:
        asset_id = 'BTC_TEST'
        currency_code = 'XTN'

    wallet_asset = factory.SubFactory(ExternalWalletAssetFactory, asset__asset_id=factory.SelfAttribute('...asset_id'))
    amount = 0.001
    status = VaultWithdrawal.STATUS.NEW


class ConfirmedWithdrawalFactory(VaultWithdrawalFactory):
    status = VaultWithdrawal.STATUS.CONFIRMED

    # We have created a linked Transaction too
    transaction = factory.RelatedFactory(WithdrawalTransactionFactory, factory_related_name='withdrawal')


class WithdrawalJobFactory(DjangoModelFactory):

    class Meta:
        model = WithdrawalJob

    asset = factory.SubFactory(VaultAssetFactory, asset_id='AVAX')
    error = ''  # Error is only filled when job has failed
    withdrawal = None  # This field is only filled when the job is complete
    status = WithdrawalJob.STATUS.NEW

    @factory.lazy_attribute
    def address(self):
        return generate_random_address('AVAX')

    @factory.lazy_attribute
    def amount(self):
        return Decimal(random.random())


class SuccessfulWithdrawalJobFactory(DjangoModelFactory):

    class Meta:
        model = WithdrawalJob

    asset = factory.SubFactory(VaultAssetFactory, asset_id='AVAX')
    error = ''  # Error is only filled when job has failed
    withdrawal = factory.SubFactory(VaultWithdrawalFactory)
    status = WithdrawalJob.STATUS.SUCCESS

    @factory.lazy_attribute
    def address(self):
        return generate_random_address('AVAX')

    @factory.lazy_attribute
    def amount(self):
        return Decimal(random.random())
