import requests


class AvalancheClient:
    """
    Avalanche Go HTTP/RPC client.
    """
    AVAX_HTTP = "https://api.avax.network"
    FUJI_HTTP = "https://api.avax-test.network"
    C_CHAIN = "/ext/bc/C/avax"
    X_CHAIN = "/ext/bc/X"
    P_CHAIN = "/ext/bc/P"

    def __init__(self, fuji=True):
        self.fuji = fuji

    @property
    def rpc_url(self):
        return self.FUJI_HTTP if self.fuji else self.AVAX_HTTP

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
            "jsonrpc":"2.0",
            "id"     :1,
            "method" :"avax.getAtomicTxStatus",
            "params" :{
                "txID": tx_id
            }
        })
        return response


    def evm_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.c_chain_rpc_url, json={
            "jsonrpc":"2.0",
            "id"     : 1,
            "method" :"avax.issueTx",
            "params" :{
                "tx": tx,
                "encoding": encoding
            }
        })
        return response


    def avm_get_utxos(self, addresses: list[str], source_chain: str, limit=1024, encoding="cb58"):
        response = requests.post(self.x_chain_rpc_url, json={
            "jsonrpc":"2.0",
            "id"     : 1,
            "method" :"avm.getUTXOs",
            "params" :{
                "addresses": addresses,
                "sourceChain": source_chain,
                "limit": limit,
                "encoding": encoding,
            }
        })
        return response

    def platform_get_utxos(self, addresses: list[str], source_chain: str, limit=1024, encoding="cb58"):
        response = requests.post(self.p_chain_rpc_url, json={
            "jsonrpc":"2.0",
            "id"     : 1,
            "method" :"platform.getUTXOs",
            "params" :{
                "addresses": addresses,
                "sourceChain": source_chain,
                "limit": limit,
                "encoding": encoding,
            }
        })
        return response


    def avm_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.x_chain_rpc_url, json={
            "jsonrpc":"2.0",
            "id"     : 1,
            "method" :"avm.issueTx",
            "params" :{
                "tx": tx,
                "encoding": encoding
            }
        })
        return response

    def platform_issue_tx(self, tx: str, encoding="cb58"):
        response = requests.post(self.p_chain_rpc_url, json={
            "jsonrpc":"2.0",
            "id"     : 1,
            "method" :"platform.issueTx",
            "params" :{
                "tx": tx,
                "encoding": encoding
            }
        })
        return response
