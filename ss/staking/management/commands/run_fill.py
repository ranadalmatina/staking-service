import traceback
from django.core.management.base import BaseCommand
from staking.fill import Fill
from fireblocks.client import get_fireblocks_client


class Command(BaseCommand):
    help = "Initaite staking on p-chain"

    def handle(self, *args, **options):
        try:
            # fill = Fill()
            # fill.run_fill()

            client = get_fireblocks_client()
            print(client.get_transactions(source_id='1'))

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            raise e
