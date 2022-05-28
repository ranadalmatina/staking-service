from common.utils.urls import get_admin_link

from django.contrib import admin, messages
from django.utils.translation import ngettext

from .models import (ExternalWallet, ExternalWalletAsset, FireblocksWallet, Transaction, VaultAccount, VaultAsset,
                     VaultDeposit, VaultWalletAddress, VaultWithdrawal, WithdrawalJob)
from .utils.deposit import get_or_create_deposit, update_deposit_status
from common.utils.explorer import get_explorer_link


class FireblocksWalletInline(admin.TabularInline):
    model = FireblocksWallet
    readonly_fields = ('created_date', 'modified_date', 'vault_account', 'asset')
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(VaultAccount)
class VaultAccountAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'vault_id', 'name', 'customer_ref_id')
    list_display = ('__str__', 'created_date', 'vault_id', 'name')
    inlines = (FireblocksWalletInline, )


@admin.register(VaultAsset)
class VaultAssetAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'asset_id')
    list_display = ('__str__', 'created_date', 'asset_id', 'is_erc_20')


@admin.register(FireblocksWallet)
class FireblocksWalletAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'vault_account', 'asset')
    list_display = ('__str__', 'created_date', 'vault_account', 'asset')


class ExternalWalletAssetInline(admin.TabularInline):
    model = ExternalWalletAsset
    readonly_fields = ('created_date', 'id', 'wallet', 'asset', 'address', 'status', 'tag')
    exclude = ('modified_date', )
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(ExternalWallet)
class ExternalWalletAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'id', 'name', 'customer_ref_id')
    list_display = ('id', 'created_date', 'name')
    inlines = (ExternalWalletAssetInline, )


@admin.register(ExternalWalletAsset)
class ExternalWalletAssetAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'modified_date', 'id', 'wallet', 'asset', 'address', 'status', 'tag')
    list_display = ('id', 'created_date', 'wallet', 'asset', 'address', 'status')


class VaultDepositInline(admin.TabularInline):
    model = VaultDeposit
    readonly_fields = ('created_date', 'status', 'address', 'linked_transaction',
                       'asset', 'amount', 'fee')
    exclude = ('modified_date', 'transaction')
    extra = 0
    max_num = 0
    can_delete = False

    def linked_transaction(self, obj):
        return get_admin_link(obj.transaction)


@admin.register(VaultWalletAddress)
class VaultWalletAddressAdmin(admin.ModelAdmin):
    list_filter = ('wallet__asset', )
    search_fields = ['address']
    readonly_fields = ('created_date', 'modified_date', 'wallet', 'address', 'description', 'tag', 'type')
    list_display = ('__str__', 'created_date', 'wallet', 'address', 'description', 'deposit_count', 'type')
    inlines = (VaultDepositInline, )

    def deposit_count(self, obj):
        return VaultDeposit.objects.filter(address=obj).count()


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('asset_id', )
    exclude = ('deposit', 'withdrawal')
    readonly_fields = ('created_date', 'modified_date', 'tx_id', 'created_at', 'asset_id', 'amount', 'fee', 'status',
                       '_deposit', '_withdrawal', 'destination', 'destination_address', 'explorer_link', 'data')
    list_display = ('__str__', 'created_at', 'asset_id', 'destination_address', 'destination', '_deposit',
                    '_withdrawal', 'amount', 'status')
    actions = ['create_deposit']

    def destination_address(self, obj):
        return get_admin_link(obj.get_vault_wallet_address())

    def explorer_link(self, obj):
        return get_explorer_link(obj.asset_id, obj.tx_hash)

    def _deposit(self, obj):
        return get_admin_link(obj.deposit)

    def _withdrawal(self, obj):
        return get_admin_link(obj.withdrawal)

    def destination(self, obj):
        dest = obj.get_vault_account() or obj.get_external_wallet()
        return get_admin_link(dest)

    def linked_vault_account(self, obj):
        return get_admin_link(obj.get_vault_account())

    def linked_external_wallet(self, obj):
        return get_admin_link(obj.get_external_wallet())

    def create_deposit(self, request, queryset):
        # Create a linked deposit for the given transaction
        count = 0

        for tx in queryset:
            deposit = get_or_create_deposit(transaction=tx)
            if deposit:
                update_deposit_status(transaction=tx)
                count += 1

        self.message_user(request, ngettext(
            f'Linked {count} new deposit to a transaction.',
            f'Linked {count} new deposits to {count} transactions.',
            count), messages.SUCCESS)

    create_deposit.short_description = 'Get or create matching deposit'


@admin.register(VaultDeposit)
class VaultDepositAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    readonly_fields = ('created_date', 'modified_date', 'status', 'address', 'linked_transaction',
                       'asset', 'amount', 'fee')
    exclude = ('transaction',)
    list_display = ('__str__', 'created_date', 'address', 'status', 'linked_transaction')

    def linked_transaction(self, obj):
        return get_admin_link(obj.transaction)


@admin.register(VaultWithdrawal)
class VaultWithdrawalAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    exclude = ('wallet_asset', 'transaction')
    readonly_fields = ('created_date', 'modified_date', '_external_wallet_asset', '_transaction',
                       '_address', 'asset', 'amount', 'status', 'transaction_id', 'job')
    list_display = ('__str__', 'created_date', '_address', '_amount', 'status', 'transaction_id',
                    '_transaction', 'job')

    def _external_wallet_asset(self, obj):
        return get_admin_link(obj.wallet_asset)

    def _transaction(self, obj):
        return get_admin_link(obj.transaction)

    def _amount(self, obj):
        return obj.amount.normalize()

    def _address(self, obj):
        return obj.wallet_asset.address


@admin.register(WithdrawalJob)
class WithdrawalJobAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    readonly_fields = ('created_date', 'modified_date', 'address', 'asset', 'amount', 'status', 'error',
                       'withdrawal')
    list_display = ('__str__', 'created_date', 'address', 'asset', '_amount', 'status', '_withdrawal')

    def _amount(self, obj):
        return obj.amount.normalize()

    def _withdrawal(self, obj):
        return get_admin_link(obj.withdrawal)
