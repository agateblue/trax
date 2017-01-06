import unittest
import datetime

from test_plus.test import TestCase
from django.conf import settings
from django.utils import timezone

from trax.trax import models, tasks


class TestCommands(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_can_kill_obsolete_timers(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        with unittest.mock.patch('django.utils.timezone.now', return_value=yesterday):
            group1 = models.TimerGroup.objects.start('Test 1', user=self.user)

        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            tasks.kill_obsolete_timers()

        group1.refresh_from_db()

        self.assertFalse(group1.is_started)
        self.assertEqual(group1.timers.first().end_date, now)
