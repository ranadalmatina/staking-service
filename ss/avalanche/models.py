import logging
import uuid
from django.db import models
from django_fsm import FSMField, transition
from extended_choices import Choices

from common.validators import validate_positive
from avalanche.base58 import Base58Decoder
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.types import AtomicTx as AtomicTxType

logger = logging.getLogger(__name__)


MAX_DEC_PLACES = 18


class AtomicTx(models.Model):
    """
    An export or import transaction on the avalanche network.
    """
    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('SUBMITTED', 'submitted', 'Submitted'),
        ('AWAITING_SIGNATURE', 'awaiting_signature', 'Awaiting signature'),
        ('SIGNED', 'signed', 'Signed'),
        ('BROADCAST', 'broadcast', 'Broadcast'),
        ('CONFIRMED', 'confirmed', 'Confirmed'),
        ('CANCELLED', 'cancelled', 'Cancelled'),
        ('REJECTED', 'rejected', 'Rejected'),
        ('FAILED', 'failed', 'Failed'),
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    from_derivation_path = models.TextField(help_text="Derivation path for from address")
    from_address = models.TextField()
    to_derivation_path = models.TextField(help_text="Derivation path for to address")
    to_address = models.TextField()
    amount = models.DecimalField(max_digits=30, decimal_places=MAX_DEC_PLACES, validators=[validate_positive],
                                 help_text="Amount in AVAX")
    description = models.TextField()

    unsigned_transaction = models.TextField(blank=True, help_text="Base58 encoded unsigned transaction")
    fireblocks_tx_id = models.TextField(blank=True)

    signed_transaction = models.TextField(blank=True, help_text="Base58 encoded signed transaction")
    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)
    avalanche_tx_id = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'AtomicTx({self.id})'

    def get_unsigned_transaction(self) -> UnsignedTransaction:
        data = Base58Decoder.CheckDecode(str(self.unsigned_transaction))
        return UnsignedTransaction.from_bytes(data)

    def get_atomic_transaction(self) -> AtomicTxType:
        return self.get_unsigned_transaction().atomic_tx

    @transition(field=status, source=STATUS.NEW, target=STATUS.SUBMITTED)
    def submit(self):
        pass

    @transition(field=status, source=STATUS.SUBMITTED, target=STATUS.NEW)
    def resubmit(self):
        # TODO testing only. Remove later
        pass

    @transition(field=status, source=STATUS.SUBMITTED, target=STATUS.AWAITING_SIGNATURE)
    def queue(self):
        pass

    @transition(field=status, source=STATUS.AWAITING_SIGNATURE, target=STATUS.SIGNED)
    def sign(self):
        pass

    @transition(field=status, source=STATUS.SIGNED, target=STATUS.BROADCAST)
    def broadcast(self):
        pass

    @transition(field=status, source=STATUS.BROADCAST, target=STATUS.SIGNED)
    def rebroadcast(self):
        # TODO testing only. Remove later
        pass

    @transition(field=status, source=STATUS.BROADCAST, target=STATUS.CONFIRMED)
    def confirm(self):
        pass

    @transition(field=status, source=[STATUS.NEW], target=STATUS.CANCELLED)
    def cancel(self):
        pass

    @transition(field=status, source=[STATUS.NEW], target=STATUS.REJECTED)
    def reject(self):
        pass

    @transition(field=status, source=[STATUS.NEW, STATUS.SUBMITTED, STATUS.BROADCAST], target=STATUS.FAILED)
    def fail(self):
        pass
