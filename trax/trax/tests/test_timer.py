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

    def test_can_start_timer_via_api_endpoint(self):
        payload = {
            'channel_id': 'cniah6qa73bjjjan6mzn11f4ie',
            'channel_name': 'town-square',
            'command': '/trax',
            'text': 'start This is my timer',
            'team_domain': 'testteam',
            'team_id': 'rdc9bgriktyx9p4kowh3dmgqyc',
            'token': 'TESTTOKEN',
            'user_id': 'testid',
            'user_name': 'thisisme',
        }

        expected = {
          "response_type": "ephemeral",
          "text": """Timer "This is my timer" was started."""
        }

        url = self.reverse('trax:slash-command')
        now = timezone.now()
        response = self.client.post(url, payload)
        json_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data, expected)

        user = User.objects.get(username='thisisme', external_id='testid')

        self.assertFalse(user.is_active)

        group = models.TimerGroup.objects.latest('id')

        self.assertEqual(group.name, 'This is my timer')
        self.assertEqual(group.slug, 'this-is-my-timer')
        self.assertEqual(group.user, user)

        timer = group.timers.first()

        self.assertGreater(timer.start_date, now)
        self.assertEqual(timer.end_date, None)
