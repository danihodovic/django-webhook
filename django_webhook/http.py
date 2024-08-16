import hashlib
import hmac
from datetime import datetime

from django.utils import timezone
from requests import Request

from django_webhook.models import Webhook


def prepare_request(webhook: Webhook, payload: str):
    now = timezone.now()
    timestamp = int(datetime.timestamp(now))

    signatures = [
        sign_payload(payload, secret, timestamp)
        for secret in webhook.secrets.values_list("token", flat=True)
    ]
    headers = {
        "Content-Type": "application/json",
        "Django-Webhook-Request-Timestamp": str(timestamp),
        "Django-Webhook-Signature-v1": ",".join(signatures),
        "Django-Webhook-UUID": str(webhook.uuid),
    }
    r = Request(
        method="POST",
        url=webhook.url,
        headers=headers,
        data=payload.encode(),
    )
    return r.prepare()


def sign_payload(payload: str, secret: str, timestamp: int):
    combined_payload = f"{timestamp}:{payload}"
    return hmac.new(
        key=secret.encode(), msg=combined_payload.encode(), digestmod=hashlib.sha256
    ).hexdigest()
