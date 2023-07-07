import factory
from factory import SubFactory

from django_webhook.models import Webhook, WebhookSecret, WebhookTopic


class WebhookSecretFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WebhookSecret

    token = factory.Faker("isbn13")


class WebhookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Webhook

    url = factory.Faker("url", schemes=["https"])
    active = True
    secrets = factory.RelatedFactory(
        WebhookSecretFactory, factory_related_name="webhook"
    )

    @factory.post_generation
    def topics(self, create, extracted, **kwargs):
        self.refresh_from_db()
        if not create:
            return

        if extracted:
            for topic in extracted:
                self.topics.add(topic)  # pylint: disable=no-member


class WebhookTopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WebhookTopic
