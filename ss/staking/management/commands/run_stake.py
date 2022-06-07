from django.core.management.base import BaseCommand
from staking.staking import Staking


class Command(BaseCommand):
    help = "Initaite staking on p-chain"

    def handle(self, *args, **options):
        staking = Staking()
        staking.run_staking()
