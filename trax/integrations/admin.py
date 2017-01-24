from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin

from . import models
from .services.mattermost.models import MattermostIncomingWebhook


class IncomingWebhookAdmin(admin.ModelAdmin):
    readonly_fields = (
        'api_url',
    )
    list_display = (
        'api_url',
        'creation_date',
        'is_active'
    )
    list_filters = (
        'is_active',
    )
    search = (
        'token'
    )
