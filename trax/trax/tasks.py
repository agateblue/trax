from django.utils import timezone

from . import models


def kill_obsolete_timers():
    now = timezone.now()
    today = now.date()

    candidates = models.Timer.objects.running()
    candidates = candidates.filter(start_date__date__lt=today)

    for candidate in candidates:
        candidate.stop()

    print('Closed %s timers' % len(candidates))
