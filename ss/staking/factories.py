from decimal import Decimal
from factory.django import DjangoModelFactory

from .models import FillJob


class FillJobFactory(DjangoModelFactory):
    """
    Generates a FillJob model
    """

    class Meta:
        model = FillJob

    amount = Decimal('1.23456')
    fireblocks_transaction_id = None
