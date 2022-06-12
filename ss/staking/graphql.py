import logging
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.aiohttp import log as requests_logger
from web3 import Web3
from web3.types import Wei

requests_logger.setLevel(logging.WARNING)

deficit_query = gql("""
query {
  deficitTotal(id:"deficit-singleton") {
    avaxAmount
  }
}
""")


class GraphAPI:

    def __init__(self, url):
        transport = AIOHTTPTransport(url=url)
        self.client = Client(transport=transport,
                             fetch_schema_from_transport=False)
        requests_logger.setLevel(logging.WARNING)

    def contract_avax_deficit(self) -> Wei:
      # TODO: Handle errors described here https://gql.readthedocs.io/en/latest/advanced/error_handling.html
        result = self.client.execute(deficit_query)
        if result:
            amount = result['deficitTotal']['avaxAmount']
            # Amount is in Wei, but as a string. Converting using Wei() doesn't work for some reason.
            return Web3.toWei(amount, 'wei')
        return 0
