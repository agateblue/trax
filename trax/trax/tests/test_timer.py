import unittest
import json
import datetime
from test_plus.test import TestCase

from trax.trax import models
from django.utils import timezone
from django.forms import ValidationError
from trax.users.models import User


class TestTimer(TestCase):

    def setUp(self):
        self.user = self.make_user()

    def test_can_start_timer_group(self):
        now = timezone.now()
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            group = models.TimerGroup.objects.start('Test 2', user=self.user)

        self.assertEqual(group.name, 'Test 2')
        self.assertEqual(group.slug, 'test-2')
        self.assertEqual(group.user, self.user)

        timer = group.timers.first()

        self.assertGreaterEqual(timer.start_date, now)
        self.assertEqual(timer.end_date, None)

    def test_can_stop_timer_group(self):
        group = models.TimerGroup.objects.start('Test 2', user=self.user)
        group.stop()
        timer = group.timers.first()

        self.assertGreater(timer.end_date, timer.start_date)

    def test_starting_another_timer_for_same_user_stop_previous_one(self):
        group1 = models.TimerGroup.objects.start('test1', user=self.user)
        group2 = models.TimerGroup.objects.start('test2', user=self.user)

        timer1 = group1.timers.first()
        timer2 = group2.timers.first()

        self.assertGreater(timer1.end_date, timer1.start_date)
        self.assertGreater(timer2.start_date, timer1.end_date)

    def test_can_get_group_today_duration(self):
        now = timezone.now()
        delta = datetime.timedelta(hours=1)
        with unittest.mock.patch('django.utils.timezone.now', return_value=now - delta):
            group = models.TimerGroup.objects.start('Test 2', user=self.user)

        self.assertEqual(group.creation_date, now - delta)
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            self.assertEqual(group.today_duration, delta)

    def test_cannot_stop_timer_with_end_date_smaller_than_start_date(self):
        now = timezone.now().replace(microsecond=0)
        start = now - datetime.timedelta(hours=2)
        invalid = start - datetime.timedelta(hours=3)

        with unittest.mock.patch('django.utils.timezone.now', return_value=start):
            group = models.TimerGroup.objects.start('Test 1', user=self.user)

        with self.assertRaises(ValidationError):
            group.stop(invalid)

    def test_timers_cannot_overlap(self):
        now = timezone.now().replace(microsecond=0)
        start = now - datetime.timedelta(hours=2)

        group1 = models.TimerGroup.objects.start('Test 1', user=self.user)
        group2 = models.TimerGroup.objects.create(name='Test 2', slug='test', user=self.user)

        with self.assertRaises(ValidationError):
            group2.timers.create()
