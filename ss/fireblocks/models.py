import logging
import uuid
from datetime import datetime
from decimal import Decimal

import pytz
from django_fsm import FSMField, transition
from extended_choices import Choices

from django.db import models
from django.db.models import CheckConstraint, ObjectDoesNotExist, Q, UniqueConstraint
from django.utils import timezone

from common.validators import validate_positive
from common.constants import MAX_DEC_PLACES

from .fields import NullTextField


logger = logging.getLogger(__name__)


class LabelledAddress(models.Model):

    address = models.CharField(max_length=50, unique=True)
    label = models.TextField(help_text='Description of address')


class VaultAccount(models.Model):
    """
    A Fireblocks Vault Account.
    https://docs.fireblocks.com/api/#vaultaccount
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    vault_id = models.TextField(primary_key=True, unique=True)
    name = models.TextField()

    customer_ref_id = models.TextField(
        help_text='The ID for AML providers to associate the owner of funds with transactions')

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'[{self.vault_id}] {self.name}'


class VaultAsset(models.Model):
    """
    An asset stored in a Vault Account
    https://docs.fireblocks.com/api/#vaultasset
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    asset_id = models.TextField(primary_key=True, unique=True)
    # Fireblocks forces us to treat ERC-20 assets differently to non ERC-20 assets.
    is_erc_20 = models.BooleanField(default=False, help_text='Is this asset an ERC-20 asset?')

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'{self.asset_id}'


class FireblocksWallet(models.Model):
    """
    This object represents a single asset in a vault account on Fireblocks.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    vault_account = models.ForeignKey(VaultAccount, on_delete=models.CASCADE)
    asset = models.ForeignKey(VaultAsset, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_date']
        # Only one wallet of each asset type is allowed per vault
        unique_together = ['vault_account', 'asset']

    def __str__(self):
        return f'[{self.vault_account.name}] {self.asset}'

    @property
    def asset_id(self):
        return self.asset.asset_id


class ExternalWallet(models.Model):
    """
    Wallets belonging to counterparties.
    https://docs.fireblocks.com/api/#externalwallet
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.TextField(primary_key=True, unique=True)
    name = models.TextField(help_text='Unique name for the wallet')
    label = models.ForeignKey(LabelledAddress, on_delete=models.CASCADE, null=True)

    customer_ref_id = models.TextField(
        help_text='The ID for AML providers to associate the owner of funds with transactions')

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'[{self.id}] {self.name}'

    def get_external_wallet_asset(self, asset: VaultAsset):
        return self.assets.filter(asset=asset).first()


class ExternalWalletAsset(models.Model):
    """
    An asset and address for the asset that is part of an external wallet.
    https://docs.fireblocks.com/api/#externalwalletasset
    """
    STATUS = Choices(
        ('WAITING_FOR_APPROVAL', 'WAITING_FOR_APPROVAL', 'Waiting for approval'),
        ('APPROVED', 'APPROVED', 'Approved'),
        ('CANCELLED', 'CANCELLED', 'Cancelled'),
        ('REJECTED', 'REJECTED', 'Rejected'),
        ('FAILED', 'FAILED', 'Failed'),
    )

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wallet = models.ForeignKey(ExternalWallet, on_delete=models.CASCADE, related_name='assets')
    # All external wallets asset_ids must match an existing VaultAsset
    asset = models.ForeignKey(VaultAsset, on_delete=models.CASCADE)

    address = models.TextField(help_text='Asset address. Globally unique per asset')
    status = models.CharField(max_length=30, choices=STATUS, default=STATUS.WAITING_FOR_APPROVAL)
    tag = models.TextField(help_text='Destination tag of the wallet')

    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = 'external wallet assets'
        constraints = [
            # Only one WalletAsset of each asset type is allowed per ExternalWallet
            UniqueConstraint(fields=['wallet', 'asset'], name='asset_unique_per_wallet'),
            # Address should be unique per asset per wallet.
            # This would allow the same address to exist in another wallet
            UniqueConstraint(fields=['wallet', 'asset', 'address'], name='ewa_unique_address'),
        ]
        indexes = [
            models.Index(fields=['wallet', 'asset', 'address']),
        ]

    def __str__(self):
        return f'[{self.id}] {self.asset} - {self.address}'

    def update_status(self, new_status, save=False):
        if self.status != new_status:
            self.status = new_status
            if save:
                self.save(update_fields=['status'])


class VaultWalletAddress(models.Model):
    """
    Fireblocks Deposit Address object
    https://docs.fireblocks.com/api/#vaultwalletaddress
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    wallet = models.ForeignKey(FireblocksWallet, on_delete=models.CASCADE)

    address = models.TextField(help_text='Asset address. Globally unique per asset')
    description = models.TextField(help_text='Address description')
    tag = models.TextField(blank=True)
    type = models.TextField(help_text='Address type')

    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = 'vault wallet addresses'
        constraints = [
            # Only one wallet of each asset type is allowed per vault
            UniqueConstraint(fields=['wallet', 'address'], name='unique_address'),
        ]
        indexes = [
            models.Index(fields=['wallet', 'address']),
        ]

    def __str__(self):
        return self.address

    @property
    def asset(self):
        return self.wallet.asset


class UnmatchedTransactionManager(models.Manager):

    def get_queryset(self):
        # When looping over unlinked Transactions, start with the earliest first
        return super().get_queryset().filter(deposit__isnull=True, withdrawal__isnull=True).order_by('created_at')


class Transaction(models.Model):
    """
    A Fireblocks transaction object.
    https://docs.fireblocks.com/api/#transactiondetails

    This object is usually linked to a VaultDeposit or VaultWithdrawal.
    """
    created_date = models.DateTimeField(auto_now_add=True, help_text='Transaction creation date in SS.')
    created_at = models.DateTimeField(editable=False, help_text='Transaction creation date in Fireblocks.')
    modified_date = models.DateTimeField(auto_now=True)

    tx_id = models.TextField(primary_key=True, unique=True)
    asset_id = models.TextField()
    data = models.JSONField()

    # Each deposit is linked to exactly one transaction that defines the other deposit parameters
    deposit = models.OneToOneField('VaultDeposit', on_delete=models.CASCADE, null=True, blank=True)
    # Each withdrawal is linked to exactly one transaction that confirms the withdrawal
    withdrawal = models.OneToOneField('VaultWithdrawal', on_delete=models.CASCADE, null=True, blank=True)

    objects = models.Manager()  # The default manager.
    unmatched = UnmatchedTransactionManager()  # Custom manager for finding unmatched transactions

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Transaction may only belong to either a deposit or a withdrawal but never both
            CheckConstraint(check=Q(deposit__isnull=True) | Q(withdrawal__isnull=True),
                            name='deposit_or_withdrawal'),
        ]

    def __str__(self):
        return f'{self.tx_id}'

    def get_created_at(self):
        if 'createdAt' in self.data:
            timestamp = self.data['createdAt']
            return datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)
        return None

    @property
    def last_updated(self):
        if 'lastUpdated' in self.data:
            timestamp = self.data['lastUpdated']
            return datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)
        return None

    @property
    def amount(self):
        if 'amount' in self.data and self.data['amount']:
            return Decimal(str(self.data['amount']))
        return None

    @property
    def fee(self):
        # Unknown why there are two possible locations for fee
        # Devin thinks that fee is the old style
        if 'fee' in self.data:
            return Decimal(str(self.data['fee']))
        if 'networkFee' in self.data:
            return Decimal(str(self.data['networkFee']))
        return None

    @property
    def tx_hash(self):
        if 'txHash' in self.data:
            return self.data['txHash']
        return None

    @property
    def status(self):
        if 'status' in self.data:
            return self.data['status']
        return None

    @property
    def destination(self):
        if 'destination' in self.data:
            return self.data['destination']
        return None

    @property
    def destination_address(self):
        if 'destinationAddress' in self.data:
            return self.data['destinationAddress']
        return None

    @property
    def destination_vault_account(self):
        if 'destination' in self.data:
            destination = self.data['destination']
            if 'type' in destination and destination['type'] == 'VAULT_ACCOUNT':
                return destination['id']
        return None

    @property
    def destination_external_wallet(self):
        if 'destination' in self.data:
            destination = self.data['destination']
            if 'type' in destination and destination['type'] == 'EXTERNAL_WALLET':
                return destination['id']
        return None

    def get_vault_account(self):
        """
        Retrieve the VaultAccount object from the destination of this transaction.
        """
        vault_id = self.destination_vault_account
        if vault_id is not None:
            try:
                return VaultAccount.objects.get(vault_id=vault_id)
            except VaultAccount.DoesNotExist:
                pass
        return None

    def get_external_wallet(self):
        """
        Retrieve the ExternalWallet object from the destination of this transaction.
        """
        external_wallet_id = self.destination_external_wallet
        if external_wallet_id is not None:
            try:
                return ExternalWallet.objects.get(id=external_wallet_id)
            except ExternalWallet.DoesNotExist:
                pass
        return None

    def get_vault_asset(self):
        """
        Retrieve the VaultAsset object linked in the transaction.
        """
        try:
            return VaultAsset.objects.get(asset_id=self.asset_id)
        except VaultAccount.DoesNotExist:
            return None

    def get_fireblocks_wallet(self):
        """
        Retrieve the FireblocksWallet object that this transaction belongs to.
        """
        account = self.get_vault_account()
        asset = self.get_vault_asset()
        if asset and account:
            try:
                return FireblocksWallet.objects.get(vault_account=account, asset=asset)
            except FireblocksWallet.DoesNotExist:
                pass
        return None

    def get_vault_wallet_address(self):
        """
        Retrieve the VaultWalletAddress object that is described by the destination address.
        """
        wallet = self.get_fireblocks_wallet()
        if wallet and self.destination_address:
            try:
                return VaultWalletAddress.objects.get(wallet=wallet, address=self.destination_address)
            except VaultWalletAddress.DoesNotExist:
                pass
        return None


# TODO add from??
class VaultDeposit(models.Model):
    """
    Deposit to an Address in a Fireblocks Vault.
    """
    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('RECEIVED', 'received', 'Received'),
        ('CONFIRMED', 'confirmed', 'Confirmed'),
    )

    created_date = models.DateTimeField(default=timezone.now, editable=False)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.ForeignKey(VaultWalletAddress, on_delete=models.CASCADE)
    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)

    class Meta:
        ordering = ['-created_date']
        get_latest_by = ['modified_date', 'created_date']

    def __str__(self):
        return str(self.id)

    @property
    def amount(self):
        try:
            return self.transaction.amount
        except ObjectDoesNotExist:
            return Decimal('0')

    @property
    def fee(self):
        try:
            return self.transaction.fee
        except ObjectDoesNotExist:
            return Decimal('0')

    @property
    def asset(self):
        return self.address.asset

    @transition(field=status, source=STATUS.NEW, target=STATUS.RECEIVED)
    def receive(self):
        pass

    @transition(field=status, source=[STATUS.NEW, STATUS.RECEIVED], target=STATUS.CONFIRMED)
    def confirm(self):
        pass


class VaultWithdrawal(models.Model):
    """
    Represents a withdrawal from a Fireblocks Vault account to an ExternalWallet.
    """
    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('APPROVED', 'approved', 'Approved'),
        ('QUEUED', 'queued', 'Queued'),
        ('SENT', 'sent', 'Sent'),
        ('CONFIRMED', 'confirmed', 'Confirmed'),
        ('FROZEN', 'frozen', 'Frozen'),
        ('CANCELLED', 'cancelled', 'Cancelled'),
        ('REJECTED', 'rejected', 'Rejected'),
        ('FAILED', 'failed', 'Failed'),
    )

    created_date = models.DateTimeField(default=timezone.now, editable=False)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wallet_asset = models.ForeignKey(ExternalWalletAsset, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=30, decimal_places=MAX_DEC_PLACES, validators=[validate_positive])
    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)

    # After we create a transaction from this withdrawal, we get the ID in the response from Fireblocks
    transaction_id = NullTextField(unique=True, default=None,
                                   help_text='The transaction ID of the withdrawal transaction')

    class Meta:
        ordering = ['-created_date']
        get_latest_by = ['modified_date', 'created_date']

    def __str__(self):
        return str(self.id)

    @property
    def asset(self):
        return self.wallet_asset.asset

    @transition(field=status, source=STATUS.NEW, target=STATUS.APPROVED)
    def approve(self):
        pass

    @transition(field=status, source=STATUS.APPROVED, target=STATUS.QUEUED)
    def queue(self):
        pass

    @transition(field=status, source=STATUS.QUEUED, target=STATUS.SENT)
    def send(self):
        pass

    @transition(field=status, source=STATUS.SENT, target=STATUS.CONFIRMED)
    def confirm(self):
        pass

    @transition(field=status, source=STATUS.APPROVED, target=STATUS.FROZEN)
    def freeze(self):
        pass

    @transition(field=status, source=STATUS.FROZEN, target=STATUS.APPROVED)
    def unfreeze(self):
        pass

    @transition(field=status, source=[STATUS.NEW, STATUS.APPROVED], target=STATUS.CANCELLED)
    def cancel(self):
        pass

    @transition(field=status, source=[STATUS.NEW, STATUS.APPROVED, STATUS.FROZEN], target=STATUS.REJECTED)
    def reject(self):
        pass

    @transition(field=status, source=STATUS.SENT, target=STATUS.FAILED)
    def fail(self):
        pass


class WithdrawalJob(models.Model):
    """
    Stores raw data to create a VaultWithdrawal object.
    """
    STATUS = Choices(
        ('NEW', 'new', 'New'),
        ('PENDING', 'pending', 'Pending'),
        ('SUCCESS', 'success', 'Success'),
        ('FAILED', 'failed', 'Failed'),
    )

    created_date = models.DateTimeField(default=timezone.now, editable=False)
    modified_date = models.DateTimeField(auto_now=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=50, help_text="Address to withdraw to")
    asset = models.ForeignKey('VaultAsset', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=30, decimal_places=MAX_DEC_PLACES, validators=[validate_positive])
    status = FSMField(max_length=30, choices=STATUS, default=STATUS.NEW)

    error = models.TextField(help_text='Error information if the job fails', blank=True)
    withdrawal = models.OneToOneField('VaultWithdrawal', on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='job', help_text='The VaultWithdrawal created by this job')

    class Meta:
        ordering = ['-created_date']
        get_latest_by = ['modified_date', 'created_date']

    def __str__(self):
        return str(self.id)

    @transition(field=status, source=[STATUS.NEW, STATUS.PENDING], target=STATUS.FAILED)
    def fail(self, reason):
        """
        Set the job status to failed with the failure reason.
        """
        self.error = reason

    @transition(field=status, source=STATUS.NEW, target=STATUS.PENDING)
    def pending(self):
        """
        Mark the job as waiting on approval for the intermediate ExternalWalletAsset.
        """
        pass

    @transition(field=status, source=STATUS.PENDING, target=STATUS.SUCCESS)
    def complete(self, withdrawal: VaultWithdrawal):
        """
        Mark the job as having completed successfully, linking the created VaultWithdrawal.
        """
        self.withdrawal = withdrawal
