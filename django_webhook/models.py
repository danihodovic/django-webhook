import logging
import uuid

from celery import states
from django.conf import settings
from django.core import validators
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields import DateTimeField

from .validators import validate_topic_model

topic_regex = r"\w+\.\w+\/[create|update|delete]"

STATES = [
    (states.PENDING, states.PENDING),
    (states.FAILURE, states.FAILURE),
    (states.SUCCESS, states.SUCCESS),
]


class Webhook(models.Model):
    url = models.URLField()
    topics = models.ManyToManyField(
        "django_webhook.WebhookTopic",
        related_name="webhooks",
        related_query_name="webhook",
    )
    active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __str__(self):
        return f"id={self.id} active={self.active}"


class WebhookTopic(models.Model):  # type: ignore
    name = models.CharField(
        max_length=250,
        unique=True,
        validators=[
            validators.RegexValidator(
                topic_regex, message="Topic must match: " + topic_regex
            ),
            validate_topic_model,
        ],
    )

    def __str__(self):
        return self.name


class WebhookSecret(models.Model):
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name="secrets",
        related_query_name="secret",
        editable=False,
    )
    token = models.CharField(
        max_length=100,
        validators=[validators.MinLengthValidator(12)],
    )
    created = DateTimeField(auto_now_add=True)


class WebhookEvent(models.Model):
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="events",
        related_query_name="event",
    )
    object = models.JSONField(
        max_length=1000,
        encoder=DjangoJSONEncoder,
        editable=False,
    )
    object_type = models.CharField(max_length=50, null=True, editable=False)
    status = models.CharField(
        max_length=40,
        default=states.PENDING,
        choices=STATES,
        editable=False,
    )
    created = DateTimeField(auto_now_add=True)
    url = models.URLField(editable=False)
    topic = models.CharField(max_length=250, null=True, editable=False)


def populate_topics_from_settings():
    # pylint: disable=import-outside-toplevel
    from django.db.utils import OperationalError, ProgrammingError

    from django_webhook.signals import CREATE, DELETE, UPDATE

    try:
        Webhook.objects.count()
    except (OperationalError, ProgrammingError) as ex:
        if "Connection refused" in ex.args[0]:
            return
        if "could not translate host name" in ex.args[0]:
            return
        if "no such table" in ex.args[0]:
            return
        if "relation" in ex.args[0] and "does not exist" in ex.args[0]:
            return
        raise ex

    webhook_settings = getattr(settings, "DJANGO_WEBHOOK", {})
    enabled_models = webhook_settings.get("MODELS")
    if not enabled_models:
        return

    allowed_topics = set()
    for model in enabled_models:
        model_allowed_topics = {
            f"{model}/{CREATE}",
            f"{model}/{UPDATE}",
            f"{model}/{DELETE}",
        }
        allowed_topics.update(model_allowed_topics)

    WebhookTopic.objects.exclude(name__in=allowed_topics).delete()
    logging.info(f"Purging WebhookTopics: {allowed_topics}")

    for topic in allowed_topics:
        if not WebhookTopic.objects.filter(name=topic).exists():
            WebhookTopic.objects.create(name=topic)
            logging.info(f"Adding topic: {topic}")
