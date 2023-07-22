from django.core.serializers.json import DjangoJSONEncoder

defaults = dict(
    PAYLOAD_ENCODER_CLASS=DjangoJSONEncoder,
    STORE_EVENTS=True,
    USE_CACHE=True,
    EVENTS_RETENTION_DAYS=30,
)
