# Imports
from typing import Dict
from bip_utils.bip.conf.common import BipCoinConf
from bip_utils.bip.conf.common import BipCoins
from .bip44_coins import Bip44Coins
from .bip44_conf import Bip44Conf

class Bip44ConfGetterConst:
    """Class container for Bip44 configuration getter constants."""

    # Map from Bip44Coins to configuration classes
    COIN_TO_CONF: Dict[Bip44Coins, BipCoinConf] = {
        Bip44Coins.AVAX_C_CHAIN: Bip44Conf.AvaxCChain,
        Bip44Coins.AVAX_P_CHAIN: Bip44Conf.AvaxPChain,
        Bip44Coins.AVAX_X_CHAIN: Bip44Conf.AvaxXChain,
        Bip44Coins.FUJI_C_CHAIN: Bip44Conf.FujiCChain,
        Bip44Coins.FUJI_P_CHAIN: Bip44Conf.FujiPChain,
        Bip44Coins.FUJI_X_CHAIN: Bip44Conf.FujiXChain,
        Bip44Coins.FB_C_CHAIN: Bip44Conf.FireblocksCChain,

    }


class Bip44ConfGetter:
    """
    Bip44 configuration getter class.
    It allows to get the Bip44 configuration of a specific coin.
    """

    @staticmethod
    def GetConfig(coin_type: BipCoins) -> BipCoinConf:
        """
        Get coin configuration.
        Args:
            coin_type (BipCoins): Coin type
        Returns:
            BipCoinConf: Coin configuration
        Raises:
            TypeError: If coin type is not of a Bip44Coins enumerative
        """
        if not isinstance(coin_type, Bip44Coins):
            raise TypeError("Coin type is not an enumerative of Bip44Coins")
        return Bip44ConfGetterConst.COIN_TO_CONF[Bip44Coins(coin_type)]
