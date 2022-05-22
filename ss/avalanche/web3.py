from web3 import Web3
from web3.middleware import geth_poa_middleware


class AvaWeb3:
    """
    Avalanche Go RPC client.
    """
    AVAX_HTTP = "https://api.avax.network"
    FUJI_HTTP = "https://api.avax-test.network"
    C_CHAIN = "/ext/bc/C/rpc"

    def __init__(self, fuji=True):
        self.fuji = fuji

    @property
    def rpc_url(self):
        url = self.FUJI_HTTP if self.fuji else self.AVAX_HTTP
        return f'{url}{self.C_CHAIN}'

    @property
    def web3(self):
        client = Web3(Web3.HTTPProvider(self.rpc_url))
        client.middleware_onion.inject(geth_poa_middleware, layer=0)
        return client

    def get_balance(self, address):
        from_address = self.web3.toChecksumAddress(address)
        amount = self.web3.fromWei(self.web3.eth.get_balance(from_address), 'ether')
        return amount

    def get_nonce(self, address):
        from_address_hex = self.web3.toChecksumAddress(address)
        nonce = self.web3.eth.getTransactionCount(from_address_hex)
        print(f'Nonce is {nonce}')
        return nonce
