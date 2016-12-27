import unittest
import datetime
from test_plus.test import TestCase

from trax.trax import models, forms, handlers
from trax.users.models import User
from django.conf import settings

from trax.trax import utils


class TestForms(TestCase):

    def test_humanize_timedelta(self):
        tests = [
            (datetime.timedelta(hours=1, minutes=10), '1 hours, 10 minutes'),
            (datetime.timedelta(hours=5, minutes=10), '5 hours, 10 minutes'),
            (datetime.timedelta(minutes=1, seconds=30), '1 minutes, 30 seconds'),
        ]

        for d, expected in tests:
            self.assertEqual(utils.humanize_timedelta(d), expected)
