import uuid
from django.db import models
from extended_choices import Choices
from django_fsm import FSMField, transition
from fireblocks.models import Transaction


class FillJob(models.Model):
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
    amount_wei = models.DecimalField(max_digits=30, decimal_places=0, help_text='Amount of the transaction, in WEI.')

    fireblocks_transaction_id = models.UUIDField(null=True, help_text='Fireblocks transaction ID.')

    @transition(field=status, source=STATUS.NEW, target=STATUS.PENDING)
    def submit(self):
        pass

    @transition(field=status, source=STATUS.PENDING, target=STATUS.COMPLETED)
    def complete(self):
        pass

    @transition(field=status, source=STATUS.PENDING, target=STATUS.FAILED)
    def fail(self):
        pass
