import uuid
from django.db import models
from django.core.urlresolvers import reverse
from polymorphic.models import PolymorphicModel

from . import registries


class IncomingWebhook(PolymorphicModel):

    is_active = models.BooleanField(default=True)
    token = models.CharField(
        max_length=100, db_index=True, unique=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    @property
    def handler(self):
        return registries.handlers_registry[self.handler_name]

    def save(self, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(**kwargs)

    def generate_token(self):
        return uuid.uuid4().hex

    @property
    def api_url(self):
        return reverse('api:integrations:incoming_webhook', kwargs={
            'token': self.token
        }) if self.token else None
