from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string

defaults = dict(
    PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
    STORE_EVENTS=True,
    EVENTS_RETENTION_DAYS=30,
    USE_CACHE=True,
)


def get_settings():
    # pylint: disable=redefined-outer-name,import-outside-toplevel
    from django.conf import settings

    user_defined_settings = getattr(settings, "DJANGO_WEBHOOK", {})
    webhook_settings = {**defaults, **user_defined_settings}

    encoder_cls = webhook_settings["PAYLOAD_ENCODER_CLASS"]
    if isinstance(encoder_cls, str):
        webhook_settings["PAYLOAD_ENCODER_CLASS"] = import_string(encoder_cls)

    before_request = webhook_settings.get("BEFORE_REQUEST")
    if isinstance(before_request, str):
        webhook_settings["BEFORE_REQUEST"] = import_string(before_request)

    after_request = webhook_settings.get("AFTER_REQUEST")
    if isinstance(after_request, str):
        webhook_settings["AFTER_REQUEST"] = import_string(after_request)

    return webhook_settings
