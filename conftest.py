import pytest
import responses as responses_lib
from pytest_factoryboy import register

from django_webhook.test_factories import (
    WebhookEventFactory,
    WebhookFactory,
    WebhookSecretFactory,
    WebhookTopicFactory,
)

register(WebhookFactory)
register(WebhookEventFactory)
register(WebhookTopicFactory)
register(WebhookSecretFactory)


@pytest.fixture
def responses():
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
