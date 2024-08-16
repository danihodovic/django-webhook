from django.core.exceptions import ValidationError

from .settings import get_settings


def validate_topic_model(value: str):
    webhook_settings = get_settings()
    allowed_models = webhook_settings.get("MODELS", [])
    if not webhook_settings or not allowed_models:
        raise ValidationError("settings.DJANGO_WEBHOOK.MODELS is empty")

    parts = value.split("/")
    if len(parts) != 2:
        raise ValidationError(f"Malformed topic: {value}")

    [model_name, _] = value.split("/")
    if model_name not in allowed_models:
        raise ValidationError(
            f"The topic: {value} is not in the whitelisted settings: {allowed_models}"
        )
