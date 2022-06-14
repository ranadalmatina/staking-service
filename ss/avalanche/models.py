import logging
import uuid

from django_fsm import FSMField, transition
from extended_choices import Choices

from django.db import models

from avalanche.base58 import Base58Decoder
from avalanche.datastructures import UnsignedTransaction
from avalanche.datastructures.types import AtomicTx as AtomicTxType
from common.constants import MAX_DEC_PLACES
from common.validators import validate_positive

logger = logging.getLogger(__name__)


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
        # Send transaction to Fireblocks for signing
        pass

    @transition(field=status, source=STATUS.SUBMITTED, target=STATUS.AWAITING_SIGNATURE)
    def queue(self):
        # Successfully sent to Fireblocks. Awaiting signature from Firebolcks
        pass

    @transition(field=status, source=STATUS.AWAITING_SIGNATURE, target=STATUS.SIGNED)
    def sign(self):
        # Signature received from Fireblocks. Transaction signed
        pass

    @transition(field=status, source=STATUS.SIGNED, target=STATUS.BROADCAST)
    def broadcast(self):
        # Transaction broadcast to Avalanche network
        pass

    @transition(field=status, source=STATUS.BROADCAST, target=STATUS.CONFIRMED)
    def confirm(self):
        # Transaction successfully broadcast, tx_id returned
        pass

    @transition(field=status, source=[STATUS.NEW], target=STATUS.REJECTED)
    def reject(self):
        pass

    @transition(field=status, source=[STATUS.NEW, STATUS.SUBMITTED, STATUS.BROADCAST], target=STATUS.FAILED)
    def fail(self):
        pass


class ChainSwap(models.Model):
    """
    An orchestration model for managing the two atomic transactions (an export and an import)
    that are required to swap AVAX between chains.
    """
    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('EXPORTING', 'exporting', 'Exporting'),
        ('EXPORTED', 'exported', 'Exported'),
        ('IMPORTING', 'importing', 'Importing'),
        ('COMPLETE', 'complete', 'Complete'),
        ('FAILED', 'failed', 'Failed'),
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    export_tx = models.ForeignKey('AtomicTx', on_delete=models.CASCADE, related_name='+')
    import_tx = models.ForeignKey('AtomicTx', on_delete=models.CASCADE, related_name='+', null=True)

    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'ChainSwap({self.id})'

    def export_exists(self):
        return self.export_tx is not None

    def export_complete(self):
        return self.export_exists() and self.export_tx.status == AtomicTx.STATUS.CONFIRMED

    def import_exists(self):
        return self.import_tx is not None

    def import_complete(self):
        return self.import_exists() and self.import_tx.status == AtomicTx.STATUS.CONFIRMED

    @transition(field=status, source=STATUS.NEW, target=STATUS.EXPORTING, conditions=[export_exists])
    def exporting(self):
        pass

    @transition(field=status, source=STATUS.EXPORTING, target=STATUS.EXPORTED, conditions=[export_complete])
    def exported(self):
        pass

    @transition(field=status, source=STATUS.EXPORTED, target=STATUS.IMPORTING, conditions=[import_exists])
    def importing(self):
        pass

    @transition(field=status, source=STATUS.IMPORTING, target=STATUS.COMPLETE, conditions=[import_complete])
    def complete(self):
        pass

    @transition(field=status, source=[STATUS.EXPORTING, STATUS.IMPORTING], target=STATUS.FAILED)
    def fail(self):
        pass
