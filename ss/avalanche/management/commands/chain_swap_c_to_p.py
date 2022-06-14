from decimal import Decimal

from django.core.management.base import BaseCommand

from avalanche.utils.chain_swap import create_chain_swap


class Command(BaseCommand):
    help = "Create a chain swap from C-Chain to P-Chain or vice-versa."

    def handle(self, *args, **options):
        amount = Decimal("1")  # 1 AVAX
        create_swap_fn = create_chain_swap(source_chain='P')
        create_swap_fn(amount=amount)
