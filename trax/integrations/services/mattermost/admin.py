from django.contrib import admin
from ...admin import IncomingWebhookAdmin
from . import models


@admin.register(models.MattermostIncomingWebhook)
class MattermostIncomingWebhookAdmin(IncomingWebhookAdmin):
    pass
