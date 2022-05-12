"""Module for BIP44 coins enum."""

# Imports
from enum import auto, unique
from bip_utils.bip.conf.common.bip_coins import BipCoins


@unique
class Bip44Coins(BipCoins):
    """Enumerative for supported BIP44 coins."""

    # Main nets
    AVAX_C_CHAIN = auto()
    AVAX_P_CHAIN = auto()
    AVAX_X_CHAIN = auto()
    # Test nets
    FUJI_C_CHAIN = auto()
    FUJI_P_CHAIN = auto()
    FUJI_X_CHAIN = auto()
    # Fireblocks Testnet
    FB_C_CHAIN = auto()
