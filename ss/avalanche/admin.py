from django.contrib import admin

from common.utils.explorer import get_explorer_link

from .models import AtomicTx


@admin.register(AtomicTx)
class AtomicTxAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    readonly_fields = ('created_date', 'modified_date', 'from_derivation_path', 'from_address', 'to_derivation_path',
                       'to_address', 'amount', 'description', 'unsigned_transaction', 'tx_type', 'fireblocks_tx_id',
                       'signed_transaction', 'avalanche_tx_id', 'status', 'explorer_link', 'transaction_hash')
    list_display = ('id', 'tx_type', 'created_date', 'from_address', 'amount', 'to_address', 'status')
    actions = ['resubmit', 'rebroadcast']

    def explorer_link(self, obj):
        return get_explorer_link('FUJI_X', obj.avalanche_tx_id)

    def transaction_hash(self, obj):
        if obj.unsigned_transaction != "":
            unsigned_tx = obj.get_unsigned_transaction()
            return unsigned_tx.hash().hex()
        return None

    def tx_type(self, obj):
        if obj.unsigned_transaction != "":
            unsigned_tx = obj.get_unsigned_transaction()
            return unsigned_tx.get_tx_type().__name__
        return None
