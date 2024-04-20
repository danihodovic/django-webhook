# Django Webhooks ![badge](https://github.com/danihodovic/django-webhook/actions/workflows/ci.yml/badge.svg?event=push)

A plug-and-play Django app for sending outgoing webhooks on model changes.

Django has a built-in signal system which allows programmers to schedule functions to be executed on
model changes. django-webhook leverages the signal system together with Celery to send HTTP requests
when models change.

Suppose we have a User model
```python
class User(models.Model):
    name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
```

If a webhook is configured, any time the above model is created, updated or deleted django-webhook
will send an outgoing HTTP request to a third party:

```
POST HTTP/1.1
host: webhook.site
user-agent: python-urllib3/2.0.3
django-webhook-uuid: 5e2ee3ba-905e-4360-94bf-18ef21c0e844
django-webhook-signature-v1:
django-webhook-request-timestamp: 1697818014

{
  "topic": "users.User/create",
  "object": {
    "id": 3,
    "name": "Dani Doo",
    "age": 30
  },
  "object_type": "users.User",
  "webhook_uuid": "5e2ee3ba-905e-4360-94bf-18ef21c0e844"
}
```

### 🔥 Features
- Automatically sends webhooks on model changes
- Leverages Celery for processing
- Webhook authentication using HMAC
- Retries with exponential backoff
- Admin integration
- Audit log with past webhook events
- Protection from replay attacks
- Allows rotating webhook secrets

### 📖 Documentation

https://django-webhook.readthedocs.io
