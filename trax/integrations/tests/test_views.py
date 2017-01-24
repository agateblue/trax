import json
from test_plus.test import TestCase

from .test_integration_app.models import TestIncomingWebhook
from .test_integration_app import handlers_registry


class TestModels(TestCase):

    def test_call_handler_from_webhook(self):
        integration = TestIncomingWebhook.objects.create(token='hello')
        url = self.reverse(
            'api:integrations:incoming_webhook', token='hello')

        payload = {
            'user': 'joe'
        }

        response = self.client.post(url, payload)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(result['message'], 'hello joe')
