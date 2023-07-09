import logging

from celery import current_app as app
from requests import Session

s = Session()
from django.forms.models import model_to_dict
from requests.exceptions import RequestException

from django_webhook.models import Webhook

from .http import prepare_request


@app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=60 * 60,
    retry_jitter=False,
)
def fire(self, webhook_id, payload):
    webhook = Webhook.objects.get(id=webhook_id)
    if not webhook.active:
        logging.warning(f"Webhook: {webhook} is inactive and I will not fire it.")
        return

    req = prepare_request(webhook, payload)
    try:
        Session().send(req).raise_for_status()
    except RequestException as ex:
        status_code = ex.response.status_code
        logging.warning(f"Webhook request failed {status_code=}")
        raise self.retry(exc=ex)
