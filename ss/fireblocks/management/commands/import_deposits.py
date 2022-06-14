from api.models import Deposit

from django.core.management.base import BaseCommand

from fireblocks.models import Transaction, VaultDeposit, VaultWalletAddress


class Command(BaseCommand):
    """
    Convert old API Deposit models into VaultDeposit models by
    matching the Transaction data between API and fireblocks apps
    """

    help = 'Generate Fireblocks VaultDeposit data from existing Deposit models.'

    def _import_deposits(self):
        deposit_count = 0

        try:
            for deposit in Deposit.objects.all():
                for transaction in deposit.transactions.all():
                    self.stdout.write(f'Deposit {deposit}, Transaction {transaction}')
                    if transaction.tx_hash:
                        try:
                            self.stdout.write(f'Fetching {transaction.tx_hash}...')
                            tx = Transaction.objects.get(data__txHash=transaction.tx_hash)
                        except Transaction.DoesNotExist:
                            self.stdout.write(self.style.WARNING('Not found'))
                        else:
                            if tx.deposit:
                                self.stdout.write(self.style.SUCCESS('Found transaction with existing deposit'))
                            else:
                                self.stdout.write('Found unmatched transaction')
                                created = self._create_deposit(deposit, tx)
                                if created:
                                    deposit_count += 1
        finally:
            self.stdout.write(self.style.SUCCESS(f'Imported {deposit_count} new VaultDeposit objects'))

    def _create_deposit(self, deposit, tx):
        # Fetch matching address
        address = VaultWalletAddress.objects.filter(address=deposit.address.address).first()
        if address:
            self.stdout.write(f'Found address {address.address}')
            # Validate address
            assert address.address == tx.destination_address

            d, created = VaultDeposit.objects.get_or_create(
                created_date=deposit.created_at, transaction=tx, account=deposit.account, address=address)
            return created

        return False

    def handle(self, *args, **options):
        self.stdout.write('Importing Deposits')
        self._import_deposits()
