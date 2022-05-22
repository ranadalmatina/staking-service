import logging
import os.path
from decimal import Decimal

from fireblocks_sdk import EXTERNAL_WALLET, UNKNOWN_PEER, VAULT_ACCOUNT
from fireblocks_sdk.sdk import DestinationTransferPeerPath, FireblocksApiException, FireblocksSDK, TransferPeerPath

from django.conf import settings

logger = logging.getLogger(__name__)


class FireblocksClient(FireblocksSDK):
    """
    FireblocksSDK that supports reading the private key either directly
    from an env var or from a local file on disk.
    """

    def __new__(cls, *args, **kwargs):
        # Setup the private key as a class attribute so that we only need to read it once
        if not hasattr(cls, 'FIREBLOCKS_PRIVATE_KEY'):
            if settings.FIREBLOCKS_PRIVATE_KEY is None:
                raise FireblocksApiException('Please setup Fireblocks private key env var.')

            if '-----BEGIN PRIVATE KEY-----' in settings.FIREBLOCKS_PRIVATE_KEY:
                # Env var directly contains the private key
                setattr(cls, 'FIREBLOCKS_PRIVATE_KEY', settings.FIREBLOCKS_PRIVATE_KEY)
            else:
                # Env var is a file path to the private key
                path = os.path.abspath(settings.FIREBLOCKS_PRIVATE_KEY)
                logger.info(f'Reading private key file from {path}')
                with open(path, 'r') as f:
                    setattr(cls, 'FIREBLOCKS_PRIVATE_KEY', f.read())

        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__(private_key=self.FIREBLOCKS_PRIVATE_KEY, api_key=settings.FIREBLOCKS_API_KEY)

    def one_time_address_withdrawal(self, vault_account_id: str, asset_id: str, amount: Decimal, address: str):
        one_time_address = {'address': address}
        source = TransferPeerPath(peer_type=VAULT_ACCOUNT, peer_id=vault_account_id)
        dest = DestinationTransferPeerPath(peer_type=UNKNOWN_PEER, peer_id='', one_time_address=one_time_address)
        return self.create_transaction(asset_id, amount=str(amount), source=source, destination=dest)

    def external_wallet_withdrawal(self, vault_account_id: str, asset_id: str, external_wallet_id: str,
                                   amount: Decimal):
        source = TransferPeerPath(peer_type=VAULT_ACCOUNT, peer_id=vault_account_id)
        dest = DestinationTransferPeerPath(peer_type=EXTERNAL_WALLET, peer_id=external_wallet_id)
        return self.create_transaction(asset_id, amount=str(amount), source=source, destination=dest)

    def vault_to_vault_transfer(self, source_vault_account_id: str, asset_id: str, destination_vault_account_id: str,
                                amount: Decimal):
        source = TransferPeerPath(peer_type=VAULT_ACCOUNT, peer_id=source_vault_account_id)
        dest = DestinationTransferPeerPath(peer_type=VAULT_ACCOUNT, peer_id=destination_vault_account_id)
        return self.create_transaction(asset_id, amount=str(amount), source=source, destination=dest)


def get_fireblocks_client():
    return FireblocksClient()