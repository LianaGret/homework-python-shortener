import datetime
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_expired_link_not_accessible(async_client: AsyncClient):
    """Test that an expired link is not accessible"""
    # Create a link that expires in 2 seconds
    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat()

    create_response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/quick-expire", "expires_at": expires_at}
    )

    assert create_response.status_code == 201
    link_data = create_response.json()
    short_code = link_data["short_code"]

    # Verify the link works before expiration
    before_response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert before_response.status_code == 307

    # Wait for the link to expire
    time.sleep(3)

    # Verify the link is no longer accessible
    after_response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert after_response.status_code == 404


@pytest.mark.asyncio
async def test_update_expiration_date(async_client: AsyncClient, create_test_link):
    """Test updating a link's expiration date"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Set expiration to 2 seconds from now
    expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat()

    # Update the link
    update_response = await async_client.put(
        f"/api/v1/links/{short_code}", json={"original_url": "https://example.com", "expires_at": expires_at}
    )

    assert update_response.status_code == 200

    # Verify the link works before expiration
    before_response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert before_response.status_code == 307

    # Wait for the link to expire
    time.sleep(3)

    # Verify the link is no longer accessible
    after_response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert after_response.status_code == 404


@pytest.mark.asyncio
async def test_create_link_with_past_expiration(async_client: AsyncClient):
    """Test creating a link with an expiration date in the past"""
    # Set expiration to 1 hour ago
    expires_at = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()

    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/past-expire", "expires_at": expires_at}
    )

    # Should fail validation
    assert response.status_code == 422
