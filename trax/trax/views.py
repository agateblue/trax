import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from . import forms
# from . import handlers


@csrf_exempt
@require_http_methods(["POST"])
def slash_command(request):
    if settings.SLASH_COMMAND_TOKEN != request.POST['token']:
        return JsonResponse({'text': 'Invalid token'}, status=403)

    form = forms.SlashCommandForm(request.POST)
    data = {
        'response_type': 'ephemeral'
    }
    if not form.is_valid():
        data['text'] = handlers.HelpHandler().response_text(request, action=None, arguments=None)
        return JsonResponse(data)

    cd = form.cleaned_data
    handler,  arguments = cd['handler'], cd['arguments']
    result = handler.handle(arguments, user=cd['user'])
    data['text'] = handler.get_response_content(
        request=request,
        action=cd['action'],
        arguments=arguments,
        context=result,)
    return JsonResponse(data)
