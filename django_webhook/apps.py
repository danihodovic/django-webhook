# pylint: disable=import-outside-toplevel
from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    name = "django_webhook"

    def ready(self):
        from django.conf import settings

        from .settings import defaults

        d = getattr(settings, "DJANGO_WEBHOOK", {})
        for k, v in defaults.items():
            if k not in d:
                d[k] = v

        settings.DJANGO_WEBHOOK = d

        # pylint: disable=unused-import
        import django_webhook.checks
        from django_webhook.models import populate_topics_from_settings
        from django_webhook.signals import connect_signals

        connect_signals()
        populate_topics_from_settings()
