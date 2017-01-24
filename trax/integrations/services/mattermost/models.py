from trax.integrations.models import IncomingWebhook


class MattermostIncomingWebhook(IncomingWebhook):
    handler_name = 'mattermost'
