from decimal import Decimal

from django.conf import settings
from django.db import transaction

from avalanche.models import ChainSwap

from .cchain_export_to_pchain import CChainExportToPChain
from .cchain_import_from_pchain import CChainImportFromPChain
from .pchain_export_to_cchain import PChainExportToCChain
from .pchain_import_from_cchain import PChainImportFromCChain


def create_chain_swap(source_chain: str):
    assert source_chain in ('C', 'P')

    def export_c_to_p(amount: Decimal):
        with transaction.atomic():
            export = CChainExportToPChain(network_id=settings.NETWORK_ID)
            export_tx = export.build_transaction(amount=amount)
            swap = ChainSwap(source_chain=source_chain, export_tx=export_tx)
            swap.save()

    def export_p_to_c(amount: Decimal):
        with transaction.atomic():
            export = PChainExportToCChain(network_id=settings.NETWORK_ID)
            export_tx = export.build_transaction(amount=amount)
            swap = ChainSwap(source_chain=source_chain, export_tx=export_tx)
            swap.save()

    return export_c_to_p if source_chain == 'C' else export_p_to_c


def create_import_tx(source_chain: str):
    assert source_chain in ('C', 'P')

    def import_p_from_c(swap: ChainSwap):
        with transaction.atomic():
            import_ = PChainImportFromCChain(network_id=settings.NETWORK_ID)
            import_tx = import_.build_transaction()
            swap.import_tx = import_tx
            swap.save()

    def import_c_from_p(swap: ChainSwap):
        with transaction.atomic():
            import_ = CChainImportFromPChain(network_id=settings.NETWORK_ID)
            import_tx = import_.build_transaction()
            swap.import_tx = import_tx
            swap.save()

    return import_p_from_c if source_chain == 'C' else import_c_from_p
