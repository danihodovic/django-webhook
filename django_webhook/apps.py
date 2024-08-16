# pylint: disable=import-outside-toplevel

from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    name = "django_webhook"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        # pylint: disable=unused-import
        import django_webhook.checks
        from django_webhook.models import populate_topics_from_settings
        from django_webhook.signals import connect_signals

        connect_signals()
        populate_topics_from_settings()
