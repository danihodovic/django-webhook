from django.core.management.base import BaseCommand

from django_webhook.models import Webhook, WebhookSecret, WebhookTopic


class Command(BaseCommand):
    help = "Sets up sample webhooks for testing"

    def handle(self, *args, **options):
        # NodeJS
        wh, _ = Webhook.objects.update_or_create(
            url="http://nodejs_receiver:8001/webhook"
        )
        wh.topics.set(
            [
                WebhookTopic.objects.get(name="tests.Country/create"),
                WebhookTopic.objects.get(name="tests.Country/update"),
            ]
        )
        WebhookSecret.objects.update_or_create(webhook=wh, token="very-secret-token")

        # Flask
        wh, _ = Webhook.objects.update_or_create(
            url="http://flask_receiver:8002/webhook"
        )
        wh.topics.set(
            [
                WebhookTopic.objects.get(name="tests.Country/create"),
                WebhookTopic.objects.get(name="tests.Country/update"),
            ]
        )
        WebhookSecret.objects.update_or_create(webhook=wh, token="very-secret-token")
