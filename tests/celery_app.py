from celery import Celery

app = Celery("tests")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
