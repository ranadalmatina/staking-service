import logging

from django.conf import settings

from avalanche.api import AvalancheClient
from avalanche.base58 import Base58Encoder
from avalanche.constants import CChainAlias, PChainAlias, XChainAlias
from avalanche.datastructures import SECP256K1Credential, SignedTransaction
from common.bip.bip32 import fireblocks_public_key
from fireblocks.client import FireblocksApiException, get_fireblocks_client
from fireblocks.utils.raw_signing import recoverable_signature, verify_message_hash

from ..models import AtomicTx

logger = logging.getLogger(__name__)


def send_for_signing(tx: AtomicTx):
    assert tx.status == AtomicTx.STATUS.NEW
    unsigned_tx = tx.get_unsigned_transaction()
    message_hash = unsigned_tx.hash().hex()
    tx.submit()
    tx.save()

    client = get_fireblocks_client()

    try:
        response = client.vault_raw_transaction(vault_account_id='0', asset_id='AVAXTEST', message_hash=message_hash,
                                                note=tx.description)
        logger.info(response)
    except FireblocksApiException as e:
        # TODO handle certain types of exception from Fireblocks
        logger.exception(e)
    else:
        if 'status' in response and response['status'] in ['SUBMITTED', 'COMPLETED']:
            tx.fireblocks_tx_id = response['id']
            tx.queue()  # Move status to AWAITING_SIGNATURE
            tx.save()


def _get_signed_messages(tx: AtomicTx):
    """
    Fetch signed messages from Fireblocks for the given Transaction
    :param tx:
    :return:
    """
    client = get_fireblocks_client()
    response = client.get_transaction_by_id(txid=tx.fireblocks_tx_id)
    if 'status' in response and response['status'] == 'COMPLETED':
        if 'signedMessages' in response:
            return response['signedMessages']
    return None


def _check_for_signature(tx: AtomicTx):
    signed_messages = _get_signed_messages(tx)
    if signed_messages is not None:
        pub_key = fireblocks_public_key(tx.from_derivation_path)
        unsigned_tx = tx.get_unsigned_transaction()
        message_hash = unsigned_tx.hash()
        sig = recoverable_signature(signed_messages)
        verify_message_hash(pub=pub_key.ToBytes(), msg_hash=message_hash, sig=sig)
        return sig
    return None


def check_for_signature(tx: AtomicTx):
    assert tx.status == tx.STATUS.AWAITING_SIGNATURE
    sig = _check_for_signature(tx)
    if sig is not None:
        atomic_tx = tx.get_unsigned_transaction().atomic_tx
        print('-----------Signed---------')
        cred = SECP256K1Credential([sig.to_bytes()])
        signed_tx = SignedTransaction(atomic_tx, [cred])
        b58_signed_tx = Base58Encoder.CheckEncode(signed_tx.to_bytes())
        tx.signed_transaction = b58_signed_tx
        tx.sign()
        tx.save()
        return b58_signed_tx
    return None


def broadcast_transaction(tx: AtomicTx):
    assert tx.status == tx.STATUS.SIGNED
    unsigned_tx = tx.get_unsigned_transaction()
    source_chain = unsigned_tx.get_source_chain()

    def fail_tx(response, msg: str):
        logger.error(response)
        tx.fail()
        tx.save()
        raise Exception(msg)  # TODO customise exception class

    def get_issue_tx():
        client = AvalancheClient(RPC_URL=settings.AVAX_RPC_URL)
        issue_tx = {
            PChainAlias: client.platform_issue_tx,
            XChainAlias: client.avm_issue_tx,
            CChainAlias: client.evm_issue_tx,
        }
        return issue_tx[source_chain]

    issue_tx = get_issue_tx()
    tx.broadcast()
    tx.save()
    response = issue_tx(tx.signed_transaction)
    if response.status_code == 200:
        response = response.json()
        if 'result' in response:
            logger.info(response)
            result = response['result']
            if 'txID' in result:
                tx.avalanche_tx_id = result['txID']
                tx.confirm()
                tx.save()

        elif 'error' in response:
            fail_tx(response, msg=f"Error while issuing transaction: {response['error']}")
        else:
            # JSON response here
            logger.error('Unknown response type from Avalanche')
            fail_tx(response, msg="Unknown error while issuing transaction")

    else:
        # Some other error code. Unknown response
        logger.error('Unknown response type from Avalanche')
        fail_tx(response, msg="Unknown error while issuing transaction")
