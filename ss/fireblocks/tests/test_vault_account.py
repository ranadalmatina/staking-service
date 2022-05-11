from django.db import IntegrityError
from django.test import TestCase

from fireblocks.factories import VaultAccountFactory
from fireblocks.models import VaultAccount


class VaultAccountTestCase(TestCase):

    def test_unique_id(self):
        VaultAccount.objects.create(vault_id=55, name='Test 1')

        # Should be unable to create a duplicate address
        with self.assertRaises(IntegrityError):
            VaultAccount.objects.create(vault_id=55, name='Test 2')

    def test_unique_id_str_int1(self):
        VaultAccount.objects.create(vault_id=1, name='Test 1')

        # Should be unable to create a duplicate address
        with self.assertRaises(IntegrityError):
            VaultAccount.objects.create(vault_id='1', name='Test 2')

    def test_unique_id_str_int2(self):
        VaultAccount.objects.create(vault_id=999, name='Test 1')

        # Should be unable to create a duplicate address
        with self.assertRaises(IntegrityError):
            VaultAccount.objects.create(vault_id='999', name='Test 2')

    def test_unique_id_factory(self):
        VaultAccountFactory(vault_id=1)

        # Should be unable to create a duplicate address
        with self.assertRaises(IntegrityError):
            VaultAccount.objects.create(vault_id='1', name='Test 2')

    def test_vault_account_factory_uniqueness(self):
        account1 = VaultAccountFactory(vault_id=999)
        account1.refresh_from_db()  # Without this line we get an error
        account2 = VaultAccount.objects.get(vault_id='999')
        self.assertEqual(account1, account2)
