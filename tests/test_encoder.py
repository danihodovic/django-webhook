import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import FieldFile

from django_webhook.models import WebhookEvent

from .models import ModelWithFileField

pytestmark = pytest.mark.django_db


class MyCustomEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, FieldFile):
            return "A file!"
        return super().default(o)


def test_custom_encoder(
    settings,
    responses,
    webhook_factory,
    webhook_topic_factory,
):
    settings.DJANGO_WEBHOOK["PAYLOAD_ENCODER_CLASS"] = (
        "tests.test_encoder.MyCustomEncoder"
    )
    webhook = webhook_factory(
        topics=[webhook_topic_factory(name="tests.ModelWithFileField/create")],
        secrets=[],
    )
    responses.post(webhook.url)

    # Action!
    test_file = SimpleUploadedFile(
        "test_file.txt", b"These are the file contents.", content_type="text/plain"
    )
    ModelWithFileField.objects.create(file=test_file)

    req = responses.calls[0].request
    json_body = json.loads(req.body)
    assert json_body["object"]["file"] == "A file!"

    event = WebhookEvent.objects.get()
    assert isinstance(event.object, dict)
    assert event.object["object"]["file"] == "A file!"
