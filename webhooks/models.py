from django.db import models

from model_utils.models import TimeStampedModel


class Webhook(TimeStampedModel):
    url = URLField()
    topics = ArrayField(base_field=models.CharField(max_length=TOPIC_MAX_LENGTH))
    topics = models.ManyToManyField("webhooks.WebhookTopic")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Webhook: id={self.id} url={self.url} topics={self.topics} "


class WebhookTopic(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
