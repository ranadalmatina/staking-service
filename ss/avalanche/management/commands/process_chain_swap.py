from django.core.management.base import BaseCommand

from avalanche.tasks import process_chain_swap


class Command(BaseCommand):
    help = "Process state transitions for AtomicTx."

    def handle(self, *args, **options):
        process_chain_swap()
