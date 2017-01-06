import unittest
import datetime

from test_plus.test import TestCase
from django.conf import settings
from django.utils import timezone

from trax.trax import models, tasks


class TestTasks(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_can_kill_obsolete_timers(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=2)
        with unittest.mock.patch('django.utils.timezone.now', return_value=yesterday):
            group1 = models.TimerGroup.objects.start('Test 1', user=self.user)

        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            tasks.kill_obsolete_timers()

        group1.refresh_from_db()

        self.assertFalse(group1.is_started)
        self.assertEqual(group1.timers.first().end_date, now)

    @unittest.mock.patch('requests.Session.send')
    def test_can_send_reminder(self, r):
        r.return_value = unittest.mock.Mock(status=200)
        now = timezone.now()
        one_minute = now + datetime.timedelta(minutes=1)
        two_minute = now + datetime.timedelta(minutes=2)

        reminder1 = models.Reminder.objects.create(
            user=self.user,
            next_call=one_minute,
            message='Hello, how are you ?',
            channel_id='channel_id',
            channel_name='channel_name',
        )
        reminder2 = models.Reminder.objects.create(
            user=self.user,
            next_call=two_minute,
            message='not send',
            channel_id='channel_id',
            channel_name='channel_name',
        )

        with unittest.mock.patch('django.utils.timezone.now', return_value=one_minute):
            tasks.send_reminders()

        reminder1.refresh_from_db()
        reminder2.refresh_from_db()

        self.assertEqual(reminder1.completed_on, one_minute)
        self.assertEqual(reminder1.next_call, None)
        self.assertEqual(reminder2.completed_on, None)
        self.assertEqual(reminder2.next_call, two_minute)
