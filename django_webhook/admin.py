from django.contrib import admin
from .forms import WebhookForm
from django.contrib.admin import TabularInline
from django_webhook.models import Webhook, WebhookSecret, WebhookTopic


class WebhookSecretInline(TabularInline):
    model = WebhookSecret
    fields = ("token",)
    extra = 0


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    form = WebhookForm
    list_display = (
        "url",
        "active",
        "uuid",
    )
    list_filter = ("active", "topics")
    search_fields = ("url",)
    filter_horizontal = ("topics",)
    inlines = [WebhookSecretInline]
