import logging
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.aiohttp import log as requests_logger

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

    def contract_avax_deficit(self):
      # TODO: Handle errors described here https://gql.readthedocs.io/en/latest/advanced/error_handling.html
        result = self.client.execute(deficit_query)
        if result:
            return result['deficitTotal']['avaxAmount']
        return 0
