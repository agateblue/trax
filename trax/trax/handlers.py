import datetime
import dateparser
import pytz
import docopt
import shlex
import croniter
import cron_descriptor

from django.template import loader, Context, TemplateDoesNotExist
from django.conf import settings
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import Q
from django.utils import safestring
from dynamic_preferences.exceptions import NotFoundInRegistry
from dynamic_preferences.serializers import SerializationError as DPSerializationError
from dynamic_preferences.registries import user_preferences_registry

from . import models
from . import exceptions
from . import utils


class Handler(object):
    response_type = 'ephemeral'

    def valid_for_action(self, action):
        return action == self.entrypoint or action in self.keywords.split(' ')

    def handle(self, arguments, user, **kwargs):
        return {}

    def get_help_content(self, user):
        try:
            t = loader.get_template('trax/handlers/{0}_help.md'.format(self.entrypoint))
        except TemplateDoesNotExist:
            return self.description

        context = {}
        context['user'] = user
        context['handler'] = self
        return safestring.mark_safe(t.render(Context(context)).strip())

    def get_response_content(
            self, request, action, arguments, context, user=None):
        t = self.get_template(request, action, arguments, context, user=user)
        context['request'] = request
        context['user'] = user
        context['action'] = action
        context['arguments'] = arguments

        context = self.get_additional_context(context)
        return safestring.mark_safe(t.render(Context(context)).strip())

    def get_template(self, request, action, arguments, context, user=None):
        return loader.get_template('trax/handlers/{0}.md'.format(self.entrypoint))

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
                self.entrypoint, exception.code),
            'trax/handlers/{0}_error.md'.format(self.entrypoint),
            'trax/handlers/error_{0}.md'.format(exception.code),
            'trax/handlers/error.md',
        ])
        context = {}
        context['request'] = request
        context['action'] = action
        context['user'] = user
        context['arguments'] = arguments
        context['exception'] = exception

        context = self.get_additional_context(context)
        return safestring.mark_safe(t.render(Context(context)).strip())

    def get_additional_context(self, context):
        return context

    def get_example(self):
        return '/<trigger> {0}'.format(self.entrypoint)


class SubcommandHandler(Handler):

    def handle(self, arguments, user, **kwargs):
        parsed = shlex.split(arguments)
        try:
            args = docopt.docopt(self.usage, parsed)
        except docopt.DocoptExit as e:
            raise exceptions.HandleError(safestring.mark_safe(str(e)), code='invalid_arg')

        subcommand = arguments.split(' ')[0]
        f = getattr(self, 'handle_{0}'.format(subcommand))
        r = f(args, user, **kwargs)
        r['parsed_arguments'] = args
        r['subcommand'] = subcommand
        return r

    def get_template(self, request, action, arguments, context, user=None):
        return loader.get_template(
            'trax/handlers/{0}_{1}.md'.format(
                self.entrypoint, context['subcommand']))


class HelpHandler(Handler):
    entrypoint = 'help'
    keywords = '? h'
    description = 'Display the list of commands'

    def get_additional_context(self, context):
        context = super().get_additional_context(context)
        context['handlers'] = handlers
        return context

    def handle(self, arguments, user, **kwargs):
        if not arguments:
            # root help
            return {}

        try:
            handler = [h for h in handlers if h.valid_for_action(arguments)][0]
        except IndexError:
            raise exceptions.HandleError(
                '`{0}` does not match any command'.format(arguments),
                code='invalid_arg',
            )

        help_content = handler.get_help_content(user)
        return {
            'help_content': help_content,
        }


class StartTimerHandler(Handler):
    entrypoint = 'start'
    keywords = 's begin'
    description = 'Start a timer'

    def handle(self, arguments, user, **kwargs):
        if not arguments:
            # missing time name
            raise exceptions.HandleError('Please provide a valid name', code='missing_arg')

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
            raise exceptions.HandleError('The shortcut you provided does not match any timer', code='invalid_arg')
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

    def handle(self, arguments, user, **kwargs):
        groups = user.timer_groups.all().running()

        end = (
            dateparser.parse(arguments) or
            timezone.now())
        tz = pytz.timezone(user.preferences['global__timezone'])
        try:
            end = tz.localize(end)
        except ValueError:
            # already localized
            pass

        for group in groups:
            group.stop(end)

        return {
            'timer_groups': groups,
            'end_date': end,
        }


class ListTimersHandler(Handler):
    entrypoint = 'list'
    keywords = 'ls l'
    description = 'Display today\'s timers'

    def handle(self, arguments, user, **kwargs):
        end = (
            dateparser.parse(arguments) or
            timezone.now())
        tz = pytz.timezone(user.preferences['global__timezone'])
        try:
            end = tz.localize(end)
        except ValueError:
            # already localized
            pass
        end = end.replace(hour=23, minute=59, second=59, microsecond=9999)
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        qs = user.timer_groups.since(start, end)

        return {
            'timer_groups': qs,
            'date': start.date(),
        }


class RestartTimersHandler(Handler):
    entrypoint = 'restart'
    keywords = 're res'
    description = 'Restart the last stopped timer'

    def handle(self, arguments, user, **kwargs):
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


class TimeHandler(Handler):
    entrypoint = 'time'
    keywords = 'hour date datetime'
    description = 'Simply display the current date/time'

    def handle(self, arguments, user, **kwargs):
        tz = user.preferences['global__timezone']
        if arguments:
            if arguments not in pytz.all_timezones:
                raise HandleError('Invalid timezone', code='invalid_arg')
            tz = arguments

        return {
            'current': timezone.now(),
            'timezone': tz,
        }


class CrontabHandler(Handler):
    entrypoint = 'cron'
    keywords = 'crontab cr'
    description = 'A simple machine to human crontab translator. See [crontab.guru](https://crontab.guru) for online helper.'

    def handle(self, arguments, user, **kwargs):
        if not arguments:
            raise exceptions.HandleError(
                'You need to provide a crontab expression such as `1 * 2 * *`',
                code='missing_arg')
            tz = arguments

        try:
            description = cron_descriptor.get_description(arguments)
        except cron_descriptor.FormatException as e:
            raise exceptions.HandleError(
                '{0} is not a valid crontab expression: {1}'.format(
                    arguments, str(e)),
                code='invalid_arg')
        return {
            'description': description,
            'crontab': arguments
        }


class ConfigHandler(Handler):
    entrypoint = 'config'
    keywords = 'conf c settings options'
    description = 'Access and update your settings'

    def handle(self, arguments, user, **kwargs):
        s = arguments.split(' ')
        setting = s[0]
        new_value = None
        if len(s) > 1:
            # a new value is provided
            new_value = ' '.join(s[1:])
        if not setting:
            settings = user.preferences
            available_settings = [
                (conf, settings['global__{0}'.format(conf.name)])
                for conf in user_preferences_registry['global'].values()
            ]
            return {
                'setting': None,
                'available_settings': available_settings,
            }

        pref = 'global__{0}'.format(setting)

        try:
            value = user.preferences[pref]
        except NotFoundInRegistry:
            raise exceptions.HandleError('{0} is not a valid setting'.format(setting), code='invalid_arg')

        if new_value:
            pref_obj = user_preferences_registry.get(pref)

            try:
                cleaned = pref_obj.field.clean(new_value)
                user.preferences[pref] = cleaned
            except DPSerializationError:
                raise exceptions.HandleError(
                    '{0} is not a valid value for setting {1}'.format(new_value, setting),
                    code='invalid_arg')

        return {
            'setting': setting,
            'old_value': value,
            'new_value': new_value,
            'updated': new_value is not None,
        }


class RemindHandler(SubcommandHandler):
    entrypoint = 'remind'
    keywords = ''
    description = 'Manage reminders'
    usage = """
        Reminder

        Usage:
            remind add <message> <when>
            remind delete <reminder_id>...
            remind list

        Examples:
            remind add "something important" "tomorrow at noon"

        Add arguments:
            <message>     The message that will be sent when the reminder is triggered
            <when>        When to set the reminder. It can either be:

                            * A relative hint, such as "in two hours" or "tomorrow at noon"
                            * An absolute date/time, such as "2017-01-10 17:15"
                            * A crontab, such as "0 12 * * *", in this case, the reminder will be recurring

        Note that it you provide multiple words for these arguments,
        you have to enclose them using double quotes:

            * GOOD: remind add something tomorrow
            * GOOD: remind add "something important" tomorrow
            * GOOD: remind add "something important" "tomorrow at noon"
            * BAD: remind add something tomorrow at noon
            * BAD: remind add something important "tomorrow at noon"
    """

    def handle_add(self, args, user, **kwargs):
        crontab = None
        crontab_error = None
        try:
            croniter.croniter(args['<when>'])
            crontab = args['<when>']
        except (croniter.CroniterBadCronError, croniter.CroniterBadDateError) as e:
            crontab_error = str(e)

        if not crontab:
            tz = pytz.timezone(user.preferences['global__timezone'])
            when = utils.parse_future(args['<when>'], tz=tz)
        else:
            when = None

        if not when and not crontab:
            raise exceptions.HandleError(
                'Invalid date/crontab for <when>\n'
                'Crontab error: {0}'.format(crontab_error), code='invalid_arg')

        reminder = user.reminders.create(
            message=args['<message>'],
            next_call=when,
            crontab=crontab,
            channel_id=kwargs['channel_id'],
            channel_name=kwargs['channel_name'],
        )
        return {
            'reminder': reminder
        }

    def handle_delete(self, args, user, **kwargs):
        raw_pks = args['<reminder_id>']
        pks = []

        for t in raw_pks:
            try:
                pks.append(int(t))
            except ValueError:
                raise exceptions.HandleError(
                    '{0} is not a valid reminder id'.format(t),
                    code='invalid_arg')

        reminders = user.reminders.filter(pk__in=pks)
        count = reminders.count()
        reminders.delete()
        return {
            'deleted': reminders,
            'count': count,
        }

    def handle_list(self, args, user, **kwargs):
        return {
            'reminders': user.reminders.all().order_by('creation_date')
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

    def handle(self, arguments, user, **kwargs):
        end = (
            dateparser.parse(arguments) or
            timezone.now())
        r = 7
        tz = pytz.timezone(user.preferences['global__timezone'])
        try:
            end = tz.localize(end)
        except ValueError:
            # already localized
            pass
        end = end.replace(hour=23, minute=59, second=59, microsecond=9999)
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
    ConfigHandler(),
    CrontabHandler(),
    TimeHandler(),
    RemindHandler(),
]

handlers_by_key = {
    h.entrypoint: h for h in handlers
}
