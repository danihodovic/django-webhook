# Configuring Celery

[Celery](https://github.com/celery/celery) is an open-source asynchronous task queue. It's a popular
choice for processing tasks in the background in Django projects.

Django-Webhook uses Celery to offload the work of sending HTTP requests to a separate worker
process. This ensures that we don't bog down the web workers and that we can retry failing webhooks.

**Running a Celery worker is a requirement for running Django-Webhook. Without a Celery worker no
webhooks will be sent.**

By default Django-Webhook places tasks on the default Celery queue, called "celery". To consume
tasks run a worker:

```bash
celery -A config.settings.celery:app worker -Q celery
```

## Using a dedicated worker

If you want to process Django-Webhook tasks separately from your other tasks you need to use [task
routing](https://docs.celeryq.dev/en/stable/userguide/routing.html#routing-tasks), a separate queue and start a separate worker. This could be to:

- process webhook tasks faster by running multiple workers for the webhooks queue
- avoid clogging up the default tasks queue with webhook tasks
- rate limit how many webhooks to send per minute

In your Celery configuration file configure the `task_routes` property:

```python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("myapp")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure task routes
app.conf.task_routes = [
    [
        ("django_webhook.tasks.fire_webhook", {"queue": "webhooks"}),
    ],
]
```
With this route enabled webhook tasks will be routed to the "webhooks" queue, while all other tasks
will be routed to the default queue (named "celery"). You now have to run a worker that consumes
from the webhooks queue:

```bash
celery -A config.settings.celery:app worker -Q webhooks
```

The worker could also consume from multiple queues:

```bash
celery -A config.settings.celery:app worker -Q celery,webhooks,email
```
