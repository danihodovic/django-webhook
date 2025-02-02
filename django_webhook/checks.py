# pylint: disable=import-outside-toplevel,unused-argument
from django.core.checks import Error, register

from .settings import get_settings
import inspect


@register()
def warn_about_webhooks_settings(app_configs, **kwargs):
    webhook_settings = get_settings()
    errors = []
    if not webhook_settings:
        errors.append(
            Error(
                "settings.DJANGO_WEBHOOK must be a dict",
                id="django_webhook.E01",
            )
        )

    if webhook_settings:
        base_msg = "settings.DJANGO_WEBHOOK.MODELS is misconfigured"
        models = webhook_settings.get("MODELS")
        if not isinstance(models, list):
            errors.append(
                Error(
                    base_msg,
                    hint="MODELS must be a list of models such as MODELS=['users.User']",
                    id="django_webhook.E02",
                )
            )
        else:
            from django.apps import apps

            for model_name in models:
                app_label, model_label = model_name.split(".")
                try:
                    apps.get_model(app_label, model_label)
                except LookupError:
                    errors.append(
                        Error(
                            base_msg,
                            hint=f"'{model_name}' in DJANGO_WEBHOOK.MODELS doesn't exist in your Django app",
                            id="django_webhook.E03",
                        )
                    )
        before_request = webhook_settings.get("BEFORE_REQUEST")
        if before_request:
            before_request_signature = inspect.signature(before_request)
            params = before_request_signature.parameters
            if set(params.keys()).difference(["webhook", "payload"]) != set():
                errors.append(
                    Error(
                        "If set, settings.DJANGO_WEBHOOK.BEFORE_REQUEST must be a function that accepts two arguments.",
                        hint=f"Function '{before_request_signature.__name__}' takes arguments {params}",
                        id="django_webhook.E04",
                    )
                )
        after_request = webhook_settings.get("AFTER_REQUEST")
        if after_request:
            after_request_signature = inspect.signature(after_request)
            params = after_request_signature.parameters
            if (
                set(params.keys()).difference(["webhook", "payload", "response"])
                != set()
            ):
                errors.append(
                    Error(
                        "If set, settings.DJANGO_WEBHOOK.AFTER_REQUEST must be a function that accepts three arguments.",
                        hint=f"Function '{after_request.__name__}' takes arguments {params}",
                        id="django_webhook.E04",
                    )
                )

    return errors
