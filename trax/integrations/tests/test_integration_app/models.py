from trax.integrations.models import IncomingWebhook


class TestIncomingWebhook(IncomingWebhook):
    handler_name = 'test'
