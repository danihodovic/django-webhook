from django.contrib import admin
from django.contrib.admin import TabularInline

from django_webhook.models import Webhook, WebhookEvent, WebhookSecret

from .forms import WebhookForm


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


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("url", "status", "created", "topic")
    list_filter = ("webhook", "status", "topic")
    search_fields = ("webhook", "status", "topic")
    readonly_fields = (
        "webhook",
        "url",
        "status",
        "created",
        "topic",
        "object_type",
        "object",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
