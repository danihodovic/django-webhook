from datetime import timedelta

import pytest
from django.core.serializers.json import DjangoJSONEncoder
from django.test import override_settings
from django.utils import timezone

from django_webhook.models import WebhookEvent
from django_webhook.tasks import clear_webhook_events
from django_webhook.test_factories import (
    WebhookEventFactory,
    WebhookFactory,
    WebhookTopicFactory,
)
from tests.models import User

pytestmark = pytest.mark.django_db


@override_settings(
    DJANGO_WEBHOOK=dict(
        STORE_EVENTS=True,
        PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
        MODELS=["tests.User"],
        USE_CACHE=False,
    )
)
def test_creates_events_when_enabled(responses):
    webhook = WebhookFactory(
        active=True, topics=[WebhookTopicFactory(name="tests.User/create")]
    )
    responses.post(webhook.url)

    User.objects.create(name="Dani", email="dani@doo.com")
    assert WebhookEvent.objects.count() == 1
    event = WebhookEvent.objects.get()
    assert event.webhook == webhook
    assert event.object == {
        "topic": "tests.User/create",
        "object": {"id": 1, "name": "Dani", "email": "dani@doo.com"},
        "object_type": "tests.User",
        "webhook_uuid": str(webhook.uuid),
    }
    assert event.object_type == "tests.User"
    assert event.topic == "tests.User/create"
    assert event.status == "SUCCESS"
    assert event.url == webhook.url


@override_settings(
    DJANGO_WEBHOOK=dict(
        STORE_EVENTS=False,
        PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
        MODELS=["tests.User"],
        USE_CACHE=False,
    )
)
def test_does_not_create_events_when_disabled(responses):
    webhook = WebhookFactory(topics=[WebhookTopicFactory(name="tests.User/create")])
    responses.post(webhook.url)

    User.objects.create(name="Dani", email="dani@doo.com")
    assert WebhookEvent.objects.count() == 0


@override_settings(
    DJANGO_WEBHOOK=dict(
        STORE_EVENTS=False,
        PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
        MODELS=["tests.User"],
        USE_CACHE=False,
        # Retention of one day should clear out any older event
        EVENTS_RETENTION_DAYS=1,
    )
)
def test_clear_webhook_events():
    now = timezone.now()

    # Created now
    retained_event = WebhookEventFactory()
    # Created two days ago
    WebhookEventFactory(created=now - timedelta(days=5))

    clear_webhook_events.delay()
    assert WebhookEvent.objects.count() == 1
    assert WebhookEvent.objects.get() == retained_event
