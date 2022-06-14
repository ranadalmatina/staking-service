import uuid
from decimal import Decimal

from django_fsm import FSMField, transition
from extended_choices import Choices
from web3 import Web3
from web3.types import Wei

from django.db import models

from common.constants import MAX_DEC_PLACES
from common.validators import validate_positive


class FillJob(models.Model):
    """
    An object representing refilling the contract from the staking pool.
    """

    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('PENDING', 'pending', 'Pending'),
        ('COMPLETED', 'completed', 'Completed'),
        ('FAILED', 'failed', 'Failed'),
    )

    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)

    created_date = models.DateTimeField(auto_now_add=True, help_text='Transaction creation date in SS.')
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=30, decimal_places=MAX_DEC_PLACES, validators=[validate_positive],
                                 help_text="Amount in AVAX")

    fireblocks_transaction_id = models.UUIDField(null=True, help_text='Fireblocks transaction ID.')

    @property
    def amount_wei(self) -> Wei:
        return Web3.toWei(self.amount, 'ether')

    @amount_wei.setter
    def amount_wei(self, value: Wei):
        self.amount = Decimal(Web3.fromWei(value, 'ether'))


    @transition(field=status, source=STATUS.NEW, target=STATUS.PENDING)
    def submit(self):
        pass

    @transition(field=status, source=STATUS.PENDING, target=STATUS.COMPLETED)
    def complete(self):
        pass

    @transition(field=status, source=STATUS.PENDING, target=STATUS.FAILED)
    def fail(self):
        pass
