import requests

from .validator import Validator


class AvalancheClient:
    """
    Avalanche Go HTTP/RPC client.
    """
    C_CHAIN = "/ext/bc/C/avax"
    X_CHAIN = "/ext/bc/X"
    P_CHAIN = "/ext/bc/P"

    def __init__(self, rpc_url=None):
        if rpc_url is None:
            raise Exception("RPC URL is not set")
        self.url = rpc_url

    @property
    def rpc_url(self):
        return self.url

    @property
    def c_chain_rpc_url(self):
        return self.rpc_url + self.C_CHAIN

    @property
    def x_chain_rpc_url(self):
        return self.rpc_url + self.X_CHAIN

    @property
    def p_chain_rpc_url(self):
        return self.rpc_url + self.P_CHAIN

    def evm_get_atomic_tx(self, tx_id):
        response = requests.post(self.c_chain_rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "avax.getAtomicTxStatus",
            "params": {
                "txID": tx_id
            }
        })
        return response

    def evm_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.c_chain_rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "avax.issueTx",
            "params": {
                "tx": tx,
                "encoding": encoding
            }
        })
        return response

    def evm_get_utxos(self, addresses: list[str], source_chain: str, limit=1024, encoding="cb58"):
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "avax.getUTXOs",
            "params": {
                "addresses": addresses,
                "sourceChain": source_chain,
                "limit": limit,
                "encoding": encoding,
            }
        }
        return requests.post(self.c_chain_rpc_url, json=body)

    def avm_get_utxos(self, addresses: list[str], source_chain=None, limit=1024, encoding="cb58"):
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "avm.getUTXOs",
            "params": {
                "addresses": addresses,
                "limit": limit,
                "encoding": encoding,
            }
        }
        if source_chain is not None:
            body["params"]["sourceChain"] = source_chain

        return requests.post(self.x_chain_rpc_url, json=body)

    def platform_get_utxos(self, addresses: list[str], source_chain=None, limit=1024, encoding="cb58"):
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "platform.getUTXOs",
            "params": {
                "addresses": addresses,
                "limit": limit,
                "encoding": encoding,
            }
        }
        if source_chain is not None:
            body["params"]["sourceChain"] = source_chain

        return requests.post(self.p_chain_rpc_url, json=body)

    def avm_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.x_chain_rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "avm.issueTx",
            "params": {
                "tx": tx,
                "encoding": encoding
            }
        })
        return response

    def platform_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.p_chain_rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "platform.issueTx",
            "params": {
                "tx": tx,
                "encoding": encoding
            }
        })
        return response

    def platform_get_current_validators(self, nodes_ids: list[str] = None, encoding="cb58"):
        if nodes_ids is None:
            nodes_ids = []
        response = requests.post(self.p_chain_rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "platform.getCurrentValidators",
            "params": {
                "nodes_ids": nodes_ids,  # empty array returns all validators
                "encoding": encoding
            }
        })
        if response.status_code != 200:
            raise Exception("Failed to get current validators")
        data = response.json()
        validators = [Validator.from_json(d) for d in data["result"]["validators"]]
        return validators
