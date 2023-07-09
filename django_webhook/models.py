import uuid

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from model_utils.fields import AutoCreatedField
from model_utils.models import TimeStampedModel

from .validators import validate_topic_model

topic_regex = r"\w+\.\w+\/[create|update|delete]"


# Use auto update fields instead of model_utils
class Webhook(TimeStampedModel):
    url = models.URLField()
    topics = models.ManyToManyField(
        "django_webhook.WebhookTopic",
        related_name="webhooks",
        related_query_name="webhook",
    )
    active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        topics = list(self.topics.values_list("name", flat=True))
        return f"Webhook: id={self.id} url={self.url} {topics=} active={self.active}"


class WebhookTopic(models.Model):
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
    created = AutoCreatedField()


def populate_topics_from_settings():
    # pylint: disable=import-outside-toplevel
    from django_webhook.signals import CREATE, UPDATE, DELETE
    from django.db.utils import OperationalError, IntegrityError

    try:
        Webhook.objects.count()
    except OperationalError as ex:
        if "no such table" in ex.args[0]:
            return
        raise ex

    webhook_settings = getattr(settings, "DJANGO_WEBHOOK", {})
    models = webhook_settings.get("MODELS")
    if not models:
        return

    for model in settings.DJANGO_WEBHOOK["MODELS"]:
        allowed_topics = [
            f"{model}/{CREATE}",
            f"{model}/{UPDATE}",
            f"{model}/{DELETE}",
        ]
        for topic in allowed_topics:
            try:
                WebhookTopic.objects.create(name=topic)
            except IntegrityError as ex:
                if "UNIQUE constraint failed" in ex.args[0]:
                    continue
                raise ex
