from django import forms

from django_webhook.models import Webhook, WebhookTopic


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = [
            "url",
            "active",
            "topics",
        ]
