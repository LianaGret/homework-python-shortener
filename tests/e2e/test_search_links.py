import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_by_original_url(async_client: AsyncClient):
    """Test searching for links by original URL"""
    # Create multiple links with the same original URL
    original_url = "https://example.com/search-test"

    # Create first link
    await async_client.post("/api/v1/links/shorten", json={"original_url": original_url})

    # Create second link with custom alias
    await async_client.post("/api/v1/links/shorten", json={"original_url": original_url, "custom_alias": "searchme"})

    # Search for links
    search_response = await async_client.get("/api/v1/links/search", params={"original_url": original_url})

    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["original_url"] == original_url
    assert len(search_data["links"]) == 2

    # Verify one of the links has our custom alias
    custom_links = [link for link in search_data["links"] if link["short_code"] == "searchme"]
    assert len(custom_links) == 1


@pytest.mark.asyncio
async def test_search_nonexistent_url(async_client: AsyncClient):
    """Test searching for a URL that doesn't exist in the database"""
    search_response = await async_client.get(
        "/api/v1/links/search", params={"original_url": "https://example.com/nonexistent"}
    )

    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["original_url"] == "https://example.com/nonexistent"
    assert len(search_data["links"]) == 0


@pytest.mark.asyncio
async def test_search_with_invalid_url(async_client: AsyncClient):
    """Test searching with an invalid URL"""
    search_response = await async_client.get("/api/v1/links/search", params={"original_url": "not-a-valid-url"})

    assert search_response.status_code == 422  # Validation error
