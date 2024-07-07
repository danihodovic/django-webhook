import logging
from datetime import timedelta

from celery import current_app as app
from celery import states
from django.conf import settings
from django.utils import timezone
from requests import Session
from requests.exceptions import RequestException

from django_webhook.models import Webhook, WebhookEvent

from .http import prepare_request


@app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=60 * 60,
    retry_jitter=False,
)
def fire_webhook(self, webhook_id: int, payload: dict):
    webhook = Webhook.objects.get(id=webhook_id)
    if not webhook.active:
        logging.warning(f"Webhook: {webhook} is inactive and I will not fire it.")
        return

    req = prepare_request(webhook, payload)
    store_events = settings.DJANGO_WEBHOOK["STORE_EVENTS"]

    if store_events:
        event = WebhookEvent.objects.create(
            webhook=webhook,
            object=payload,
            object_type=payload.get("object_type"),
            status=states.PENDING,
            url=webhook.url,
            topic=payload.get("topic"),
        )
    try:
        Session().send(req).raise_for_status()
        if store_events:
            WebhookEvent.objects.filter(id=event.id).update(status=states.SUCCESS)
    except RequestException as ex:
        status_code = ex.response.status_code  # type: ignore
        logging.warning(f"Webhook request failed {status_code=}")
        if store_events:
            WebhookEvent.objects.filter(id=event.id).update(status=states.FAILURE)
        raise self.retry(exc=ex)


@app.task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=60 * 60,
    retry_jitter=False,
)
def clear_webhook_events():
    """
    Clears out old webhook events
    """
    days_ago = settings.DJANGO_WEBHOOK["EVENTS_RETENTION_DAYS"]
    now = timezone.now()
    cutoff_date = now - timedelta(days=days_ago)  # type: ignore
    qs = WebhookEvent.objects.filter(created__lt=cutoff_date)
    logging.info(
        f"Clearing webhook events older than {cutoff_date=}. Found {qs.count()} matching events"
    )
    qs.delete()
