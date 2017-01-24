# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^webhook/(?P<token>[\w-]{1,40})$',
        view=views.incoming_webhook,
        name='incoming_webhook'
    ),
]
