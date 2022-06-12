from django.contrib import admin

from .models import FillJob


@admin.register(FillJob)
class FillJobAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    readonly_fields = ('created_date', 'modified_date', 'amount_wei', 'fireblocks_transaction_id')
    list_display = ('id', 'created_date', 'amount_wei', 'status', 'fireblocks_transaction_id')
