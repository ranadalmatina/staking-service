from web3 import Web3
from web3.middleware import geth_poa_middleware
from functools import cached_property


class AvaWeb3:
    """
    Avalanche Go RPC client.
    """
    C_CHAIN = "/ext/bc/C/rpc"
    url = None

    def __init__(self, RPC_URL=None):
        if RPC_URL is None:
            raise Exception("RPC URL is not set")
        self.url = RPC_URL

    @property
    def rpc_url(self):
        return f'{self.url}{self.C_CHAIN}'

    @cached_property
    def web3(self):
        client = Web3(Web3.HTTPProvider(self.rpc_url))
        client.middleware_onion.inject(geth_poa_middleware, layer=0)
        return client

    def get_balance(self, address):
        from_address = self.web3.toChecksumAddress(address)
        amount = self.web3.fromWei(
            self.web3.eth.get_balance(from_address), 'ether')
        return amount

    def get_nonce(self, address):
        from_address_hex = self.web3.toChecksumAddress(address)
        nonce = self.web3.eth.getTransactionCount(from_address_hex)
        print(f'Nonce is {nonce}')
        return nonce
