from uuid import uuid4

import factory
from factory.django import DjangoModelFactory

from common.testing import generate_random_address

from ..models import (ExternalWallet, ExternalWalletAsset, FireblocksWallet, VaultAccount, VaultAsset,
                      VaultWalletAddress)


class VaultAccountFactory(DjangoModelFactory):
    """
    Generates a VaultAccount model
    """

    class Meta:
        model = VaultAccount
        django_get_or_create = ('vault_id',)

    vault_id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda obj: f'Vault_{obj.vault_id}')
    customer_ref_id = ''


class VaultAssetFactory(DjangoModelFactory):

    class Meta:
        model = VaultAsset
        django_get_or_create = ('asset_id',)

    asset_id = factory.Iterator(['BTC', 'ETH', 'BTC_TEST', 'ETH_TEST', 'DASH'])

    @factory.lazy_attribute
    def is_erc_20(self):
        # Quick and dirty way to test right now
        return 'ETH' in self.asset_id


class FireblocksWalletFactory(DjangoModelFactory):

    class Meta:
        model = FireblocksWallet

    vault_account = factory.SubFactory(VaultAccountFactory)
    asset = factory.SubFactory(VaultAssetFactory)


class ExternalWalletFactory(DjangoModelFactory):

    class Meta:
        model = ExternalWallet

    id = factory.LazyFunction(uuid4)


class ExternalWalletAssetFactory(DjangoModelFactory):

    class Meta:
        model = ExternalWalletAsset

    id = factory.LazyFunction(uuid4)
    wallet = factory.SubFactory(ExternalWalletFactory)
    asset = factory.SubFactory(VaultAssetFactory)

    @factory.lazy_attribute
    def address(self):
        return generate_random_address('AVAX')

    status = ExternalWalletAsset.STATUS.APPROVED
    tag = ''


class VaultWalletAddressFactory(DjangoModelFactory):

    class Meta:
        model = VaultWalletAddress

    wallet = factory.SubFactory(FireblocksWalletFactory)

    @factory.lazy_attribute
    def address(self):
        return generate_random_address('AVAX')
