from test_plus.test import TestCase

from .test_integration_app.models import TestIncomingWebhook
from .test_integration_app import handlers_registry


class TestModels(TestCase):

    def test_call_handler_from_webhook(self):
        integration = TestIncomingWebhook.objects.create(token='hello')

        payload = {
            'user': 'joe'
        }

        result = integration.handler.handle(payload)
        self.assertEqual(result['message'], 'hello joe')
