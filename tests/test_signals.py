import hashlib
import hmac
import json
from datetime import datetime, timedelta

import pytest
from django.db.models.signals import post_save, post_delete
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time
from pytest_django.asserts import assertNumQueries

from django_webhook.test_factories import (
    WebhookFactory,
    WebhookSecretFactory,
    WebhookTopicFactory,
)
from django_webhook.signals import SignalListener

from tests.model_data import TEST_JOIN_DATE, TEST_LAST_ACTIVE, TEST_USER
from tests.models import Country, User


pytestmark = pytest.mark.django_db


@freeze_time("2012-01-14 03:21:34")
def test_create(responses):
    uuid = "54c10b6e-42e7-4edc-a047-a53c7ff80c77"
    webhook = WebhookFactory(
        topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[], uuid=uuid
    )
    secret = WebhookSecretFactory(webhook=webhook, token="very-secret-token")
    responses.post(webhook.url)

    User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    assert len(responses.calls) == 1
    req = responses.calls[0].request
    now = timezone.now()
    assert req.headers["Django-Webhook-Request-Timestamp"] == "1326511294"
    assert req.headers["Django-Webhook-UUID"] == str(webhook.uuid)
    assert json.loads(req.body) == {
        "topic": "tests.User/create",
        "object": TEST_USER,
        "object_type": "tests.User",
        "webhook_uuid": "54c10b6e-42e7-4edc-a047-a53c7ff80c77",
    }

    hmac_msg = f"{int(now.timestamp())}:{req.body.decode()}".encode()
    assert (
        req.headers["Django-Webhook-Signature-v1"]
        == hmac.new(
            key=secret.token.encode(), msg=hmac_msg, digestmod=hashlib.sha256
        ).hexdigest()
    )


def test_update(responses):
    user = User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    webhook = WebhookFactory(
        topics=[WebhookTopicFactory(name="tests.User/update")],
    )
    responses.post(webhook.url)

    user.name = "Adin"
    user.save()
    assert len(responses.calls) == 1
    req = responses.calls[0].request
    expected_object = TEST_USER.copy()
    expected_object["name"] = "Adin"
    assert json.loads(req.body) == {
        "topic": "tests.User/update",
        "object": expected_object,
        "object_type": "tests.User",
        "webhook_uuid": str(webhook.uuid),
    }


def test_delete(responses):
    user = User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    webhook = WebhookFactory(
        topics=[WebhookTopicFactory(name="tests.User/delete")],
    )
    responses.post(webhook.url)

    user.delete()
    assert len(responses.calls) == 1
    req = responses.calls[0].request
    assert json.loads(req.body) == {
        "topic": "tests.User/delete",
        "object": TEST_USER,
        "object_type": "tests.User",
        "webhook_uuid": str(webhook.uuid),
    }


def test_filters_topic_by_type(responses):
    webhook = WebhookFactory(
        topics=[WebhookTopicFactory(name="tests.User/update")],
    )
    responses.post(webhook.url)
    user = User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    assert len(responses.calls) == 0
    user.save()
    assert len(responses.calls) == 1


def test_multiple_topic_types(responses):
    user = User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    webhook = WebhookFactory(
        topics=[
            WebhookTopicFactory(name="tests.User/create"),
            WebhookTopicFactory(name="tests.User/update"),
            WebhookTopicFactory(name="tests.User/delete"),
        ],
    )
    responses.post(webhook.url)
    user.delete()
    assert len(responses.calls) == 1
    assert json.loads(responses.calls[0].request.body)["topic"] == "tests.User/delete"


def test_multiple_topic_models(responses):
    User.objects.create(
        name="Dani",
        email="dani@doo.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )
    country = Country.objects.create(name="Sweden")
    webhook = WebhookFactory(
        topics=[
            WebhookTopicFactory(name="tests.User/update"),
            WebhookTopicFactory(name="tests.Country/update"),
        ],
    )
    responses.post(webhook.url)
    country.save()

    assert json.loads(responses.calls[0].request.body) == {
        "topic": "tests.Country/update",
        "object": {"id": 1, "name": "Sweden"},
        "object_type": "tests.Country",
        "webhook_uuid": str(webhook.uuid),
    }


@pytest.mark.skip(reason="TODO")
def test_enriches_payload_with_api_url():
    pass


@pytest.mark.skip(reason="TODO")
def test_enriches_payload_with_app_url():
    pass


def test_does_not_fire_inactive_webhooks(responses):
    country = Country.objects.create(name="Sweden")
    webhook = WebhookFactory(
        active=False,
        topics=[
            WebhookTopicFactory(name="tests.Country/update"),
        ],
    )
    responses.post(webhook.url)
    country.save()
    assert len(responses.calls) == 0


@override_settings(
    DJANGO_WEBHOOK=dict(
        MODELS=["tests.Country"],
        USE_CACHE=True,
    )
)
def test_caches_webhook_query_calls(mocker):
    mocker.patch("django_webhook.signals.fire_webhook")
    country = Country.objects.create(name="Yugoslavia")
    WebhookFactory(
        topics=[
            WebhookTopicFactory(name="tests.Country/update"),
        ],
    )

    now = datetime.now()
    with freeze_time(now):
        # First save call caches the query for webhooks
        country.save()
        with assertNumQueries(1):  # pylint: disable=not-context-manager
            # The second save calls doesn't query webhooks again, but only updates the Country table
            country.save()

    # Move time forward and assert that the cache was busted
    with freeze_time(now + timedelta(minutes=1, seconds=1)):
        with assertNumQueries(2):  # pylint: disable=not-context-manager
            country.save()


def test_signal_listener_uid():
    assert (
        SignalListener(signal=post_save, signal_name="post_save", model_cls=Country).uid
        == "django_webhook_tests.Country_post_save"
    )
    assert (
        SignalListener(
            signal=post_delete, signal_name="post_delete", model_cls=Country
        ).uid
        == "django_webhook_tests.Country_post_delete"
    )
