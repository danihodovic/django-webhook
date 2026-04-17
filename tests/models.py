from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    join_date = models.DateField()
    last_active = models.DateTimeField()


class Country(models.Model):
    name = models.CharField(max_length=30)


class ModelWithFileField(models.Model):
    """
        The FileField can't be encoded with JSON.
    https://github.com/danihodovic/django-webhook/issues/35
    """

    file = models.FileField()


class ModelWithCustomTopic(models.Model):
    name = models.CharField(max_length=30)

    def webhook_topics(self, action: str) -> list[str]:
        return [
            f"test.ModelWithCustomTopic/{action}/{self.name}",
        ]