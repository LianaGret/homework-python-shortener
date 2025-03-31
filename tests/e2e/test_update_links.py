import datetime

import httpx


def test_update_link_url(test_client: httpx.Client, create_test_link):
    """Test updating a link's original URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    update_response = test_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com/updated"}
    )

    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["original_url"] == "https://example.com/updated"
    assert updated_data["short_code"] == short_code

    redirect_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/updated"


def test_update_link_expiration(test_client: httpx.Client, create_test_link):
    """Test updating a link's expiration date"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

    update_response = test_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com", "expires_at": expires_at}
    )

    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["expires_at"] is not None


def test_update_nonexistent_link(test_client: httpx.Client):
    """Test updating a nonexistent link"""
    update_response = test_client.put("/api/v1/links/nonexistent", json={"original_url": "https://example.com/updated"})

    assert update_response.status_code == 404


def test_update_with_invalid_url(test_client: httpx.Client, create_test_link):
    """Test updating a link with an invalid URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    update_response = test_client.put(f"/api/v1/links/{short_code}", json={"original_url": "not-a-valid-url"})

    assert update_response.status_code == 422
