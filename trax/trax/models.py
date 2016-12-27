import datetime

from django.db import models
from django.utils import timezone
from django.forms import ValidationError
from django.utils.text import slugify

from trax.users.models import User


class TimerGroupQuerySet(models.QuerySet):
    def running(self):
        return self.filter(timers__end_date__isnull=True)

    def since(self, date):
        return self.filter(timers__start_date__gte=date)


class TimerGroupManager(models.Manager):

    def start(self, name, user, **kwargs):
        slug = slugify(name)
        # first, we check if a timer for this group is already started
        qs = user.timer_groups.filter(slug=slug).running()
        existing = qs.first()
        if existing:
            return existing

        # we stop any previously running group for the same user
        groups = user.timer_groups.all().running()
        for group in groups:
            group.stop()

        # then we get_or_create a new group based on the given name
        group, created = self.get_or_create(
            user=user, slug=slugify(name),
            defaults={'name': name},
        )

        # and finally, we start the whole thing
        group.start()
        return group


class TimerGroup(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=150)
    creation_date = models.DateTimeField(default=lambda: timezone.now())
    description = models.TextField()
    user = models.ForeignKey(User, related_name='timer_groups')

    objects = TimerGroupManager.from_queryset(TimerGroupQuerySet)()

    class Meta:
        unique_together = ('slug', 'user')
        ordering = ('-creation_date',)

    @property
    def today_duration(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.timers.all().since(today).duration()

    @property
    def current_timer(self):
        return self.timers.running().order_by('-start_date').first()

    @property
    def is_started(self):
        return TimerGroup.objects.filter(pk=self.pk).running().exists()

    def start(self):
        return Timer.objects.create(
            group=self,
        )

    def stop(self):
        for timer in self.timers.all().running():
            timer.stop()


class TimerQuerySet(models.QuerySet):
    def running(self):
        return self.filter(end_date__isnull=True)

    def since(self, date):
        return self.filter(start_date__gte=date)

    def duration(self):
        duration = 0
        for timer in self.all():
            duration += timer.duration

        return datetime.timedelta(seconds=duration)


class Timer(models.Model):
    start_date = models.DateTimeField(default=lambda: timezone.now())
    end_date = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey(TimerGroup, related_name='timers')

    objects = TimerQuerySet.as_manager()

    class Meta:
        ordering = ('-start_date',)

    @property
    def duration(self):
        end = self.end_date or timezone.now()
        return (end - self.start_date).seconds

    @property
    def is_started(self):
        return self.end_date is None

    def stop(self):
        self.end_date = timezone.now()
        self.save()
