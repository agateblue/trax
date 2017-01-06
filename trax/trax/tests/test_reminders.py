import unittest
import datetime
import requests

from test_plus.test import TestCase
from dynamic_preferences.registries import global_preferences_registry

from trax.trax import models
from django.utils import timezone
from django.forms import ValidationError
from trax.users.models import User


class TestTimer(TestCase):

    def setUp(self):
        self.user = self.make_user()
        # self.preferences = global_preferences_registry.manager()
        # self.preferences['trax__slash_command_token'] = 'good_token'

    def test_can_create_reminder(self):

        now = timezone.now()
        one_minute = now + datetime.timedelta(minutes=1)

        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            reminder = models.Reminder.objects.create(
                user=self.user,
                next_call=one_minute,
                message='Hello, how are you ?',
                channel_id='channel_id',
                channel_name='channel_name',
            )
        self.assertEqual(reminder.creation_date, now)
        self.assertEqual(reminder.completed_on, None)

    @unittest.mock.patch('requests.Session.send')
    def test_can_check_can_send_reminder(self, r):
        r.return_value = unittest.mock.Mock(status=200)
        now = timezone.now()
        one_minute = now + datetime.timedelta(minutes=1)

        reminder = models.Reminder.objects.create(
            user=self.user,
            next_call=one_minute,
            message='Hello, how are you ?',
            channel_id='channel_id',
            channel_name='channel_name',
        )
        with self.assertRaises(ValueError):
            reminder.send()

        with unittest.mock.patch('django.utils.timezone.now', return_value=one_minute):
            reminder.send()

        self.assertEqual(reminder.completed_on, one_minute)
        self.assertEqual(reminder.next_call, None)
