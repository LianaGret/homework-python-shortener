import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_basic_link(async_client: AsyncClient):
    """Test creating a basic link without custom alias or expiration"""
    response = await async_client.post("/api/v1/links/shorten", json={"original_url": "https://example.com"})

    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com"
    assert data["custom_alias"] is False
    assert "created_at" in data
    assert data["expires_at"] is None


@pytest.mark.asyncio
async def test_create_link_with_custom_alias(async_client: AsyncClient):
    """Test creating a link with a custom alias"""
    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/custom", "custom_alias": "mylink"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "mylink"
    assert data["original_url"] == "https://example.com/custom"
    assert data["custom_alias"] is True


@pytest.mark.asyncio
async def test_create_link_with_expiration(async_client: AsyncClient):
    """Test creating a link with an expiration date"""
    # Create a link that expires in 1 hour
    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/expiring", "expires_at": expires_at}
    )

    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/expiring"
    assert data["expires_at"] is not None


@pytest.mark.asyncio
async def test_create_link_with_invalid_url(async_client: AsyncClient):
    """Test creating a link with an invalid URL"""
    response = await async_client.post("/api/v1/links/shorten", json={"original_url": "not-a-valid-url"})

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_link_with_duplicate_alias(async_client: AsyncClient):
    """Test creating a link with a duplicate custom alias"""
    # First create a link with a custom alias
    first_response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/first", "custom_alias": "duplicate"}
    )

    assert first_response.status_code == 201

    # Try to create another link with the same alias
    second_response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/second", "custom_alias": "duplicate"}
    )

    assert second_response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_create_link_with_invalid_alias(async_client: AsyncClient):
    """Test creating a link with an invalid custom alias"""
    response = await async_client.post(
        "/api/v1/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": "a",  # Too short
        },
    )

    assert response.status_code == 422  # Validation error

    response = await async_client.post(
        "/api/v1/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": "invalid@alias",  # Contains non-alphanumeric characters
        },
    )

    assert response.status_code == 422  # Validation error
