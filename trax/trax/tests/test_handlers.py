import unittest
import datetime

from test_plus.test import TestCase
from django.conf import settings
from django.utils import timezone

from trax.trax import models, forms, handlers
from trax.users.models import User


class TestForms(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_start_timer_handler(self):
        handler = handlers.handlers_by_key['start']
        arguments = 'this is my timer'

        now = timezone.now()
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            result = handler.handle(arguments, user=self.user)

        group = result['timer_group']

        self.assertEqual(group.name, 'this is my timer')
        self.assertEqual(group.slug, 'this-is-my-timer')
        self.assertEqual(group.user, self.user)

        timer = group.timers.first()

        self.assertGreaterEqual(timer.start_date, now)
        self.assertEqual(timer.end_date, None)

    def test_can_start_using_an_integer_shortcut(self):
        handler = handlers.handlers_by_key['start']
        group1 = models.TimerGroup.objects.start('Test 1', user=self.user)
        group1 = models.TimerGroup.objects.start('Test 1', user=self.user)
        group2 = models.TimerGroup.objects.start('Test 2', user=self.user)

        arguments = '1'
        result = handler.handle(arguments, user=self.user)

        self.assertEqual(result['timer_group'], group1)
        self.assertTrue(group1.is_started)

    def test_stop_timer(self):
        handler = handlers.handlers_by_key['stop']
        group = models.TimerGroup.objects.start('Test 2', user=self.user)

        self.assertTrue(group.is_started)

        result = handler.handle('', user=self.user)
        timer = group.timers.first()

        self.assertFalse(group.is_started)
        self.assertFalse(timer.is_started)

    def test_can_stop_timer_in_the_past(self):
        handler = handlers.handlers_by_key['stop']
        now = timezone.now().replace(microsecond=0)
        start = now - datetime.timedelta(hours=2)
        with unittest.mock.patch('django.utils.timezone.now', return_value=start):
            group = models.TimerGroup.objects.start('Test 2', user=self.user)

        timer = group.current_timer

        self.assertEqual(timer.start_date, start)

        now = start + datetime.timedelta(hours=2)
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            result = handler.handle('one hour ago', user=self.user)

        timer.refresh_from_db()
        difference = timer.end_date - (timer.start_date + datetime.timedelta(hours=1))
        self.assertEqual(difference.seconds, 0)

    def test_list_timers(self):
        handler = handlers.handlers_by_key['list']
        group = models.TimerGroup.objects.start('Test 2', user=self.user)

        result = handler.handle('', user=self.user)
        self.assertEqual(len(result['timer_groups']), 1)
        self.assertEqual(result['timer_groups'].first(), group)

    def test_stats_handler(self):
        handler = handlers.handlers_by_key['stats']
        group1 = models.TimerGroup.objects.start('Test 1', user=self.user)
        group2 = models.TimerGroup.objects.start('Test 2', user=self.user)
        empty_group = models.TimerGroup.objects.create(
            name='Empty', slug='empty', user=self.user)

        result = handler.handle('', user=self.user)
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(result['rows'][0]['label'], 'Test 1')
        self.assertEqual(result['rows'][1]['label'], 'Test 2')

    def test_restart_handler(self):
        group1 = models.TimerGroup.objects.start('Test 1', user=self.user)
        group2 = models.TimerGroup.objects.start('Test 2', user=self.user)
        group2.stop()

        handler = handlers.handlers_by_key['restart']
        result = handler.handle('', user=self.user)

        group2.refresh_from_db()
        self.assertTrue(group2.is_started)

    def test_config_handler(self):
        self.user.delete()
        with self.settings(TIME_ZONE='Europe/Berlin'):
            user = self.make_user()
            tz = user.preferences['global__timezone']
        self.assertEqual(tz, 'Europe/Berlin')

        handler = handlers.handlers_by_key['config']
        result = handler.handle('timezone Europe/Paris', user=user)

        self.assertEqual(user.preferences['global__timezone'], 'Europe/Paris')
