class FireblocksException(Exception):
    """
    Base exception class for all exceptions raised by the Fireblocks app.
    """
    pass


class ExternalWalletAssetAlreadyExists(FireblocksException):
    """
    Raised when we have already created an address for a given asset in a given wallet.
    """
    pass


class IllegalWithdrawalState(FireblocksException):
    """
    Raised when an attempt is made to execute a Withdrawal that has not been changed to "SENT" state.
    """
    pass


class BroadcastFailed(FireblocksException):
    """
    Raised after getting an error while attempting to broadcast a withdrawal transaction.
    """
    pass


class FireblocksWalletCreationException(FireblocksException):
    """
    Raised if we do not get the expected response when attempting to create a FireblocksWallet
    (a new asset in a vault).
    """
    pass
