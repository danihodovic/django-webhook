from django import forms

from django_webhook.models import Webhook


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = [
            "url",
            "active",
            "topics",
        ]
