import pytz
from django.conf import settings
from dynamic_preferences.types import (
    ChoicePreference, Section, StringPreference)
from dynamic_preferences.registries import user_preferences_registry
from dynamic_preferences.registries import global_preferences_registry

glob = Section('global')
trax = Section('trax')


@global_preferences_registry.register
class SlashCommandToken(StringPreference):
    section = trax
    name = 'slash_command_token'
    description = "The token used to validate slash command payload"
    default = 'CHANGEME'


@user_preferences_registry.register
class TimeZone(ChoicePreference):
    section = glob
    name = 'timezone'
    description = "The timezone used for date handling"
    choices = [(t, t) for t in pytz.all_timezones]

    def get_default(self):
        return settings.TIME_ZONE
