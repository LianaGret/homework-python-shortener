import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_link_url(async_client: AsyncClient, create_test_link):
    """Test updating a link's original URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Update the link
    update_response = await async_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com/updated"}
    )

    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["original_url"] == "https://example.com/updated"
    assert updated_data["short_code"] == short_code

    # Verify the redirect works with the new URL
    redirect_response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/updated"


@pytest.mark.asyncio
async def test_update_link_expiration(async_client: AsyncClient, create_test_link):
    """Test updating a link's expiration date"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Set expiration to 1 hour from now
    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

    # Update the link
    update_response = await async_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com", "expires_at": expires_at}
    )

    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["expires_at"] is not None


@pytest.mark.asyncio
async def test_update_nonexistent_link(async_client: AsyncClient):
    """Test updating a nonexistent link"""
    update_response = await async_client.put(
        "/api/v1/links/nonexistent", json={"original_url": "https://example.com/updated"}
    )

    assert update_response.status_code == 404  # Not found


@pytest.mark.asyncio
async def test_update_with_invalid_url(async_client: AsyncClient, create_test_link):
    """Test updating a link with an invalid URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    update_response = await async_client.put(f"/api/v1/links/{short_code}", json={"original_url": "not-a-valid-url"})

    assert update_response.status_code == 422  # Validation error
