"""
This code is directly ported from Fireblocks Javascript front end.
It might contain bugs or need to be patched as things change.
"""


def _clean_tx_hash(e):
    if e:
        parts = e.split('-')
        if len(parts) > 0:
            n = len(parts) - 1
            try:
                r = int(parts[n])
            except ValueError:
                pass
            else:
                return (parts[0, n].join('') + str(r)).replace('.', '')
    return e


def _get_link(asset_id: str, tx_hash: str) -> str:
    if tx_hash:
        link_map = {
            'xrp_test': f'https://test.bithomp.com/explorer/{tx_hash}',
            'xrp': f'https://bithomp.com/explorer/{tx_hash}',
            'etc': f'https://etcblockexplorer.com/tx/{tx_hash}',
            'etc_test': f'https://mordor.etccoopexplorer.com/tx/{tx_hash}/internal_transactions',
            'eth_test': f'https://ropsten.etherscan.io/tx/{tx_hash}',
            'eth_test2': f'https://kovan.etherscan.io/tx/{tx_hash}',
            'eth': f'https://etherscan.io/tx/{tx_hash}',
            'ltc_test': f'https://chain.so/tx/LTCTEST/{tx_hash}',
            'btc_test': f'https://chain.so/tx/BTCTEST/{tx_hash}',
            'btc': f'https://blockchair.com/bitcoin/transaction/{tx_hash}',
            'ltc': f'https://blockchair.com/litecoin/transaction/{tx_hash}',
            'xlm': f'https://stellar.expert/explorer/public/tx/{tx_hash}',
            'xlm_test': f'https://stellar.expert/explorer/testnet/tx/{tx_hash}',
            'dash': f'https://blockchair.com/dash/transaction/{tx_hash}',
            'dash_test': f'https://sochain.com/tx/DASHTEST/{tx_hash}',
            'bsv': f'https://blockchair.com/bitcoin-sv/transaction/{tx_hash}',
            'bsv_test': f'https://testnet.bitcoincloud.net/tx/{tx_hash}',
            'bch': f'https://blockchair.com/bitcoin-cash/transaction/{tx_hash}',
            'bcha': f'https://blockchair.com/bitcoin-abc/transaction/{tx_hash}',
            'bch_test': f'https://www.blockchain.com/bch-testnet/tx/{tx_hash}',
            'bcha_test': f'https://www.blockchain.com/bch-testnet/tx/{tx_hash}',
            'eos': f'https://bloks.io/transaction/{tx_hash}',
            'eos_test': f'https://jungle.bloks.io/transaction/{tx_hash}',
            'usdt_omni': f'https://blockexplorer.one/omni/mainnet/tx/{tx_hash}',
            'pcust': f'https://omniexplorer.info/search/{tx_hash}',
            'omni_test': f'https://blockexplorer.one/omni/testnet/tx/{tx_hash}',
            'zec': f'https://blockchair.com/zcash/transaction/{tx_hash}',
            'zec_test': f'https://chain.so/tx/ZECTEST/{tx_hash}',
            'hbar': f'https://app.dragonglass.me/hedera/transactions//{_clean_tx_hash(tx_hash)}',
            'hbar_test': f'https://testnet.dragonglass.me/hedera/transactions//{_clean_tx_hash(tx_hash)}',
            'dot': f'https://polkascan.io/polkadot/transaction/{tx_hash}',
            'wnd': f'https://westend.subscan.io/extrinsic/{tx_hash}',
            'xem': f'http://chain.nem.ninja/#/transfer/{tx_hash}',
            'xem_test': f'http://chain.nem.ninja/#/transfer/{tx_hash}',
        }
        if asset_id in link_map:
            return link_map[asset_id]
    return None


def get_explorer_link(asset_id: str, tx_hash: str) -> str:
    return _get_link(asset_id.lower(), tx_hash)
