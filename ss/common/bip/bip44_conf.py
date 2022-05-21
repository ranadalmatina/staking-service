# Imports
from bip_utils.addr import AvaxPChainAddrEncoder, AvaxXChainAddrEncoder, EthAddrEncoder

from bip_utils.bip.bip32 import Bip32Const, Bip32KeyNetVersions, Bip32Secp256k1
from bip_utils.bip.conf.common import BipCoinConf, NOT_HARDENED_DEF_PATH
from .address import FujiPChainAddrEncoder, FujiXChainAddrEncoder
from .coin_conf import CoinsConf

# Bitcoin key net version for main net (same as BIP32)
_BIP44_BTC_KEY_NET_VER_MAIN: Bip32KeyNetVersions = Bip32Const.MAIN_NET_KEY_NET_VERSIONS
# Bitcoin key net version for test net (same as BIP32)
_BIP44_BTC_KEY_NET_VER_TEST: Bip32KeyNetVersions = Bip32Const.TEST_NET_KEY_NET_VERSIONS


class Bip44Conf:
    """Class container for Bip44 configuration."""

    # Configuration for Avax C-Chain
    AvaxCChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.AvaxCChain.CoinNames(),
        coin_idx=60,
        is_testnet=False,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_MAIN,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=EthAddrEncoder,
        addr_params={},
    )
    # Configuration for Avax P-Chain
    AvaxPChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.AvaxPChain.CoinNames(),
        coin_idx=9000,
        is_testnet=False,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_MAIN,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=AvaxPChainAddrEncoder,
        addr_params={},
    )
    # Configuration for Avax X-Chain
    AvaxXChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.AvaxXChain.CoinNames(),
        coin_idx=9000,
        is_testnet=False,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_MAIN,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=AvaxXChainAddrEncoder,
        addr_params={},
    )

    # Configuration for Fireblocks Testnet Workspace C-Chain
    FireblocksCChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiCChain.CoinNames(),
        coin_idx=1,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_MAIN,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=EthAddrEncoder,
        addr_params={},
    )
    # Configuration for Fireblocks Testnet Workspace P-Chain
    FireblocksPChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiPChain.CoinNames(),
        coin_idx=1,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_TEST,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=FujiPChainAddrEncoder,
        addr_params={},
    )
    # Configuration for Fireblocks Testnet Workspace X-Chain
    FireblocksXChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiXChain.CoinNames(),
        coin_idx=1,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_TEST,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=FujiXChainAddrEncoder,
        addr_params={},
    )

    # Configuration for Avax Testnet C-Chain
    FujiCChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiCChain.CoinNames(),
        coin_idx=60,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_TEST,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=EthAddrEncoder,
        addr_params={},
    )
    # Configuration for Avax Testnet P-Chain
    FujiPChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiPChain.CoinNames(),
        coin_idx=9000,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_TEST,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=FujiPChainAddrEncoder,
        addr_params={},
    )
    # Configuration for Avax Testnet X-Chain
    FujiXChain: BipCoinConf = BipCoinConf(
        coin_names=CoinsConf.FujiXChain.CoinNames(),
        coin_idx=9000,
        is_testnet=True,
        def_path=NOT_HARDENED_DEF_PATH,
        key_net_ver=_BIP44_BTC_KEY_NET_VER_TEST,
        wif_net_ver=None,
        bip32_cls=Bip32Secp256k1,
        addr_cls=FujiXChainAddrEncoder,
        addr_params={},
    )
