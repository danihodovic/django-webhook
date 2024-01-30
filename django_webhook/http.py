import hashlib
import hmac
import json
from datetime import datetime
from json import JSONEncoder
from typing import cast

from django.conf import settings
from django.utils import timezone
from requests import Request

from django_webhook.models import Webhook


def prepare_request(webhook: Webhook, payload: dict):
    now = timezone.now()
    timestamp = int(datetime.timestamp(now))

    encoder_cls = cast(
        type[JSONEncoder], settings.DJANGO_WEBHOOK["PAYLOAD_ENCODER_CLASS"]
    )
    signatures = [
        sign_payload(payload, secret, timestamp, encoder_cls)
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
        data=json.dumps(payload, cls=encoder_cls).encode(),
    )
    return r.prepare()


def sign_payload(
    payload: dict, secret: str, timestamp: int, encoder_cls: type[JSONEncoder]
):
    combined_payload = f"{timestamp}:{json.dumps(payload, cls=encoder_cls)}"
    return hmac.new(
        key=secret.encode(), msg=combined_payload.encode(), digestmod=hashlib.sha256
    ).hexdigest()


# TODO: Test that encoder is swappable
