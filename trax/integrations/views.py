from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.http import Http404
from . import models


@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def incoming_webhook(request, token):
    try:
        webhook = models.IncomingWebhook.objects.get(
            is_active=True, token=token)
    except models.IncomingWebhook.DoesNotExist:
        raise Http404

    data = webhook.handler.prepare_data(request.POST, webhook)
    result = webhook.handler.handle(data)
    return webhook.handler.to_response(result)
