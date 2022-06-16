from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from .models import AtomicTx, ChainSwap


class AtomicTxFactory(DjangoModelFactory):
    """
    Generates an AtomicTx model
    """

    class Meta:
        model = AtomicTx

    from_derivation_path = "44/1/0/0/0"
    from_address = '0xe5649e7ec3f3be043d9828db8be18f0eb3dea9b'
    to_derivation_path = "44/1/0/0/0"
    to_address = '0xe5649e7ec3f3b34d9828db8be18f0eb3dea9b'
    amount = Decimal('1.23456')
    description = 'Test atomic transaction'


class ChainSwapFactory(DjangoModelFactory):
    """
    Generates a ChainSwap model
    """

    class Meta:
        model = ChainSwap

    source_chain = 'P'
    export_tx = factory.SubFactory(AtomicTxFactory)
