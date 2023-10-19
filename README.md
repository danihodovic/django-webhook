# Django Webhooks ![badge](https://github.com/danihodovic/django-webhook/actions/workflows/ci.yml/badge.svg?event=push)

A plug-and-play Django app for sending outgoing webhooks on model changes.

Django has a built-in signal system which allows programmers to schedule functions to be executed on
model changes. django-webhook leverages the signal system together with Celery to send HTTP requests
when models change.

### 🔥 Feautures
- Automatically sends webhooks on model changes
- Leverages Celery for processing
- Webhook authentication using HMAC
- Retries with exponential backoff
- Admin integration
- Audit log with past webhook events
- Protection from replay attacks

### 📖 Documentation

https://django-webhook.readthedocs.io
