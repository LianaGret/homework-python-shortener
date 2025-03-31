import random
import string

import httpx
import pytest


@pytest.fixture(scope="session")
def test_client() -> httpx.Client:
    with httpx.Client(base_url="http://localhost:8000") as client:
        yield client


def generate_random_string(length=8):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


@pytest.fixture
def create_test_link(test_client: httpx.Client):
    response = test_client.post("/api/v1/links/shorten", json={"original_url": "https://example.com"})
    return response.json()


@pytest.fixture
async def create_custom_link(test_client: httpx.Client):
    custom_alias = generate_random_string(8)
    response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/custom", "custom_alias": custom_alias}
    )
    return response.json()


@pytest.fixture
async def create_expiring_link(test_client: httpx.Client):
    import datetime

    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

    response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/expiring", "expires_at": expires_at}
    )
    return response.json()
