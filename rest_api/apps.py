from django.apps import AppConfig


class RestApiConfig(AppConfig):
    name = 'rest_api'

    def ready(self):
        import rest_api.tools.signals
