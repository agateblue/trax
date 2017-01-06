import datetime
import requests

from django.db import models, transaction
from django.utils import timezone
from django.forms import ValidationError
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from dynamic_preferences.registries import global_preferences_registry

from trax.users.models import User


def get_now():
    return timezone.now()


class TimerGroupQuerySet(models.QuerySet):
    def running(self):
        return self.filter(timers__end_date__isnull=True)

    def since(self, start_date, end_date=None):
        qs = self.filter(timers__start_date__gte=start_date)
        if end_date:
            q = models.Q(timers__end_date__lt=end_date) | models.Q(timers__end_date__isnull=True)
            qs = qs.filter(q).filter(timers__start_date__lt=end_date)
        return qs.distinct()

    def order_by_usage(self):
        return self.annotate(c=models.Count('timers')).order_by('-c')

    def with_position(self):
        qs = list(self.all())
        for i, e in enumerate(qs):
            setattr(e, 'queryset_position', i + 1)
        return qs

    def stop(self):
        qs = list(self.all().running())
        for group in qs:
            group.stop()

        return qs


class TimerGroupManager(models.Manager):

    def start(self, name, user, **kwargs):
        slug = slugify(name)
        # first, we check if a timer for this group is already started
        qs = user.timer_groups.filter(slug=slug).running()
        existing = qs.first()
        if existing:
            return existing

        # we stop any previously running group for the same user
        user.timer_groups.stop()

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
    creation_date = models.DateTimeField(default=get_now)
    description = models.TextField()
    user = models.ForeignKey(User, related_name='timer_groups')

    objects = TimerGroupManager.from_queryset(TimerGroupQuerySet)()

    def __str__(self):
        return '{0} / {1}'.format(self.user, self.name)

    class Meta:
        unique_together = ('slug', 'user')
        ordering = ('-creation_date',)

    @property
    def today_duration(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_duration(today)

    def get_duration(self, start, end=None):
        return self.timers.all().since(start, end).duration()

    @property
    def current_timer(self):
        return self.timers.running().order_by('-start_date').first()

    @property
    def is_started(self):
        return TimerGroup.objects.filter(pk=self.pk).running().exists()

    def start(self):
        self.user.timer_groups.stop()
        return self.timers.create(
            group=self,
        )

    def stop(self, end=None):
        for timer in self.timers.all().running():
            timer.stop(end=end)


class TimerQuerySet(models.QuerySet):
    def running(self):
        return self.filter(end_date__isnull=True)

    def since(self, start_date, end_date=None):
        qs = self.filter(start_date__gte=start_date)
        if end_date:
            q = models.Q(end_date__lt=end_date) | models.Q(end_date__isnull=True)
            qs = qs.filter(q).filter(start_date__lt=end_date)
        return qs.distinct()

    def duration(self):
        duration = 0
        for timer in self.all():
            duration += timer.duration

        return datetime.timedelta(seconds=duration)


class Timer(models.Model):
    start_date = models.DateTimeField(default=get_now)
    end_date = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey(TimerGroup, related_name='timers')

    objects = TimerQuerySet.as_manager()

    class Meta:
        ordering = ('-start_date',)

    def __str__(self):
        return '{0}: {1} -> {2}'.format(
            self.group.name, self.start_date, self.end_date
        )

    @property
    def duration(self):
        end = self.end_date or timezone.now()
        return (end - self.start_date).seconds

    def save(self, **kwargs):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date must be greater than start date')

        # we try to find any overlapping timer
        qs = Timer.objects.filter(group__user=self.group.user)
        query = models.Q(start_date__lte=self.start_date, end_date__gte=self.start_date)

        if self.end_date:
            query |= models.Q(start_date__lte=self.end_date, end_date__gte=self.end_date)

        duplicates = qs.running() | qs.filter(query)
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)

        if duplicates.exists():
            raise ValidationError('Timer is overlapping another timer from the same group')
        return super().save(**kwargs)

    @property
    def is_started(self):
        return self.end_date is None

    def stop(self, end=None):
        self.end_date = end or timezone.now()
        self.save()


class Reminder(models.Model):
    creation_date = models.DateTimeField(default=get_now)
    next_call = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    crontab = models.CharField(null=True, blank=True, max_length=100)
    user = models.ForeignKey(User, related_name='reminders')
    message = models.TextField()
    channel_id = models.CharField(max_length=100, null=True, blank=True)
    channel_name = models.CharField(max_length=100, null=True, blank=True)

    @transaction.atomic
    def send(self, strict=True):
        if strict and timezone.now() < self.next_call:
            raise ValueError('This reminder cannot be send, it\'s too early')

        request = self.prepare_request()
        session = requests.Session()
        response = session.send(request)
        response.raise_for_status()

        self.completed_on = timezone.now()
        self.next_call = None
        self.save()

        return response

    def prepare_request(self):
        preferences = global_preferences_registry.manager()
        url = preferences['trax__webhook_url']
        data = {
            'text': self.message,
            'channel': self.channel_id,
        }
        return requests.Request(
            'POST',
            url=url,
            data=data
        ).prepare()
