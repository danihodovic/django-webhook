from django.core.serializers.json import DjangoJSONEncoder

defaults = dict(
    PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
    STORE_EVENTS=True,
    EVENTS_RETENTION_DAYS=30,
    USE_CACHE=True,
)
