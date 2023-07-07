# pylint: disable=import-outside-toplevel,unused-argument
from django.conf import settings
from django.core.checks import Error, register


@register()
def warn_about_webhooks_settings(app_configs, **kwargs):
    webhook_settings = getattr(settings, "DJANGO_WEBHOOK")
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

    return errors
