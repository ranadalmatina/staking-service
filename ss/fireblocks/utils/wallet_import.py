import logging

from ..models import ExternalWallet

logger = logging.getLogger(__name__)


def import_external_wallet(wallet_data: dict):
    """
    Import an ExternalWallet object from Fireblocks given its wallet data.
    """
    wallet_id = wallet_data['id']
    name = wallet_data['name']
    customer_ref = wallet_data.get('customerRefId', '')

    wallet, created = ExternalWallet.objects.get_or_create(
        id=wallet_id, defaults={'name': name, 'customer_ref_id': customer_ref})

    return wallet, created
