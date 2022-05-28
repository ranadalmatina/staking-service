from django.contrib import admin, messages

from .models import AtomicTx
from common.utils.explorer import get_explorer_link


@admin.register(AtomicTx)
class AtomicTxAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    readonly_fields = ('created_date', 'modified_date', 'from_derivation_path', 'from_address', 'to_derivation_path',
                       'to_address', 'amount', 'description', 'unsigned_transaction', 'fireblocks_tx_id',
                       'signed_transaction', 'avalanche_tx_id', 'status', 'explorer_link')
    list_display = ('__str__', 'created_date', 'from_address', 'amount', 'to_address', 'status')
    actions = ['resubmit']

    def explorer_link(self, obj):
        return get_explorer_link('FUJI_X', obj.avalanche_tx_id)

    def resubmit(self, request, queryset):
        for tx in queryset:
            tx.resubmit()
            tx.save()
            self.message_user(request, f'Reset state for {tx}', messages.SUCCESS)

    resubmit.short_description = 'Roll state back'
