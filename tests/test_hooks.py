import pytest
import json
from freezegun import freeze_time
from unittest.mock import patch, MagicMock

from django_webhook.tasks import fire_webhook
from django_webhook.test_factories import (
    WebhookFactory,
    WebhookSecretFactory,
    WebhookTopicFactory,
)
from django.test import override_settings

pytestmark = pytest.mark.django_db


def before_request():
    pass


def after_request():
    pass


@freeze_time("2012-01-14 03:21:34")
def test_before_request_string(responses):
    with patch("tests.test_hooks.before_request") as hook_mock:
        with override_settings(
            DJANGO_WEBHOOK=dict(
                BEFORE_REQUEST="tests.test_hooks.before_request",
            )
        ):
            webhook = WebhookFactory(
                topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
            )
            responses.post(webhook.url)
            WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
            WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
            payload = dict(hello="world")
            fire_webhook.apply((webhook.id, json.dumps(payload)))
            hook_mock.assert_called_once()


@freeze_time("2012-01-14 03:21:34")
def test_after_request_success_string(responses):
    with (
        patch("tests.test_hooks.after_request") as hook_mock,
        override_settings(
            DJANGO_WEBHOOK=dict(
                AFTER_REQUEST="tests.test_hooks.after_request",
            )
        ),
    ):
        webhook = WebhookFactory(
            topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
        )
        responses.post(webhook.url)
        WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
        WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
        payload = dict(hello="world")
        fire_webhook.apply((webhook.id, json.dumps(payload)))
        hook_mock.assert_called_once()


@freeze_time("2012-01-14 03:21:34")
def test_after_request_error_string(responses):
    with (
        patch("django_webhook.tasks.Session.send") as response_mock,
        patch("tests.test_hooks.after_request") as hook_mock,
        override_settings(
            DJANGO_WEBHOOK=dict(
                AFTER_REQUEST="tests.test_hooks.after_request",
            )
        ),
    ):
        response_mock.status_code = 400
        webhook = WebhookFactory(
            topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
        )
        responses.post(webhook.url)
        WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
        WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
        payload = dict(hello="world")
        fire_webhook.apply((webhook.id, json.dumps(payload)))
        hook_mock.assert_called_once()


@freeze_time("2012-01-14 03:21:34")
def test_before_request_function(responses):
    hook_mock = MagicMock()
    with override_settings(
        DJANGO_WEBHOOK=dict(
            BEFORE_REQUEST=hook_mock,
        )
    ):
        webhook = WebhookFactory(
            topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
        )
        responses.post(webhook.url)
        WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
        WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
        payload = dict(hello="world")
        fire_webhook.apply((webhook.id, json.dumps(payload)))
        hook_mock.assert_called_once()


@freeze_time("2012-01-14 03:21:34")
def test_after_request_success_function(responses):
    hook_mock = MagicMock()
    with override_settings(
        DJANGO_WEBHOOK=dict(
            AFTER_REQUEST=hook_mock,
        )
    ):
        webhook = WebhookFactory(
            topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
        )
        responses.post(webhook.url)
        WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
        WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
        payload = dict(hello="world")
        fire_webhook.apply((webhook.id, json.dumps(payload)))
        hook_mock.assert_called_once()


@freeze_time("2012-01-14 03:21:34")
def test_after_request_error_function(responses):
    hook_mock = MagicMock()
    with (
        patch("django_webhook.tasks.Session.send") as response_mock,
        override_settings(
            DJANGO_WEBHOOK=dict(
                AFTER_REQUEST=hook_mock,
            )
        ),
    ):
        response_mock.status_code = 400
        webhook = WebhookFactory(
            topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
        )
        responses.post(webhook.url)
        WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
        WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
        payload = dict(hello="world")
        fire_webhook.apply((webhook.id, json.dumps(payload)))
        hook_mock.assert_called_once()
