from datetime import datetime

import pytz

from django.core.management.base import BaseCommand

from fireblocks.client import get_fireblocks_client
from fireblocks.models import (ExternalWalletAsset, FireblocksWallet, Transaction, VaultAccount, VaultAsset,
                               VaultWalletAddress)
from fireblocks.utils.deposit import get_or_create_deposit, update_deposit_status
from fireblocks.utils.wallet_import import import_external_wallet
from fireblocks.utils.withdrawal import get_or_create_withdrawal


class Command(BaseCommand):
    help = 'Import Fireblocks data into models.'

    def add_arguments(self, parser):
        parser.add_argument('--no-link', dest='link_transactions', action='store_false',
                            help='Do not attempt to link imported Transaction objects')

    def _import_vault_accounts(self):
        vault_count = 0
        asset_count = 0
        wallet_count = 0

        fb = get_fireblocks_client()
        accounts = fb.get_vault_accounts()
        try:
            for account_data in accounts:
                customer_ref_id = account_data.get('customerRefId', '')

                account, created = VaultAccount.objects.get_or_create(
                    vault_id=account_data['id'], defaults={
                        'name': account_data['name'],
                        'customer_ref_id': customer_ref_id,
                    })
                if created:
                    vault_count += 1

                for asset_data in account_data['assets']:
                    # Create wallets for each asset in the vault
                    asset, created = VaultAsset.objects.get_or_create(asset_id=asset_data['id'])
                    if created:
                        asset_count += 1

                    wallet, created = FireblocksWallet.objects.get_or_create(vault_account=account, asset=asset)
                    if created:
                        wallet_count += 1
        finally:
            self.stdout.write(self.style.SUCCESS(f'Imported {vault_count} new VaultAccount objects'))
            self.stdout.write(self.style.SUCCESS(f'Imported {asset_count} new VaultAsset objects'))
            self.stdout.write(self.style.SUCCESS(f'Imported {wallet_count} new FireblocksWallet objects'))

    def _import_addresses(self):
        address_count = 0
        fb = get_fireblocks_client()

        try:
            for wallet in FireblocksWallet.objects.all():
                addresses = fb.get_deposit_addresses(vault_account_id=wallet.vault_account.vault_id,
                                                     asset_id=wallet.asset.asset_id)
                for address_data in addresses:
                    defaults = {
                        'description': address_data['description'],
                        'tag': address_data['tag'],
                        'type': address_data['type'],
                    }
                    address, created = VaultWalletAddress.objects.get_or_create(
                        wallet=wallet, address=address_data['address'], defaults=defaults)
                    if created:
                        address_count += 1
        finally:
            self.stdout.write(self.style.SUCCESS(f'Imported {address_count} new VaultWalletAddress objects'))

    def _import_transactions(self):
        tx_count = 0
        fb = get_fireblocks_client()

        try:
            transactions = fb.get_transactions(limit=1000)

            # Import transactions earliest first
            for tx_data in sorted(transactions, key=lambda tx_: tx_['createdAt']):
                timestamp = tx_data['createdAt']
                created_at = datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)

                defaults = {
                    'asset_id': tx_data['assetId'],
                    'created_at': created_at,
                    'data': tx_data,
                }
                tx, created = Transaction.objects.get_or_create(tx_id=tx_data['id'], defaults=defaults)
                if created:
                    tx_count += 1
        finally:
            self.stdout.write(self.style.SUCCESS(f'Imported {tx_count} new Transaction objects'))

    def _link_transactions(self):
        linked_deposit_count = 0
        linked_withdrawal_count = 0

        try:
            # Link Transactions starting with the earliest first
            for tx in Transaction.unmatched.order_by('created_at'):
                deposit = get_or_create_deposit(transaction=tx)
                if deposit:
                    update_deposit_status(tx)
                    linked_deposit_count += 1
                else:
                    withdrawal = get_or_create_withdrawal(transaction=tx)
                    if withdrawal:
                        linked_withdrawal_count += 1

        finally:
            self.stdout.write(
                self.style.SUCCESS(f'Linked {linked_deposit_count} Transaction objects to VaultDeposits'))
            self.stdout.write(
                self.style.SUCCESS(f'Linked {linked_withdrawal_count} Transaction objects to VaultWithdrawals'))

    def _import_external_wallets(self):
        wallets_created = 0
        assets_created = 0

        fb = get_fireblocks_client()
        external_wallets = fb.get_external_wallets()

        try:
            for wallet_data in external_wallets:
                wallet, created = import_external_wallet(wallet_data=wallet_data)
                if created:
                    wallets_created += 1

                wallet_assets = wallet_data['assets']

                for wallet_asset in wallet_assets:
                    asset_id = wallet_asset['id']
                    address = wallet_asset['address']
                    status = wallet_asset['status']
                    tag = wallet_asset['tag']

                    try:
                        asset = VaultAsset.objects.get(asset_id=asset_id)
                    except VaultAsset.DoesNotExist as e:
                        self.stderr.write(f'Unable to find VaultAsset: {asset_id}')
                        self.stderr.write(str(e))
                    else:
                        ewa, created = ExternalWalletAsset.objects.get_or_create(
                            wallet=wallet, asset=asset, address=address, defaults={'status': status, 'tag': tag})
                        if created:
                            assets_created += 1

        finally:
            self.stdout.write(self.style.SUCCESS(f'Created {wallets_created} new ExternalWallet objects'))
            self.stdout.write(self.style.SUCCESS(f'Created {assets_created} new ExternalWalletAsset objects'))

    def handle(self, *args, **options):
        self.stdout.write('Importing Vault Accounts')
        self._import_vault_accounts()

        self.stdout.write('Importing Wallet Addresses')
        self._import_addresses()

        self.stdout.write('Importing Transactions')
        self._import_transactions()

        if options['link_transactions']:
            self.stdout.write('Linking imported Transactions')
            self._link_transactions()

        self.stdout.write('Importing External Wallets')
        self._import_external_wallets()
