from bip_utils.coin_conf.coin_conf import CoinConf
from bip_utils.utils.conf import CoinNames


class CoinsConf:
    """Class container for coins configuration."""

    # Configuration for Avax C-Chain
    AvaxCChain: CoinConf = CoinConf(
        coin_name=CoinNames("Avax C-Chain", "AVAX"),
        params={},
    )

    # Configuration for Avax P-Chain
    AvaxPChain: CoinConf = CoinConf(
        coin_name=CoinNames("Avax P-Chain", "AVAX"),
        params={
            "addr_hrp": "avax",
            "addr_prefix": "P-",
        },
    )

    # Configuration for Avax X-Chain
    AvaxXChain: CoinConf = CoinConf(
        coin_name=CoinNames("Avax X-Chain", "AVAX"),
        params={
            "addr_hrp": "avax",
            "addr_prefix": "X-",
        },
    )

    # Configuration for Avax Testnet C-Chain
    FujiCChain: CoinConf = CoinConf(
        coin_name=CoinNames("Fuji C-Chain", "AVAX"),
        params={},
    )

    # Configuration for Avax Testnet P-Chain
    FujiPChain: CoinConf = CoinConf(
        coin_name=CoinNames("Fuji P-Chain", "AVAX"),
        params={
            "addr_hrp": "fuji",
            "addr_prefix": "P-",
        },
    )

    # Configuration for Avax Testnet X-Chain
    FujiXChain: CoinConf = CoinConf(
        coin_name=CoinNames("Fuji X-Chain", "AVAX"),
        params={
            "addr_hrp": "fuji",
            "addr_prefix": "X-",
        },
    )
