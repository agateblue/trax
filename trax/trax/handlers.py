import datetime
import dateparser
import pytz

from django.template import loader, Context
from django.conf import settings
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import Q

from . import models
from . import exceptions


class Handler(object):
    response_type = 'ephemeral'

    def valid_for_action(self, action):
        return action == self.entrypoint or action in self.keywords.split(' ')

    def handle(self, arguments, user):
        return {}

    def get_response_content(self, request, action, arguments, context):
        t = loader.get_template('trax/handlers/{0}.md'.format(self.entrypoint))
        context['request'] = request
        context['action'] = action
        context['arguments'] = arguments

        context = self.get_additional_context(context)
        return t.render(Context(context)).strip()

    def get_exception_response_content(
            self,
            exception,
            request,
            action,
            user,
            arguments):
        """
        Called when an exception in triggered in handle
        """

        t = loader.select_template([
            'trax/handlers/{0}_error_{1}.md'.format(
                self.entrypoint, exception.err_code),
            'trax/handlers/{0}_error.md'.format(self.entrypoint),
            'trax/handlers/error_{0}.md'.format(exception.err_code),
            'trax/handlers/error.md',
        ])
        context = {}
        context['request'] = request
        context['action'] = action
        context['user'] = user
        context['arguments'] = arguments
        context['exception'] = exception

        context = self.get_additional_context(context)
        return t.render(Context(context)).strip()

    def get_additional_context(self, context):
        return context

    def get_example(self):
        return '/<trigger> {0}'.format(self.entrypoint)


class HelpHandler(Handler):
    entrypoint = 'help'
    keywords = '?'
    description = 'Display the list of commands'

    def get_additional_context(self, context):
        context = super().get_additional_context(context)
        context['handlers'] = handlers
        return context


class StartTimerHandler(Handler):
    entrypoint = 'start'
    keywords = 's begin'
    description = 'Start a timer'

    def handle(self, arguments, user):
        if not arguments:
            # missing time name
            raise exceptions.HandleError('Please provide a valid name', err_code='missing_arg')

        try:
            # we try to fetch the timer group using a shortcut instead of name
            shortcut = int(arguments)
            existing = user.timer_groups.order_by_usage().with_position()
            for t in existing:
                if shortcut != t.queryset_position:
                    continue
                t.start()
                return {
                    'timer_group': t,
                }
            raise exceptions.HandleError('The shortcut you provided does not match any timer', err_code='invalid_arg')
        except ValueError:
            pass

        return {
            'timer_group': models.TimerGroup.objects.start(
                arguments, user=user
            )
        }

    def get_example(self):
        example = super().get_example()
        example += ' my great timer'
        return example


class StopTimersHandler(Handler):
    entrypoint = 'stop'
    keywords = 'kill'
    description = 'Stop any running timers'

    def handle(self, arguments, user):
        groups = user.timer_groups.all().running()
        for group in groups:
            group.stop()
        return {
            'timer_groups': groups,
        }


class ListTimersHandler(Handler):
    entrypoint = 'list'
    keywords = 'ls l'
    description = 'Display today\'s timers'

    def handle(self, arguments, user):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = user.timer_groups.since(today)
        return {
            'timer_groups': qs,
        }


class RestartTimersHandler(Handler):
    entrypoint = 'restart'
    keywords = 're res'
    description = 'Restart the previously stopped timer'

    def handle(self, arguments, user):
        timer = (
            models.Timer.objects.filter(group__user=user)
                                .order_by('-start_date').first()
        )
        if not timer:
            return {
                'timer_group': None
            }

        timer.group.start()
        return {
            'timer_group': timer.group
        }


class StatsHandler(Handler):
    entrypoint = 'stats'
    keywords = 'report reports stat rep'
    description = 'Display your personal time tracking statistics'
    response_type = 'in_channel'

    def get_example(self):
        example = super().get_example()
        example += ' two weeks ago'
        return example

    def handle(self, arguments, user):
        end = (
            dateparser.parse(arguments) or
            timezone.now().replace(
                hour=23, minute=59, second=59, microsecond=9999))
        r = 7
        tz = pytz.timezone(settings.TIME_ZONE)
        end = end.replace(tzinfo=tz)
        start = (end - datetime.timedelta(days=r)).replace(hour=0, minute=0, second=0, microsecond=0)
        intervals = [
            (start + datetime.timedelta(days=i), start + datetime.timedelta(days=i + 1))
            for i in range(1, r + 1)
        ]
        data = {
            'headers': [i[0] for i in intervals],
            'rows': [],
            'start_date': start.date(),
            'end_date': end.date(),
            'interval_totals': [],
        }
        available_groups = user.timer_groups.since(start, end).order_by('name')
        for group in available_groups:
            row_data = {
                'label': group.name,
                'values': [],
                'total': None,
            }
            for s, e in intervals:
                row_data['values'].append(group.get_duration(s, e))

            row_data['total'] = datetime.timedelta(seconds=sum([v.seconds for v in row_data['values']]))
            data['rows'].append(row_data)

        for i1, v in enumerate(data['headers']):
            seconds = 0
            for i2, group in enumerate(available_groups):
                seconds += data['rows'][i2]['values'][i1].seconds

            data['interval_totals'].append(datetime.timedelta(seconds=seconds))

        data['total'] = datetime.timedelta(seconds=sum([v.seconds for v in data['interval_totals']]))

        return data


handlers = [
    HelpHandler(),
    StartTimerHandler(),
    StopTimersHandler(),
    ListTimersHandler(),
    RestartTimersHandler(),
    StatsHandler(),
]

handlers_by_key = {
    h.entrypoint: h for h in handlers
}
