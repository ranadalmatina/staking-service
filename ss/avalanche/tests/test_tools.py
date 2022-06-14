from decimal import Decimal

from django.test import TestCase

from ..tools import from_nano_avax, to_nano_avax


class ToolsTestCase(TestCase):

    def test_to_nano_avax(self):
        one_billion_nano = Decimal("1000000000")
        avax = from_nano_avax(amount=one_billion_nano)
        self.assertEqual(avax, Decimal('1'))

    def test_from_nano_avax(self):
        axax = Decimal("1.234567")
        nano = to_nano_avax(amount=axax)
        self.assertEqual(nano, Decimal("1234567000"))
