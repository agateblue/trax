from trax.integrations.registries import handlers_registry, Handler


@handlers_registry.register(name='test')
class TestHandler(Handler):
    def handle(self, data):
        return {
            '_status_code': 200,
            'message': 'hello {0}'.format(data['user'])
        }
