import persisting_theory
from django.http import JsonResponse


class Handler(object):
    def handle(self, data):
        raise NotImplementedError

    def prepare_data(self, raw_data, webhook):
        return raw_data

    def to_response(self, data):
        status = data.pop('_status_code')
        return JsonResponse(data, status=status)


class HandlersRegistry(persisting_theory.Registry):
    look_into = 'handlers_registry'

    def prepare_data(self, data):
        return data()

handlers_registry = HandlersRegistry()
