import pytest
import responses as responses_lib


@pytest.fixture
def responses():
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
