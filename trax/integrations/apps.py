from django.apps import AppConfig, apps
from .registries import handlers_registry


class IntegrationsConfig(AppConfig):
    name = 'trax.integrations'
    verbose_name = "Integrations"

    def ready(self):
        app_names = [app.name for app in apps.app_configs.values()]
        handlers_registry.autodiscover(app_names)
