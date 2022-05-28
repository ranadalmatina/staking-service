from django.core.management.base import BaseCommand
from avalanche.tasks import process_atomic_transaction


class Command(BaseCommand):
    help = "Process state transitions for AtomicTx."

    def handle(self, *args, **options):
        process_atomic_transaction()
