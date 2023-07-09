import hashlib
import hmac
import json
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from requests import Request

from django_webhook.models import Webhook


def prepare_request(webhook: Webhook, payload: dict):
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
    r = Request(method="POST", url=webhook.url, headers=headers, json=payload)
    return r.prepare()


def sign_payload(payload: dict, secret: str, timestamp: int):
    encoder_cls = settings.DJANGO_WEBHOOK["PAYLOAD_ENCODER_CLASS"]
    combined_payload = f"{timestamp}:{json.dumps(payload, cls=encoder_cls)}"
    return hmac.new(
        key=secret.encode(), msg=combined_payload.encode(), digestmod=hashlib.sha256
    ).hexdigest()


# TODO: Test that encoder is swappable
