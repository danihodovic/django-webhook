from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    name = 'webhooks'

    def ready(self):
        try:
            # pylint: disable=unused-import
            import webhooks.signals
        except ImportError:
            pass
