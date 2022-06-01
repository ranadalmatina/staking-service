from django.core.management.base import BaseCommand
from staking.contracts import Contracts


class Command(BaseCommand):
    help = "Read some basic state from our contracts"

    def handle(self, *args, **options):
        contracts = Contracts()
        total_controlled = contracts.staking.functions.totalControlledAVAX().call()
        print(f'Total controlled AVAX {total_controlled}')
