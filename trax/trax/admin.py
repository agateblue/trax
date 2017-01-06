from django.contrib import admin

from . import models


@admin.register(models.Timer)
class TimerAdmin(admin.ModelAdmin):
    list_display = [
        'group',
        'start_date',
        'end_date',
        'duration',
    ]
    list_filter = [
        'group__user',
        'group__slug',
    ]
    search_fields = [
        'group__user__username',
        'group__name',
        'group__slug',
    ]


@admin.register(models.TimerGroup)
class TimerGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'user',
        'creation_date',
        'is_started',
    ]
    list_filter = [
        'user',
        'slug',
    ]
    search_fields = [
        'user__username',
        'name',
        'slug',
    ]
