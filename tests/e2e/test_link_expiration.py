import datetime
import time

import httpx


def test_expired_link_not_accessible(test_client: httpx.Client):
    """Test that an expired link is not accessible"""

    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat()

    create_response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/quick-expire", "expires_at": expires_at}
    )

    assert create_response.status_code == 201
    link_data = create_response.json()
    short_code = link_data["short_code"]

    before_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert before_response.status_code == 307

    time.sleep(3)

    after_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert after_response.status_code == 404


def test_update_expiration_date(test_client: httpx.Client, create_test_link):
    """Test updating a link's expiration date"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat()

    update_response = test_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com", "expires_at": expires_at}
    )

    assert update_response.status_code == 200

    before_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert before_response.status_code == 307

    time.sleep(3)

    after_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert after_response.status_code == 404


def test_create_link_with_past_expiration(test_client: httpx.Client):
    """Test creating a link with an expiration date in the past"""

    expires_at = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()

    response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/past-expire", "expires_at": expires_at}
    )

    assert response.status_code == 422
