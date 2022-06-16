from django.core.management.base import BaseCommand

from staking.export import Export


class Command(BaseCommand):
    help = "Run the export command manually"

    def handle(self, *args, **options):
        exporter = Export()
        exporter.run_export_to_pchain()
