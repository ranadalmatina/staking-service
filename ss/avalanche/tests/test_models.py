from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..factories import AtomicTxFactory, ChainSwapFactory
from ..models import AtomicTx, ChainSwap


class ModelTestCase(TestCase):

    def test_atomic_tx_factory(self):
        tx = AtomicTxFactory()
        self.assertEqual(tx.status, AtomicTx.STATUS.NEW)
        tx.full_clean()

    def test_atomic_tx_negative_amount(self):
        amount = Decimal('-1.2345')
        tx = AtomicTxFactory(amount=amount)
        with self.assertRaises(ValidationError) as ex:
            tx.full_clean()
        self.assertIn('amount', ex.exception.message_dict)

    def test_chain_swap_factory(self):
        swap = ChainSwapFactory()
        self.assertEqual(swap.source_chain, 'P')
        self.assertEqual(swap.status, ChainSwap.STATUS.NEW)
        swap.full_clean()

    def test_chain_swap_factory_invalid_chain(self):
        swap = ChainSwapFactory(source_chain='G')
        with self.assertRaises(ValidationError) as ex:
            swap.full_clean()
        self.assertIn('source_chain', ex.exception.message_dict)

    def test_chain_swap_export_failure(self):
        swap = ChainSwapFactory()
        self.assertFalse(swap.export_failed())
        self.assertFalse(swap.import_failed())
        self.assertFalse(swap.should_fail())
        export_tx = AtomicTxFactory(status=AtomicTx.STATUS.FAILED)
        swap.export_tx = export_tx
        swap.save()
        self.assertTrue(swap.export_failed())
        self.assertFalse(swap.import_failed())
        self.assertTrue(swap.should_fail())

    def test_chain_swap_import_failure(self):
        import_tx = AtomicTxFactory()
        swap = ChainSwapFactory(import_tx=import_tx)
        self.assertTrue(swap.export_exists())
        self.assertTrue(swap.import_exists())
        self.assertFalse(swap.export_failed())
        self.assertFalse(swap.import_failed())
        self.assertFalse(swap.should_fail())
        import_tx = AtomicTxFactory(status=AtomicTx.STATUS.FAILED)
        swap.import_tx = import_tx
        swap.save()
        self.assertFalse(swap.export_failed())
        self.assertTrue(swap.import_failed())
        self.assertTrue(swap.should_fail())
