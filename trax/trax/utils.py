import dateparser
from django.utils import timezone


def humanize_timedelta(delta):
    days, rem = divmod(delta.seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    if seconds < 1:seconds = 1
    magnitudes = ["days", "hours", "minutes"]
    if seconds / delta.seconds > 0.05:
        magnitudes.append('seconds')
    locals_ = locals()
    magnitudes_str = ("{n} {magnitude}".format(n=int(locals_[magnitude]), magnitude=magnitude)
                      for magnitude in magnitudes if locals_[magnitude])
    return ", ".join(magnitudes_str)


def parse_future(s, tz):
    now = timezone.now()
    result = dateparser.parse(s)
    if result:
        result = tz.localize(result)
    if (not result or result < now) and not s.startswith('in'):
        # we try to prepend "in" in front of the string to see if it changes
        # anything
        s2 = "in " + s
        result = dateparser.parse(s2)
    return result
