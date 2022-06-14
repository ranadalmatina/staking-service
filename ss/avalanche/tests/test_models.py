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
