from django.db.models.base import Model as Model
from django.db.models.signals import ModelSignal
from django_webhook.signals import SignalListener, connect_signals
from django_webhook.settings import defaults
from django.db.models.signals import post_save, post_delete
from tests.models import Country
from django.test import override_settings
import pytest

from django_webhook.test_factories import WebhookFactory, WebhookTopicFactory
import json

from unittest.mock import patch


class DummySignalListener:
    pass


def test_invalid_signal_listener():
    with override_settings(
        DJANGO_WEBHOOK=defaults
        | {"SIGNAL_LISTENER": "tests.test_override.UnknownSignalListener"}
    ):
        with pytest.raises(ImportError):
            connect_signals()

    with override_settings(
        DJANGO_WEBHOOK=defaults
        | {"SIGNAL_LISTENER": "tests.test_override.DummySignalListener"}
    ):
        with pytest.raises(ValueError):
            connect_signals()


class CustomSignalListener(SignalListener):
    def run(self, sender, created=False, instance=None, **kwargs):
        if isinstance(instance, Country) and instance.name in [
            "France",
            "Spain",
            "Italy",
            "Germany",
        ]:
            return super().run(sender, created, instance, **kwargs)

    def model_dict(self, model):
        return {"id": model.id, "country_name": model.name}


def _disconnect_signals():
    assert post_save.disconnect(
        sender=Country,
        dispatch_uid="django_webhook_tests.Country_post_save",
    )
    assert post_delete.disconnect(
        sender=Country,
        dispatch_uid="django_webhook_tests.Country_post_delete",
    )


@pytest.mark.django_db
def test_override_signal_listener(responses):
    country = Country.objects.create(name="France")
    webhook = WebhookFactory(
        topics=[
            WebhookTopicFactory(name="tests.Country/update")
        ]
    )
    responses.post(webhook.url)

    _disconnect_signals()

    with override_settings(
        DJANGO_WEBHOOK={
            "SIGNAL_LISTENER": "tests.test_override.CustomSignalListener",
            "MODELS": ["tests.Country"],
        }
        | defaults
    ):
        connect_signals()

    country.save()

    assert len(responses.calls) == 1
    assert json.loads(responses.calls[0].request.body) == {
        "topic": "tests.Country/update",
        "object": {"id": country.id, "country_name": "France"},
        "object_type": "tests.Country",
        "webhook_uuid": str(webhook.uuid),
    }
