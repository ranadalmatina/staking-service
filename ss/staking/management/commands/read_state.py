from django.conf import settings
from django.core.management.base import BaseCommand
from staking.contracts import Contracts
from staking.graphql import GraphAPI


class Command(BaseCommand):
    help = "Read some basic state from our contracts"

    def handle(self, *args, **options):
        contracts = Contracts()
        graphapi = GraphAPI(settings.GRAPHQL_URL)

        total_controlled = contracts.staking.functions.totalControlledAVAX().call()
        print(f'Total controlled AVAX {total_controlled}')

        deficit = graphapi.contract_avax_deficit()
        print(f'Contract deficit {deficit}')
