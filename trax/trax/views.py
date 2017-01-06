import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction

from . import forms
from . import exceptions
from . import handlers
from django.utils import timezone

# from . import handlers


@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def slash_command(request):
    if settings.SLASH_COMMAND_TOKEN != request.POST['token']:
        return JsonResponse({'text': 'Invalid token'}, status=403)

    form = forms.SlashCommandForm(request.POST)
    data = {
        'response_type': 'ephemeral'
    }
    if not form.is_valid():
        data['text'] = handlers.HelpHandler().get_response_content(
            request=request,
            action='help',
            arguments='',
            context={})
        return JsonResponse(data)

    cd = form.cleaned_data
    handler,  arguments = cd['handler'], cd['arguments']

    with timezone.override(cd['user'].preferences['global__timezone']):
        try:
            result = handler.handle(arguments, user=cd['user'])
        except (exceptions.HandleError, exceptions.ValidationError) as e:
            data['text'] = handler.get_exception_response_content(
                exception=e,
                user=cd['user'],
                request=request,
                action=cd['action'],
                arguments=arguments
            )
            return JsonResponse(data)
        data = {
            'response_type': handler.response_type
        }
        data['text'] = handler.get_response_content(
            request=request,
            user=cd['user'],
            action=cd['action'],
            arguments=arguments,
            context=result,)

        if data['response_type'] == 'in_channel':
            data['text'] = '*{0} invoked command "{1} {2}"*\n\n'.format(
                cd['user'].username, cd['command'], cd['text']
            ) + data['text']
        return JsonResponse(data)
