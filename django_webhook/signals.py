# pylint: disable=redefined-builtin
import json
from datetime import timedelta
import logging

from django.apps import apps
from django.db import models
from django.db.models.signals import ModelSignal, post_delete, post_save
from django.forms import model_to_dict

from django_webhook.models import Webhook, WebhookTopic

from .settings import get_settings
from .tasks import fire_webhook
from .util import cache

logger = logging.getLogger(__name__)

CREATE = "create"
UPDATE = "update"
DELETE = "delete"


class SignalListener:
    def __init__(
        self, signal: ModelSignal, signal_name: str, model_cls: type[models.Model]
    ):
        valid_signals = ["post_save", "post_delete"]
        if signal_name not in valid_signals:
            raise ValueError(f"{signal} must be one of {valid_signals}")

        self.signal = signal
        self.signal_name = signal_name
        self.model_cls = model_cls

    # pylint: disable=unused-argument
    def run(self, sender, created: bool = False, instance=None, **kwargs):
        action_type = None
        match self.signal_name:
            case "post_save" if created:
                action_type = CREATE
            case "post_save":
                action_type = UPDATE
            case "post_delete":
                action_type = DELETE

        topic_names = {f"{self.model_label}/{action_type}"}
        if hasattr(instance, "webhook_topics") and callable(getattr(instance, "webhook_topics")):
            instance_webhook_topics = instance.webhook_topics(action_type)
            for topic in instance_webhook_topics:
                WebhookTopic.objects.get_or_create(name=topic)
                
            topic_names = topic_names.union(set(instance_webhook_topics))
        webhook_ids = _find_webhooks(frozenset(topic_names))
        logger.info(f"Found {len(webhook_ids)} webhooks for topics: {topic_names}")
        encoder_cls = get_settings()["PAYLOAD_ENCODER_CLASS"]

        for id, uuid, topic_name in webhook_ids:
            payload_dict = dict(
                object=model_dict(instance),
                topic=topic_name,
                object_type=self.model_label,
                webhook_uuid=str(uuid),
            )
            payload = json.dumps(payload_dict, cls=encoder_cls)
            fire_webhook.delay(
                id,
                payload,
                topic=topic_name,
                object_type=self.model_label,
            )

    def connect(self):
        self.signal.connect(
            self.run, sender=self.model_cls, weak=False, dispatch_uid=self.uid  # type: ignore
        )

    @property
    def uid(self):
        return f"django_webhook_{self.model_label}_{self.signal_name}"

    @property
    def model_label(self):
        return self.model_cls._meta.label


def connect_signals():
    for cls in _active_models():
        post_save_listener = SignalListener(
            signal=post_save, signal_name="post_save", model_cls=cls
        )
        post_delete_listener = SignalListener(
            signal=post_delete, signal_name="post_delete", model_cls=cls
        )
        post_save_listener.connect()
        post_delete_listener.connect()


def model_dict(model):
    """
    Returns the model instance as a dict, nested values for related models.
    """
    fields = {
        field.name: field.value_from_object(model) for field in model._meta.fields
    }
    return model_to_dict(model, fields=fields)  # type: ignore


def _active_models():
    model_names = get_settings().get("MODELS", [])
    model_classes = []
    for name in model_names:
        parts = name.split(".")
        if len(parts) != 2:
            continue
        app_label, model_label = parts
        try:
            model_class = apps.get_model(app_label, model_label)
        except LookupError:
            continue
        model_classes.append(model_class)
    return model_classes


def _find_webhooks(topic_names: list[str]):
    """
    In tests and for smaller setups we don't want to cache the query.
    """
    if get_settings()["USE_CACHE"]:
        return _query_webhooks_cached(topic_names)
    return _query_webhooks(topic_names)


@cache(ttl=timedelta(minutes=1))
def _query_webhooks_cached(topic_names: list[str]):
    """
    Cache the calls to the database so we're not polling the db anytime a signal is triggered.
    """
    return _query_webhooks(topic_names)


def _query_webhooks(topic_names: list[str]):
    return Webhook.objects.filter(active=True, topics__name__in=topic_names).values_list(
        "id", "uuid", "topics__name"
    )
