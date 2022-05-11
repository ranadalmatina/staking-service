import factory
from factory.django import DjangoModelFactory

from ..models import VaultDeposit
from .core import VaultWalletAddressFactory
from .transaction import DepositTransactionFactory


class VaultDepositFactory(DjangoModelFactory):
    """
    This creates a brand new deposit, for which there is not yet a
    matching transaction.
    """

    class Meta:
        model = VaultDeposit

    class Params:
        asset_id = 'BTC_TEST'

    address = factory.SubFactory(VaultWalletAddressFactory,
                                 wallet__asset__asset_id=factory.SelfAttribute('....asset_id'))
    status = VaultDeposit.STATUS.NEW


class SuccessfulDepositFactory(VaultDepositFactory):
    """
    This creates a VaultDeposit with a matching transaction.
    """
    status = VaultDeposit.STATUS.CONFIRMED

    # Successful VaultDeposits have a linked Transaction
    transaction = factory.RelatedFactory(DepositTransactionFactory, factory_related_name='deposit')
