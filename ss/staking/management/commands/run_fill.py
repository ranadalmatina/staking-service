import traceback

from django.core.management.base import BaseCommand

from staking.fill import Fill


class Command(BaseCommand):
    help = "Initaite staking on p-chain"

    def handle(self, *args, **options):
        try:
            fill = Fill()
            fill.run_fill()

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            raise e
