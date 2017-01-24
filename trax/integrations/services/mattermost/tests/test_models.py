from test_plus.test import TestCase

from trax.integrations.services.mattermost import models
from trax.integrations.services.mattermost import handlers_registry

class TestModels(TestCase):

    def test_can_create_incoming_webhook(self):

        integration = models.MattermostIncomingWebhook.objects.create(
            token='test'
        )

    def test_handler(self):
        integration = models.MattermostIncomingWebhook.objects.create(
            token='test'
        )

        self.assertTrue(integration.handler, handlers_registry.MattermostHandler)
