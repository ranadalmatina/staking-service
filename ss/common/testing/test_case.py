from datetime import datetime
from uuid import UUID

import arrow
import pytz

from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def assert_is_valid_UUID(self, uuid_to_test, version=4):
        """
        Check if uuid_to_test is a valid UUID.

        Parameters
        ----------
        uuid_to_test : str
        version : {1, 2, 3, 4}

        Returns
        -------
        `True` if uuid_to_test is a valid UUID, otherwise `False`.
        """
        uuid_obj = UUID(uuid_to_test, version=version)
        self.assertEqual(str(uuid_obj), uuid_to_test)

    def assert_is_timestamp(self, timestamp_int):
        """
        Check if timestamp_int is a valid timestamp as used by Fireblocks.
        """
        self.assertIsInstance(timestamp_int, int)
        converted = datetime.fromtimestamp(timestamp_int / 1000, tz=pytz.utc)
        self.assertIsInstance(converted, datetime)

    def assert_is_iso_8601(self, datetime_string):
        """
        Check if datetime_string is a valid ISO 8601 string.
        """
        self.assertIsInstance(datetime_string, str)
        self.assertIn('T', datetime_string)
        converted = arrow.get(datetime_string).datetime
        self.assertIsInstance(converted, datetime)
