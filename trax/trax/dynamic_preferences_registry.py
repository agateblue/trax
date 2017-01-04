import pytz
from django.conf import settings
from dynamic_preferences.types import ChoicePreference, Section
from dynamic_preferences.registries import user_preferences_registry

glob = Section('global')


@user_preferences_registry.register
class TimeZone(ChoicePreference):
    section = glob
    name = 'timezone'
    description = "The timezone used for date handling"
    choices = [(t, t) for t in pytz.all_timezones]

    def get_default(self):
        return settings.TIME_ZONE
