from django.template import loader, Context
from django.conf import settings
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import Q

from . import models
from . import exceptions


class Handler(object):
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
        return t.render(Context(context)).rstrip()

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
            raise exceptions.HandleError('Please provide a valid name')
        return {
            'timer_group': models.TimerGroup.objects.start(
                arguments, user=user
            )
        }

    def get_example(self):
        example = super().get_example()
        example += 'my great timer'
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


handlers = [
    HelpHandler(),
    StartTimerHandler(),
    StopTimersHandler(),
    ListTimersHandler(),
]

handlers_by_key = {
    h.entrypoint: h for h in handlers
}
