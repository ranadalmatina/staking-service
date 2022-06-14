from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from avalanche.models import ChainSwap
from avalanche.utils.cchain_export_to_pchain import CChainExportToPChain


class Command(BaseCommand):
    help = "Create a chain swap from C-Chain to P-Chain."

    def handle(self, *args, **options):
        amount = Decimal("1")  # 1 AVAX
        with transaction.atomic():
            export = CChainExportToPChain(network_id=5)
            export_tx = export.build_transaction(amount=amount)
            swap = ChainSwap(export_tx=export_tx)
            swap.save()
