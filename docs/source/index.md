# Welcome to django-webhook!

A plug-and-play Django app for sending outgoing webhooks on model changes.

Django has a built-in signal system which allows programmers to schedule functions to be executed on
model changes. django-webhook leverages the signal system together with Celery to send HTTP requests
when models change.

```{toctree}
install
```
