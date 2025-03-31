import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_very_long_url(async_client: AsyncClient):
    """Test creating a link with a very long URL"""
    # Create a URL with 2000 characters
    long_url = f"https://example.com/{'a' * 1980}"

    response = await async_client.post("/api/v1/links/shorten", json={"original_url": long_url})

    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == long_url


@pytest.mark.asyncio
async def test_unicode_in_custom_alias(async_client: AsyncClient):
    """Test creating a link with Unicode characters in the custom alias"""
    # This should fail validation as we only allow alphanumeric characters
    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/unicode", "custom_alias": "unicode😊test"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_maximum_length_custom_alias(async_client: AsyncClient):
    """Test creating a link with a custom alias of maximum allowed length"""
    # Assuming maximum length is 16 characters
    max_length_alias = "a" * 16

    response = await async_client.post(
        "/api/v1/links/shorten",
        json={"original_url": "https://example.com/max-length", "custom_alias": max_length_alias},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == max_length_alias


@pytest.mark.asyncio
async def test_create_many_links_same_url(async_client: AsyncClient):
    """Test creating many links for the same URL"""
    original_url = "https://example.com/many-links"

    # Create 5 links for the same URL
    links = []
    for _ in range(5):
        response = await async_client.post("/api/v1/links/shorten", json={"original_url": original_url})

        assert response.status_code == 201
        links.append(response.json())

    # Verify all links have unique short codes
    short_codes = [link["short_code"] for link in links]
    assert len(short_codes) == len(set(short_codes))  # All short codes should be unique

    # Search for the links
    search_response = await async_client.get("/api/v1/links/search", params={"original_url": original_url})

    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data["links"]) >= 5  # Should find at least our 5 links


@pytest.mark.asyncio
async def test_malformed_short_code(async_client: AsyncClient):
    """Test accessing a link with a malformed short code"""
    # Try with special characters that might cause issues
    response = await async_client.get("/api/v1/links/!@#$%^&*()", follow_redirects=False)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_empty_short_code(async_client: AsyncClient):
    """Test accessing a link with an empty short code"""
    response = await async_client.get("/api/v1/links/", follow_redirects=False)
    assert response.status_code in [404, 405]  # Either not found or method not allowed
