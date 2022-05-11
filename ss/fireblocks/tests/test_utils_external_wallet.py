from unittest import mock

from django.test import TestCase

from ..factories import ExternalWalletAssetFactory, ExternalWalletFactory, VaultAssetFactory
from ..models import ExternalWallet, ExternalWalletAsset
from ..utils.external_wallet import (_create_external_wallet, _create_external_wallet_asset,
                                     _get_empty_external_wallet, get_external_wallet_asset)


class ExternalWalletUtilsTestCase(TestCase):

    @mock.patch('fireblocks.utils.external_wallet.get_fireblocks_client')
    def test_create_external_wallet(self, mock_get_fb_client):
        create_external_wallet_response = {
            'id': 'dfbf22c0-d586-ed60-d7fd-8e99c54e728c',
            'name': 'trader 3187996092687990783 wallet',
            'assets': [],
        }
        mock_get_fb_client.return_value.create_external_wallet.return_value = create_external_wallet_response

        self.assertEqual(ExternalWallet.objects.count(), 0)
        ew = _create_external_wallet(name="Contract")
        self.assertEqual(ExternalWallet.objects.count(), 1)
        self.assertEqual(ew.name, 'trader 3187996092687990783 wallet')


class GetEmptyWalletTestCase(TestCase):

    @mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
    def test_get_empty_external_wallet_none_exist(self, mock_create_external_wallet):
        mock_create_external_wallet.side_effect = lambda name: ExternalWalletFactory(name=name)
        vault_asset = VaultAssetFactory(asset_id='BTC')
        # No wallets exist, thus one will be created
        self.assertEqual(ExternalWallet.objects.count(), 0)
        ew = _get_empty_external_wallet(name="Contract", vault_asset=vault_asset)
        self.assertEqual(ExternalWallet.objects.count(), 1)
        self.assertIsInstance(ew, ExternalWallet)
        # create_external_wallet is called
        self.assertTrue(mock_create_external_wallet.called)

    @mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
    def test_get_empty_external_wallet_one_exists(self, mock_create_external_wallet):
        vault_asset = VaultAssetFactory(asset_id='BTC')
        # We are going to fetch this empty wallet
        ExternalWalletFactory(name="Contract")
        self.assertEqual(ExternalWallet.objects.count(), 1)
        ew = _get_empty_external_wallet(name="Contract", vault_asset=vault_asset)
        self.assertEqual(ExternalWallet.objects.count(), 1)
        self.assertEqual(ew.name, "Contract")
        self.assertFalse(mock_create_external_wallet.called)

    @mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
    def test_get_empty_external_wallet_existing(self, mock_create_external_wallet):
        vault_asset = VaultAssetFactory(asset_id='BTC')
        wallet = ExternalWalletFactory(name="Wonderland")
        ExternalWalletFactory(name="Wonderland")
        ExternalWalletAssetFactory(wallet=wallet, asset=vault_asset)  # First wallet already contains BTC
        # Two wallets exist, one already contains BTC, thus we will get the other
        self.assertEqual(ExternalWallet.objects.count(), 2)
        ew = _get_empty_external_wallet(name="Wonderland", vault_asset=vault_asset)
        self.assertEqual(ExternalWallet.objects.count(), 2)
        self.assertEqual(ew.name, "Wonderland")
        self.assertFalse(mock_create_external_wallet.called)

    @mock.patch('fireblocks.utils.external_wallet._create_external_wallet')
    def test_get_empty_external_wallet(self, mock_create_external_wallet):
        asset_btc = VaultAssetFactory(asset_id='BTC')
        asset_eth = VaultAssetFactory(asset_id='ETH')
        wallet_0 = ExternalWalletFactory(name="Contract")
        wallet_1 = ExternalWalletFactory(name="Fees")
        ExternalWalletAssetFactory(wallet=wallet_0, asset=asset_btc)  # Wallet 0 already contains BTC
        ExternalWalletAssetFactory(wallet=wallet_1, asset=asset_eth)  # Wallet 1 does not contain BTC
        self.assertEqual(ExternalWallet.objects.count(), 2)

        ew = _get_empty_external_wallet(name="Fees", vault_asset=asset_btc)
        self.assertEqual(ExternalWallet.objects.count(), 2)
        self.assertEqual(ew.id, str(wallet_1.id))
        self.assertEqual(ew.name, 'Fees')
        self.assertFalse(mock_create_external_wallet.called)

        # This should return the opposite wallet if we filter for ETH instead
        ew = _get_empty_external_wallet(name="Contract", vault_asset=asset_eth)
        self.assertEqual(ExternalWallet.objects.count(), 2)
        self.assertEqual(ew.id, str(wallet_0.id))
        self.assertEqual(ew.name, 'Contract')
        self.assertFalse(mock_create_external_wallet.called)


class ExternalWalletAssetUtilsTestCase(TestCase):

    @mock.patch('fireblocks.utils.external_wallet.get_fireblocks_client')
    def test_create_external_wallet_asset(self, mock_get_fb_client):
        wallet = ExternalWalletFactory()
        asset = VaultAssetFactory(asset_id='BTC_TEST')
        address = 'mgbaC5SKZtMxBiimSVbVyvTxZQUxahVSkr'

        # create_external_wallet_asset_response
        mock_get_fb_client.return_value.create_external_wallet_asset.return_value = {
            'id': 'BTC_TEST',
            'balance': 0,
            'lockedAmount': 0,
            'status': 'WAITING_FOR_APPROVAL',
        }

        self.assertEqual(ExternalWalletAsset.objects.count(), 0)
        external_asset = _create_external_wallet_asset(wallet=wallet, vault_asset=asset, address=address)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertEqual(external_asset.status, ExternalWalletAsset.STATUS.WAITING_FOR_APPROVAL)
        self.assertEqual(external_asset.address, address)
        self.assertEqual(external_asset.asset, asset)
        self.assertEqual(external_asset.wallet, wallet)

    @mock.patch('fireblocks.utils.external_wallet._create_external_wallet_asset')
    def test_get_external_wallet_asset(self, mock_create_external_wallet_asset):
        wallet = ExternalWalletFactory()
        asset = VaultAssetFactory(asset_id='BTC_TEST')
        address = 'mgbaC6SKZtMxBiimSVbVyvTxZQUxahVSkj'

        existing_external_asset = ExternalWalletAssetFactory(wallet=wallet, asset=asset, address=address)

        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        external_asset = get_external_wallet_asset(vault_asset=asset, address=address)
        self.assertEqual(ExternalWalletAsset.objects.count(), 1)
        self.assertFalse(mock_create_external_wallet_asset.called)
        self.assertEqual(existing_external_asset.id, external_asset.id)
